"""
MCP ツール用の統一エラーハンドリング
"""

import logging
import asyncio
from functools import wraps
from typing import Callable, Any, Dict, Optional

from .models import ErrorInfo, ErrorType

logger = logging.getLogger(__name__)


def handle_mcp_errors(func: Callable) -> Callable:
    """
    MCP ツール関数用のデコレータ - 統一されたエラーハンドリングを提供
    同期/非同期の両方の関数に対応。
    """
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> str:
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                # エラーをログに記録
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                # エラータイプを判定
                error_info = classify_error(e)
                # ユーザーフレンドリーなエラーメッセージを生成
                return format_error_message(error_info, func.__name__)
        return async_wrapper
    else:
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> str:
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                # エラーをログに記録
                logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                # エラータイプを判定
                error_info = classify_error(e)
                # ユーザーフレンドリーなエラーメッセージを生成
                return format_error_message(error_info, func.__name__)
        return sync_wrapper


def classify_error(exception: Exception) -> ErrorInfo:
    """
    例外をErrorInfoに分類する
    """
    error_message = str(exception)
    
    # 認証エラー
    if any(keyword in error_message.lower() for keyword in ['auth', 'unauthorized', 'wsse', 'credential']):
        return ErrorInfo(
            error_type=ErrorType.AUTH_ERROR,
            message="認証に失敗しました。ユーザーID、ブログID、APIキーの設定を確認してください。",
            details={"original_error": error_message, "error_code": "AUTH_FAILED"}
        )
    
    # ネットワークエラー
    if any(keyword in error_message.lower() for keyword in ['connection', 'timeout', 'network', 'unreachable']):
        return ErrorInfo(
            error_type=ErrorType.NETWORK_ERROR,
            message="ネットワーク接続エラーが発生しました。インターネット接続を確認してください。",
            details={"original_error": error_message, "error_code": "NETWORK_FAILED"}
        )
    
    # API制限エラー
    if any(keyword in error_message.lower() for keyword in ['rate limit', 'too many requests', '429']):
        return ErrorInfo(
            error_type=ErrorType.RATE_LIMIT_ERROR,
            message="API呼び出し制限に達しました。しばらく時間をおいてから再試行してください。",
            details={"original_error": error_message, "error_code": "RATE_LIMITED"}
        )
    
    # データエラー
    if any(keyword in error_message.lower() for keyword in ['validation', 'invalid', 'required', 'missing']):
        return ErrorInfo(
            error_type=ErrorType.DATA_ERROR,
            message="入力データに問題があります。パラメータを確認してください。",
            details={"original_error": error_message, "error_code": "INVALID_DATA"}
        )
    
    # ファイルエラー
    if any(keyword in error_message.lower() for keyword in ['file not found', 'no such file', 'permission denied']):
        return ErrorInfo(
            error_type=ErrorType.DATA_ERROR,
            message="ファイルアクセスエラーが発生しました。ファイルパスと権限を確認してください。",
            details={"original_error": error_message, "error_code": "FILE_ERROR"}
        )
    
    # その他のエラー
    return ErrorInfo(
        error_type=ErrorType.DATA_ERROR,
        message="予期しないエラーが発生しました。",
        details={"original_error": error_message, "error_code": "UNKNOWN_ERROR"}
    )


def format_error_message(error_info: ErrorInfo, function_name: str) -> str:
    """
    ErrorInfo をユーザーフレンドリーなメッセージに変換
    """
    base_message = f"❌ {error_info.message}"
    
    # エラータイプ別の追加情報
    if error_info.error_type == ErrorType.AUTH_ERROR:
        base_message += "\n\n💡 解決方法:\n"
        base_message += "1. .env ファイルの HATENA_USER_ID を確認\n"
        base_message += "2. .env ファイルの HATENA_BLOG_ID を確認\n"
        base_message += "3. .env ファイルの HATENA_API_KEY を確認\n"
        base_message += "4. はてなブログの設定画面でAPIキーが有効か確認"
    
    elif error_info.error_type == ErrorType.NETWORK_ERROR:
        base_message += "\n\n💡 解決方法:\n"
        base_message += "1. インターネット接続を確認\n"
        base_message += "2. ファイアウォール設定を確認\n"
        base_message += "3. しばらく時間をおいてから再試行"
    
    elif error_info.error_type == ErrorType.RATE_LIMIT_ERROR:
        base_message += "\n\n💡 解決方法:\n"
        base_message += "1. 数分間待ってから再試行\n"
        base_message += "2. API呼び出し頻度を下げる"
        
        # retry_after情報があれば追加
        if error_info.retry_after:
            base_message += f"\n⏰ 推奨待機時間: {error_info.retry_after}秒"
    
    elif error_info.error_type == ErrorType.DATA_ERROR:
        base_message += "\n\n💡 解決方法:\n"
        base_message += "1. 必須パラメータが指定されているか確認\n"
        base_message += "2. パラメータの形式が正しいか確認\n"
        base_message += "3. ファイルパスが正しいか確認"
    
    # 詳細情報を追加（デバッグ用）
    if error_info.details and "original_error" in error_info.details:
        base_message += f"\n\n🔍 詳細: {error_info.details['original_error']}"
    
    # エラーコードを追加
    if error_info.details and "error_code" in error_info.details:
        base_message += f"\n\n📋 エラーコード: {error_info.details['error_code']}"
    
    return base_message


def validate_required_params(params: Dict[str, Any], required_fields: list[str]) -> Optional[str]:
    """
    必須パラメータの検証
    
    Returns:
        None if validation passes, error message if validation fails
    """
    missing_fields = []
    for field in required_fields:
        if field not in params or params[field] is None or params[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        return f"必須パラメータが不足しています: {', '.join(missing_fields)}"
    
    return None


def validate_file_path(path: str) -> Optional[str]:
    """
    ファイルパスの検証
    
    Returns:
        None if validation passes, error message if validation fails
    """
    import os
    
    if not path or not isinstance(path, str):
        return "ファイルパスが指定されていません。"
    
    if not os.path.exists(path):
        return f"ファイルが見つかりません: {path}"
    
    if not os.path.isfile(path):
        return f"指定されたパスはファイルではありません: {path}"
    
    if not path.lower().endswith('.md'):
        return f"Markdownファイル（.md）を指定してください: {path}"
    
    return None