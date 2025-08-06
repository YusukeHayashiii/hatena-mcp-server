"""
Tests for Authentication Manager.
"""

import base64
import hashlib
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from hatena_blog_mcp.auth import AuthenticationManager
from hatena_blog_mcp.models import AuthConfig, ErrorType


class TestAuthenticationManager:
    """認証マネージャーのテスト"""

    def test_init_valid_config(self):
        """有効な設定での初期化テスト"""
        config = AuthConfig(username="testuser", password="testpass")
        auth_manager = AuthenticationManager(config)

        assert auth_manager.config.username == "testuser"
        assert auth_manager.config.password == "testpass"

    def test_init_empty_username(self):
        """空のユーザー名での初期化テスト"""
        config = AuthConfig(username="", password="testpass")

        with pytest.raises(ValueError, match="ユーザー名が設定されていません"):
            AuthenticationManager(config)

    def test_init_empty_password(self):
        """空のパスワードでの初期化テスト"""
        config = AuthConfig(username="testuser", password="")

        with pytest.raises(ValueError, match="APIキーが設定されていません"):
            AuthenticationManager(config)

    def test_validate_credentials_valid(self):
        """有効な認証情報の検証テスト"""
        config = AuthConfig(username="testuser", password="testpass")
        auth_manager = AuthenticationManager(config)

        assert auth_manager.validate_credentials() is True

    def test_validate_credentials_invalid(self):
        """無効な認証情報の検証テスト"""
        config = AuthConfig(username="testuser", password="testpass")
        auth_manager = AuthenticationManager(config)

        # パスワードを空にして無効化
        auth_manager.config.password = ""

        assert auth_manager.validate_credentials() is False

    @patch('hatena_blog_mcp.auth.datetime')
    @patch('hatena_blog_mcp.auth.secrets.token_bytes')
    def test_get_auth_headers_format(self, mock_token_bytes, mock_datetime):
        """WSSE認証ヘッダーの形式テスト"""
        # モック設定
        mock_datetime.now.return_value.isoformat.return_value.replace.return_value = "2024-01-01T00:00:00Z"
        mock_token_bytes.return_value = b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\x09\\x0a\\x0b\\x0c\\x0d\\x0e\\x0f'

        config = AuthConfig(username="testuser", password="testpass")
        auth_manager = AuthenticationManager(config)

        headers = auth_manager.get_auth_headers()

        # ヘッダーの存在確認
        assert "X-WSSE" in headers
        assert "Content-Type" in headers
        assert "User-Agent" in headers

        # Content-Typeの確認
        assert headers["Content-Type"] == "application/atom+xml; charset=utf-8"
        assert headers["User-Agent"] == "hatena-blog-mcp-server/0.1.0"

        # WSSEヘッダーの形式確認
        wsse_header = headers["X-WSSE"]
        assert "UsernameToken" in wsse_header
        assert 'Username="testuser"' in wsse_header
        assert "PasswordDigest=" in wsse_header
        assert "Nonce=" in wsse_header
        assert "Created=" in wsse_header

    @patch('hatena_blog_mcp.auth.datetime')
    @patch('hatena_blog_mcp.auth.secrets.token_bytes')
    def test_get_auth_headers_digest_calculation(self, mock_token_bytes, mock_datetime):
        """PasswordDigestの計算テスト"""
        # 固定値でテスト
        created = "2024-01-01T00:00:00Z"
        nonce_bytes = b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\x09\\x0a\\x0b\\x0c\\x0d\\x0e\\x0f'

        mock_datetime.now.return_value.isoformat.return_value.replace.return_value = created
        mock_token_bytes.return_value = nonce_bytes

        config = AuthConfig(username="testuser", password="testpass")
        auth_manager = AuthenticationManager(config)

        headers = auth_manager.get_auth_headers()

        # 期待されるPasswordDigestを手動計算
        digest_input = nonce_bytes + created.encode('utf-8') + b"testpass"
        expected_digest = base64.b64encode(hashlib.sha1(digest_input).digest()).decode('ascii')

        wsse_header = headers["X-WSSE"]
        assert f'PasswordDigest="{expected_digest}"' in wsse_header

    def test_get_auth_headers_invalid_credentials(self):
        """無効な認証情報でのヘッダー生成テスト"""
        config = AuthConfig(username="testuser", password="testpass")
        auth_manager = AuthenticationManager(config)

        # 認証情報を無効化
        auth_manager.config.username = ""

        with pytest.raises(ValueError, match="認証情報が無効です"):
            auth_manager.get_auth_headers()

    def test_create_auth_error_basic(self):
        """基本的な認証エラー作成テスト"""
        config = AuthConfig(username="testuser", password="testpass")
        auth_manager = AuthenticationManager(config)

        error = auth_manager.create_auth_error("認証に失敗しました")

        assert error.error_type == ErrorType.AUTH_ERROR
        assert error.message == "認証に失敗しました"
        assert error.details == {}
        assert error.retry_after is None

    def test_create_auth_error_with_details(self):
        """詳細情報付き認証エラー作成テスト"""
        config = AuthConfig(username="testuser", password="testpass")
        auth_manager = AuthenticationManager(config)

        details = {"status_code": 401, "reason": "Unauthorized"}
        error = auth_manager.create_auth_error("認証に失敗しました", details)

        assert error.error_type == ErrorType.AUTH_ERROR
        assert error.message == "認証に失敗しました"
        assert error.details == details
        assert error.retry_after is None

    def test_multiple_auth_headers_unique_nonce(self):
        """複数回のヘッダー生成でナンスが異なることを確認"""
        config = AuthConfig(username="testuser", password="testpass")
        auth_manager = AuthenticationManager(config)

        headers1 = auth_manager.get_auth_headers()
        headers2 = auth_manager.get_auth_headers()

        # WSSEヘッダーが異なることを確認（ナンスとタイムスタンプが異なるため）
        assert headers1["X-WSSE"] != headers2["X-WSSE"]

    def test_auth_headers_contain_current_time(self):
        """認証ヘッダーに現在時刻が含まれることを確認"""
        config = AuthConfig(username="testuser", password="testpass")
        auth_manager = AuthenticationManager(config)

        # テスト実行前の時刻
        before_time = datetime.now(UTC)

        headers = auth_manager.get_auth_headers()

        # テスト実行後の時刻
        after_time = datetime.now(UTC)

        wsse_header = headers["X-WSSE"]

        # Created部分を抽出
        created_part = [part for part in wsse_header.split(", ") if part.startswith("Created=")]
        assert len(created_part) == 1

        created_str = created_part[0].split("=")[1].strip('"')
        created_time = datetime.fromisoformat(created_str.replace("Z", "+00:00"))

        # 生成された時刻が実行時間範囲内であることを確認
        assert before_time <= created_time <= after_time
