"""
Rate Limiting and API Error Handling for Hatena Blog API.
API制限対応とレート制限機能を提供します。
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional
from dataclasses import dataclass, field
from collections import deque

import httpx

from .models import ErrorInfo, ErrorType


logger = logging.getLogger(__name__)


@dataclass
class RateLimitState:
    """レート制限の状態を管理するデータクラス"""
    
    # リクエスト履歴（タイムスタンプのデック）
    requests: deque = field(default_factory=deque)
    
    # 最大リクエスト数（分間）
    max_requests_per_minute: int = 30
    
    # 時間窓（秒）
    time_window: int = 60
    
    # 最後にリセットされた時刻
    last_reset: float = field(default_factory=time.time)
    
    # 一時的な制限（API制限応答後）
    temporary_limit_until: Optional[float] = None
    
    # バックオフ乗数
    backoff_multiplier: float = 1.0


class RateLimiter:
    """APIレート制限とエラーハンドリングを管理するクラス"""
    
    def __init__(
        self,
        max_requests_per_minute: int = 30,
        max_concurrent_requests: int = 5,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0
    ):
        """
        レート制限器を初期化します。

        Args:
            max_requests_per_minute: 分間最大リクエスト数
            max_concurrent_requests: 同時実行最大リクエスト数
            base_delay: 基本遅延時間（秒）
            max_delay: 最大遅延時間（秒）
            backoff_factor: バックオフ係数
        """
        self.state = RateLimitState(max_requests_per_minute=max_requests_per_minute)
        self.max_concurrent = max_concurrent_requests
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        
        # 並行制御用セマフォ
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        # 制御用ロック
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """
        レート制限を適用してリクエスト実行権を取得します。

        必要に応じて待機時間を挿入し、同時実行数を制限します。
        """
        async with self._semaphore:
            async with self._lock:
                await self._wait_for_rate_limit()
                self._record_request()

    def _record_request(self) -> None:
        """リクエストの実行を記録します"""
        now = time.time()
        self.state.requests.append(now)
        
        # 古いリクエスト履歴を削除
        cutoff = now - self.state.time_window
        while self.state.requests and self.state.requests[0] < cutoff:
            self.state.requests.popleft()

    async def _wait_for_rate_limit(self) -> None:
        """レート制限に基づいて必要な待機を行います"""
        now = time.time()
        
        # 一時的な制限が有効かチェック
        if self.state.temporary_limit_until and now < self.state.temporary_limit_until:
            wait_time = self.state.temporary_limit_until - now
            logger.info(f"一時的なAPI制限により {wait_time:.1f} 秒待機中")
            await asyncio.sleep(wait_time)
            return
        
        # 通常のレート制限チェック
        cutoff = now - self.state.time_window
        
        # 古いリクエスト履歴を削除
        while self.state.requests and self.state.requests[0] < cutoff:
            self.state.requests.popleft()
        
        # リクエスト数が上限に達している場合
        if len(self.state.requests) >= self.state.max_requests_per_minute:
            # 最も古いリクエストから time_window が経過するまで待機
            oldest_request = self.state.requests[0]
            wait_time = (oldest_request + self.state.time_window) - now
            
            if wait_time > 0:
                logger.info(f"レート制限により {wait_time:.1f} 秒待機中")
                await asyncio.sleep(wait_time)

    def handle_response(self, response: httpx.Response) -> None:
        """
        レスポンスを処理してレート制限状態を更新します。

        Args:
            response: HTTPレスポンス
        """
        status_code = response.status_code
        
        if status_code == 429:  # Too Many Requests
            self._handle_rate_limit_response(response)
        elif status_code >= 500:  # Server Error
            self._handle_server_error(response)
        elif 200 <= status_code < 300:  # Success
            self._handle_success_response()
        else:
            # その他のエラーは特別な処理なし
            pass

    def _handle_rate_limit_response(self, response: httpx.Response) -> None:
        """レート制限レスポンス（429）を処理します"""
        logger.warning("API制限に達しました (429 Too Many Requests)")
        
        # Retry-Afterヘッダーをチェック
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                delay = float(retry_after)
                self.state.temporary_limit_until = time.time() + delay
                logger.info(f"Retry-Afterヘッダーに基づき {delay} 秒間制限")
            except ValueError:
                # Retry-Afterが日時形式の場合は基本遅延を使用
                delay = self._calculate_backoff_delay()
                self.state.temporary_limit_until = time.time() + delay
        else:
            # Retry-Afterヘッダーがない場合はバックオフ遅延を使用
            delay = self._calculate_backoff_delay()
            self.state.temporary_limit_until = time.time() + delay
        
        # バックオフ乗数を増加
        self.state.backoff_multiplier = min(
            self.state.backoff_multiplier * self.backoff_factor,
            self.max_delay / self.base_delay
        )

    def _handle_server_error(self, response: httpx.Response) -> None:
        """サーバーエラー（5xx）を処理します"""
        logger.warning(f"サーバーエラー: {response.status_code}")
        
        # バックオフ乗数を増加（レート制限ほど激しくない）
        self.state.backoff_multiplier = min(
            self.state.backoff_multiplier * 1.5,
            self.max_delay / self.base_delay
        )

    def _handle_success_response(self) -> None:
        """成功レスポンスを処理します"""
        # バックオフ乗数をリセット
        self.state.backoff_multiplier = 1.0
        
        # 一時的な制限をクリア
        self.state.temporary_limit_until = None

    def _calculate_backoff_delay(self) -> float:
        """バックオフ遅延時間を計算します"""
        delay = self.base_delay * self.state.backoff_multiplier
        return min(delay, self.max_delay)

    def create_rate_limit_error(
        self,
        retry_after: Optional[float] = None
    ) -> ErrorInfo:
        """
        レート制限エラー情報を作成します。

        Args:
            retry_after: リトライまでの推奨待機時間

        Returns:
            ErrorInfo: レート制限エラー情報
        """
        return ErrorInfo(
            error_type=ErrorType.RATE_LIMIT_ERROR,
            message="API制限に達しました。しばらく時間をおいてから再試行してください。",
            details={
                "current_requests": len(self.state.requests),
                "max_requests_per_minute": self.state.max_requests_per_minute,
                "backoff_multiplier": self.state.backoff_multiplier
            },
            retry_after=retry_after or self._calculate_backoff_delay()
        )

    def get_status(self) -> Dict[str, Any]:
        """
        レート制限の現在の状態を取得します。

        Returns:
            Dict[str, Any]: 状態情報
        """
        now = time.time()
        
        # 古いリクエスト履歴を削除
        cutoff = now - self.state.time_window
        while self.state.requests and self.state.requests[0] < cutoff:
            self.state.requests.popleft()
        
        return {
            "current_requests": len(self.state.requests),
            "max_requests_per_minute": self.state.max_requests_per_minute,
            "remaining_requests": max(0, self.state.max_requests_per_minute - len(self.state.requests)),
            "backoff_multiplier": self.state.backoff_multiplier,
            "temporary_limit_active": (
                self.state.temporary_limit_until is not None and 
                now < self.state.temporary_limit_until
            ),
            "temporary_limit_remaining": (
                max(0, self.state.temporary_limit_until - now) 
                if self.state.temporary_limit_until else 0
            )
        }

    async def reset(self) -> None:
        """レート制限状態をリセットします"""
        async with self._lock:
            self.state.requests.clear()
            self.state.backoff_multiplier = 1.0
            self.state.temporary_limit_until = None
            self.state.last_reset = time.time()
            logger.info("レート制限状態をリセットしました")