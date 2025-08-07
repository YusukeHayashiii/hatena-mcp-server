"""
HTTP Client for Hatena Blog AtomPub API.
WSSE認証とXML処理を統合したHTTPクライアントを提供します。
"""

import asyncio
import logging
from typing import Any, Optional, Dict, Union
from urllib.parse import urljoin

import httpx
from lxml import etree

from .auth import AuthenticationManager
from .models import ErrorInfo, ErrorType
from .rate_limiter import RateLimiter


logger = logging.getLogger(__name__)


class HatenaHttpClient:
    """はてなブログAPI用のHTTPクライアント"""
    
    HATENA_BLOG_BASE_URL = "https://blog.hatena.ne.jp"
    
    def __init__(
        self,
        auth_manager: AuthenticationManager,
        username: str,
        blog_id: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        base_url: Optional[str] = None,
        rate_limiter: Optional[RateLimiter] = None
    ) -> None:
        """
        HTTPクライアントを初期化します。

        Args:
            auth_manager: WSSE認証マネージャー
            username: はてなユーザー名
            blog_id: ブログID
            timeout: リクエストタイムアウト（秒）
            max_retries: 最大リトライ回数
            base_url: ベースURL（テスト用）
            rate_limiter: レート制限器（指定しない場合はデフォルト設定で作成）
        """
        self.auth_manager = auth_manager
        self.username = username
        self.blog_id = blog_id
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_url = base_url or self.HATENA_BLOG_BASE_URL
        self.rate_limiter = rate_limiter or RateLimiter()
        
        # AtomPub APIエンドポイントのベースURL
        self.atom_base_url = f"{self.base_url}/{username}/{blog_id}/atom"
        
        # httpxクライアントの設定
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
            http2=False  # HTTP/2を無効化（h2パッケージが不要）
        )

    async def __aenter__(self):
        """非同期コンテキストマネージャーのエントリ"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャーの終了"""
        await self.close()

    async def close(self) -> None:
        """HTTPクライアントを閉じます"""
        await self._client.aclose()

    def _build_url(self, path: str) -> str:
        """APIエンドポイントのURLを構築します"""
        return urljoin(f"{self.atom_base_url}/", path.lstrip("/"))

    async def _make_request(
        self,
        method: str,
        url: str,
        content: Optional[Union[str, bytes]] = None,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> httpx.Response:
        """
        認証付きHTTPリクエストを実行します。

        Args:
            method: HTTPメソッド
            url: リクエストURL
            content: リクエストボディ
            headers: 追加ヘッダー
            params: クエリパラメータ

        Returns:
            httpx.Response: レスポンスオブジェクト

        Raises:
            httpx.HTTPError: リクエスト失敗時
        """
        # 認証ヘッダーを取得
        auth_headers = self.auth_manager.get_auth_headers()
        
        # ヘッダーをマージ
        request_headers = auth_headers.copy()
        if headers:
            request_headers.update(headers)

        # レート制限を適用
        await self.rate_limiter.acquire()

        # リトライロジック
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(
                    f"HTTPリクエスト実行 (試行 {attempt + 1}/{self.max_retries + 1}): "
                    f"{method} {url}"
                )
                
                response = await self._client.request(
                    method=method,
                    url=url,
                    content=content,
                    headers=request_headers,
                    params=params
                )
                
                # レート制限器にレスポンスを通知
                self.rate_limiter.handle_response(response)
                
                # ステータスコードをチェック
                response.raise_for_status()
                
                logger.debug(f"HTTPレスポンス: {response.status_code}")
                return response

            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTPステータスエラー (試行 {attempt + 1}): {e}")
                
                # レート制限器にレスポンスを通知
                self.rate_limiter.handle_response(e.response)
                
                # 429（レート制限）は特別な処理
                if e.response.status_code == 429:
                    if attempt == self.max_retries:
                        # 最後の試行の場合はレート制限エラーを作成
                        rate_limit_error = self.rate_limiter.create_rate_limit_error()
                        raise httpx.HTTPStatusError(
                            message=rate_limit_error.message,
                            request=e.request,
                            response=e.response
                        )
                    # まだリトライする場合は続行
                    last_exception = e
                elif e.response.status_code < 500:
                    # その他の4xx系エラーはリトライしない
                    raise
                else:
                    last_exception = e

            except httpx.RequestError as e:
                logger.warning(f"HTTPリクエストエラー (試行 {attempt + 1}): {e}")
                last_exception = e

            # 最後の試行でない場合、指数バックオフで待機
            if attempt < self.max_retries:
                wait_time = 2 ** attempt
                logger.debug(f"リトライ前に {wait_time} 秒待機")
                await asyncio.sleep(wait_time)

        # すべてのリトライが失敗した場合
        if last_exception:
            raise last_exception
        else:
            raise httpx.RequestError("予期しないエラーが発生しました")

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """
        GETリクエストを実行します。

        Args:
            path: APIパス
            params: クエリパラメータ
            headers: 追加ヘッダー

        Returns:
            httpx.Response: レスポンス
        """
        url = self._build_url(path)
        return await self._make_request("GET", url, params=params, headers=headers)

    async def post(
        self,
        path: str,
        xml_content: Union[str, bytes, etree._Element],
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """
        POSTリクエストを実行します（XML送信）。

        Args:
            path: APIパス
            xml_content: XMLコンテンツ
            headers: 追加ヘッダー

        Returns:
            httpx.Response: レスポンス
        """
        url = self._build_url(path)
        
        # XMLコンテンツの処理
        if isinstance(xml_content, etree._Element):
            content = etree.tostring(xml_content, encoding='utf-8', xml_declaration=True)
        elif isinstance(xml_content, str):
            content = xml_content.encode('utf-8')
        else:
            content = xml_content

        return await self._make_request("POST", url, content=content, headers=headers)

    async def put(
        self,
        path: str,
        xml_content: Union[str, bytes, etree._Element],
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """
        PUTリクエストを実行します（XML送信）。

        Args:
            path: APIパス
            xml_content: XMLコンテンツ
            headers: 追加ヘッダー

        Returns:
            httpx.Response: レスポンス
        """
        url = self._build_url(path)
        
        # XMLコンテンツの処理
        if isinstance(xml_content, etree._Element):
            content = etree.tostring(xml_content, encoding='utf-8', xml_declaration=True)
        elif isinstance(xml_content, str):
            content = xml_content.encode('utf-8')
        else:
            content = xml_content

        return await self._make_request("PUT", url, content=content, headers=headers)

    async def delete(
        self,
        path: str,
        headers: Optional[Dict[str, str]] = None
    ) -> httpx.Response:
        """
        DELETEリクエストを実行します。

        Args:
            path: APIパス
            headers: 追加ヘッダー

        Returns:
            httpx.Response: レスポンス
        """
        url = self._build_url(path)
        return await self._make_request("DELETE", url, headers=headers)

    def create_network_error(
        self,
        message: str,
        original_error: Optional[Exception] = None
    ) -> ErrorInfo:
        """
        ネットワークエラー情報を作成します。

        Args:
            message: エラーメッセージ
            original_error: 元の例外

        Returns:
            ErrorInfo: ネットワークエラー情報
        """
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__

        return ErrorInfo(
            error_type=ErrorType.NETWORK_ERROR,
            message=message,
            details=details,
            retry_after=None
        )