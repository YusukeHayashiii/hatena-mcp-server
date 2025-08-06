"""
Authentication Manager for Hatena Blog MCP Server.
WSSE認証ヘッダー生成とクレデンシャル管理を提供します。
"""

import base64
import hashlib
import secrets
from datetime import UTC, datetime
from typing import Any

from .models import AuthConfig, ErrorInfo, ErrorType


class AuthenticationManager:
    """WSSE認証とクレデンシャル管理を担当するクラス"""

    def __init__(self, config: AuthConfig) -> None:
        """
        認証マネージャーを初期化します。

        Args:
            config: 認証設定（ユーザー名とAPIキー）
        """
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        """認証設定の妥当性を検証します"""
        if not self.config.username:
            raise ValueError("ユーザー名が設定されていません")
        if not self.config.password:
            raise ValueError("APIキーが設定されていません")

    def validate_credentials(self) -> bool:
        """
        認証情報の妥当性を検証します。

        Returns:
            bool: 認証情報が有効な場合True
        """
        try:
            self._validate_config()
            return True
        except ValueError:
            return False

    def get_auth_headers(self) -> dict[str, str]:
        """
        WSSE認証ヘッダーを生成します。

        AtomPub API用のWSSE認証ヘッダーを現在時刻のナンスと共に生成します。

        Returns:
            Dict[str, str]: 認証ヘッダー辞書

        Raises:
            ValueError: 認証情報が不正な場合
        """
        if not self.validate_credentials():
            raise ValueError("認証情報が無効です")

        # 現在時刻をISO 8601形式で取得
        created = datetime.now(UTC).isoformat().replace("+00:00", "Z")

        # ランダムなナンス生成（16バイト）
        nonce_bytes = secrets.token_bytes(16)
        nonce_b64 = base64.b64encode(nonce_bytes).decode('ascii')

        # PasswordDigest計算: Base64(SHA1(nonce + created + password))
        digest_input = nonce_bytes + created.encode('utf-8') + self.config.password.encode('utf-8')
        password_digest = base64.b64encode(hashlib.sha1(digest_input).digest()).decode('ascii')

        # WSSE認証ヘッダー構築
        wsse_header = (
            f'UsernameToken Username="{self.config.username}", '
            f'PasswordDigest="{password_digest}", '
            f'Nonce="{nonce_b64}", '
            f'Created="{created}"'
        )

        return {
            "X-WSSE": wsse_header,
            "Content-Type": "application/atom+xml; charset=utf-8",
            "User-Agent": "hatena-blog-mcp-server/0.1.0"
        }

    def create_auth_error(self, message: str, details: dict[str, Any] | None = None) -> ErrorInfo:
        """
        認証エラー情報を作成します。

        Args:
            message: エラーメッセージ
            details: エラー詳細情報

        Returns:
            ErrorInfo: 認証エラー情報
        """
        return ErrorInfo(
            error_type=ErrorType.AUTH_ERROR,
            message=message,
            details=details or {},
            retry_after=None
        )
