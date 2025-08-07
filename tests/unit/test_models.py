"""
Tests for Data Models.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from hatena_blog_mcp.models import (
    ApiResponse,
    AuthConfig,
    BlogConfig,
    BlogPost,
    ErrorInfo,
    ErrorType,
)


class TestErrorType:
    """エラータイプ列挙のテスト"""

    def test_error_types(self):
        """エラータイプの値確認"""
        assert ErrorType.AUTH_ERROR == "auth_error"
        assert ErrorType.API_LIMIT_ERROR == "api_limit_error"
        assert ErrorType.NETWORK_ERROR == "network_error"
        assert ErrorType.VALIDATION_ERROR == "validation_error"
        assert ErrorType.NOT_FOUND_ERROR == "not_found_error"
        assert ErrorType.PERMISSION_ERROR == "permission_error"


class TestAuthConfig:
    """認証設定のテスト"""

    def test_valid_auth_config(self):
        """有効な認証設定テスト"""
        config = AuthConfig(username="test_user", password="mock_password_test")

        assert config.username == "test_user"
        assert config.password == "mock_password_test"

    def test_auth_config_password_hidden_in_repr(self):
        """パスワードが表示に含まれないことを確認"""
        config = AuthConfig(username="test_user", password="mock_secret_for_testing")

        config_str = str(config)
        assert "test_user" in config_str
        assert "mock_secret_for_testing" not in config_str

    def test_auth_config_missing_fields(self):
        """必須フィールド不足のテスト"""
        with pytest.raises(ValidationError):
            AuthConfig(username="test_user")

        with pytest.raises(ValidationError):
            AuthConfig(password="mock_password_test")

    def test_auth_config_extra_fields_forbidden(self):
        """余分なフィールドが拒否されることを確認"""
        with pytest.raises(ValidationError):
            AuthConfig(username="test_user", password="mock_password_test", extra_field="value")


class TestBlogConfig:
    """ブログ設定のテスト"""

    def test_valid_blog_config(self):
        """有効なブログ設定テスト"""
        config = BlogConfig(
            username="testuser",
            blog_id="test_blog",
            api_key="mock_api_key_test"
        )

        assert config.username == "testuser"
        assert config.blog_id == "test_blog"
        assert config.api_key == "mock_api_key_test"

    def test_blog_config_api_key_hidden_in_repr(self):
        """APIキーが表示に含まれないことを確認"""
        config = BlogConfig(
            username="test_user",
            blog_id="test_blog",
            api_key="mock_secret_for_testing"
        )

        config_str = str(config)
        assert "test_user" in config_str
        assert "test_blog" in config_str
        assert "mock_secret_for_testing" not in config_str

    def test_blog_config_missing_fields(self):
        """必須フィールド不足のテスト"""
        with pytest.raises(ValidationError):
            BlogConfig(username="testuser", blog_id="test_blog")

        with pytest.raises(ValidationError):
            BlogConfig(username="testuser", api_key="mock_api_key_test")

        with pytest.raises(ValidationError):
            BlogConfig(blog_id="test_blog", api_key="mock_api_key_test")


class TestBlogPost:
    """ブログ記事のテスト"""

    def test_minimal_blog_post(self):
        """最小限のブログ記事テスト"""
        post = BlogPost(title="テストタイトル", content="テスト本文")

        assert post.title == "テストタイトル"
        assert post.content == "テスト本文"
        assert post.categories == []
        assert post.post_id is None
        assert post.post_url is None
        assert post.created_at is None
        assert post.updated_at is None

    def test_full_blog_post(self):
        """完全なブログ記事テスト"""
        created_time = datetime.now()
        updated_time = datetime.now()

        post = BlogPost(
            title="テストタイトル",
            content="テスト本文",
            categories=["カテゴリ1", "カテゴリ2"],
            post_id="123456",
            post_url="https://example.hatenablog.com/entry/test",
            created_at=created_time,
            updated_at=updated_time
        )

        assert post.title == "テストタイトル"
        assert post.content == "テスト本文"
        assert post.categories == ["カテゴリ1", "カテゴリ2"]
        assert post.post_id == "123456"
        assert post.post_url == "https://example.hatenablog.com/entry/test"
        assert post.created_at == created_time
        assert post.updated_at == updated_time

    def test_blog_post_missing_required_fields(self):
        """必須フィールド不足のテスト"""
        with pytest.raises(ValidationError):
            BlogPost(title="テストタイトル")

        with pytest.raises(ValidationError):
            BlogPost(content="テスト本文")

    def test_blog_post_categories_default(self):
        """カテゴリのデフォルト値テスト"""
        post = BlogPost(title="テスト", content="テスト")

        assert isinstance(post.categories, list)
        assert len(post.categories) == 0


class TestErrorInfo:
    """エラー情報のテスト"""

    def test_minimal_error_info(self):
        """最小限のエラー情報テスト"""
        error = ErrorInfo(
            error_type=ErrorType.AUTH_ERROR,
            message="認証エラー"
        )

        assert error.error_type == ErrorType.AUTH_ERROR
        assert error.message == "認証エラー"
        assert error.details is None
        assert error.retry_after is None

    def test_full_error_info(self):
        """完全なエラー情報テスト"""
        details = {"status_code": 401, "reason": "Unauthorized"}

        error = ErrorInfo(
            error_type=ErrorType.API_LIMIT_ERROR,
            message="API制限エラー",
            details=details,
            retry_after=300
        )

        assert error.error_type == ErrorType.API_LIMIT_ERROR
        assert error.message == "API制限エラー"
        assert error.details == details
        assert error.retry_after == 300

    def test_error_info_missing_required_fields(self):
        """必須フィールド不足のテスト"""
        with pytest.raises(ValidationError):
            ErrorInfo(error_type=ErrorType.AUTH_ERROR)

        with pytest.raises(ValidationError):
            ErrorInfo(message="エラー")


class TestApiResponse:
    """API応答のテスト"""

    def test_success_response(self):
        """成功応答のテスト"""
        data = {"post_id": "123", "url": "https://example.com"}

        response = ApiResponse(success=True, data=data)

        assert response.success is True
        assert response.data == data
        assert response.error is None

    def test_error_response(self):
        """エラー応答のテスト"""
        error = ErrorInfo(
            error_type=ErrorType.NETWORK_ERROR,
            message="ネットワークエラー"
        )

        response = ApiResponse(success=False, error=error)

        assert response.success is False
        assert response.data is None
        assert response.error == error

    def test_response_with_both_data_and_error(self):
        """データとエラー両方を持つ応答テスト"""
        data = {"partial_result": True}
        error = ErrorInfo(
            error_type=ErrorType.VALIDATION_ERROR,
            message="部分的な検証エラー"
        )

        response = ApiResponse(success=False, data=data, error=error)

        assert response.success is False
        assert response.data == data
        assert response.error == error

    def test_api_response_missing_success_field(self):
        """成功フラグ不足のテスト"""
        with pytest.raises(ValidationError):
            ApiResponse(data={"test": "data"})


class TestModelIntegration:
    """モデル統合テスト"""

    def test_blog_post_to_api_response(self):
        """ブログ記事からAPI応答への変換テスト"""
        post = BlogPost(
            title="テスト記事",
            content="テスト内容",
            post_id="123",
            post_url="https://example.com/123"
        )

        # ブログ記事をAPI応答のデータ部分として使用
        response_data = post.model_dump()

        response = ApiResponse(success=True, data=response_data)

        assert response.success is True
        assert response.data["title"] == "テスト記事"
        assert response.data["post_id"] == "123"

    def test_error_info_to_api_response(self):
        """エラー情報からAPI応答への変換テスト"""
        error = ErrorInfo(
            error_type=ErrorType.AUTH_ERROR,
            message="認証が必要です",
            details={"action": "login_required"}
        )

        response = ApiResponse(success=False, error=error)

        assert response.success is False
        assert response.error.error_type == ErrorType.AUTH_ERROR
        assert response.error.details["action"] == "login_required"
