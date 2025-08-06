"""
Tests for Configuration Manager.
"""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from hatena_blog_mcp.config import ConfigManager, HatenaBlogSettings
from hatena_blog_mcp.models import AuthConfig, BlogConfig, ErrorType


class TestHatenaBlogSettings:
    """設定モデルのテスト"""

    def test_default_values(self):
        """デフォルト値のテスト"""
        settings = HatenaBlogSettings()

        assert settings.hatena_username == ""
        assert settings.hatena_blog_id == ""
        assert settings.hatena_api_key == ""


class TestConfigManager:
    """設定マネージャーのテスト"""

    def test_init_default_path(self):
        """デフォルトパスでの初期化テスト"""
        config_manager = ConfigManager()

        assert config_manager.config_path == Path(".env")

    def test_init_custom_path(self):
        """カスタムパスでの初期化テスト"""
        custom_path = Path("/custom/.env")
        config_manager = ConfigManager(custom_path)

        assert config_manager.config_path == custom_path

    @patch.dict(os.environ, {
        "HATENA_USERNAME": "testuser",
        "HATENA_BLOG_ID": "testblog",
        "HATENA_API_KEY": "testkey"
    })
    def test_load_settings_from_env(self):
        """環境変数からの設定読み込みテスト"""
        config_manager = ConfigManager()
        settings = config_manager.load_settings()

        assert settings.hatena_username == "testuser"
        assert settings.hatena_blog_id == "testblog"
        assert settings.hatena_api_key == "testkey"

    @patch.dict(os.environ, {
        "HATENA_USERNAME": "fileuser",
        "HATENA_BLOG_ID": "fileblog",
        "HATENA_API_KEY": "filekey"
    })
    @patch("pathlib.Path.exists")
    def test_load_settings_from_file(self, mock_exists):
        """ファイルからの設定読み込みテスト（環境変数経由）"""
        mock_exists.return_value = True

        config_manager = ConfigManager()
        settings = config_manager.load_settings()

        assert settings.hatena_username == "fileuser"
        assert settings.hatena_blog_id == "fileblog"
        assert settings.hatena_api_key == "filekey"

    @patch.dict(os.environ, {
        "HATENA_USERNAME": "testuser",
        "HATENA_API_KEY": "testkey"
    })
    def test_get_auth_config_success(self):
        """認証設定取得成功テスト"""
        config_manager = ConfigManager()
        auth_config = config_manager.get_auth_config()

        assert isinstance(auth_config, AuthConfig)
        assert auth_config.username == "testuser"
        assert auth_config.password == "testkey"

    @patch.dict(os.environ, {"HATENA_API_KEY": "testkey"})
    def test_get_auth_config_missing_username(self):
        """ユーザー名不足での認証設定取得テスト"""
        config_manager = ConfigManager()

        with pytest.raises(ValueError, match="HATENA_USERNAME が設定されていません"):
            config_manager.get_auth_config()

    @patch.dict(os.environ, {"HATENA_USERNAME": "testuser"})
    def test_get_auth_config_missing_api_key(self):
        """APIキー不足での認証設定取得テスト"""
        config_manager = ConfigManager()

        with pytest.raises(ValueError, match="HATENA_API_KEY が設定されていません"):
            config_manager.get_auth_config()

    @patch.dict(os.environ, {
        "HATENA_USERNAME": "testuser",
        "HATENA_BLOG_ID": "testblog",
        "HATENA_API_KEY": "testkey"
    })
    def test_get_blog_config_success(self):
        """ブログ設定取得成功テスト"""
        config_manager = ConfigManager()
        blog_config = config_manager.get_blog_config()

        assert isinstance(blog_config, BlogConfig)
        assert blog_config.username == "testuser"
        assert blog_config.blog_id == "testblog"
        assert blog_config.api_key == "testkey"

    @patch.dict(os.environ, {
        "HATENA_USERNAME": "testuser",
        "HATENA_API_KEY": "testkey"
    })
    def test_get_blog_config_missing_blog_id(self):
        """ブログID不足でのブログ設定取得テスト"""
        config_manager = ConfigManager()

        with pytest.raises(ValueError, match="HATENA_BLOG_ID が設定されていません"):
            config_manager.get_blog_config()

    @patch.dict(os.environ, {
        "HATENA_USERNAME": "testuser",
        "HATENA_BLOG_ID": "testblog",
        "HATENA_API_KEY": "testkey"
    })
    def test_validate_configuration_success(self):
        """設定検証成功テスト"""
        config_manager = ConfigManager()
        is_valid, errors = config_manager.validate_configuration()

        assert is_valid is True
        assert errors == []

    @patch.dict(os.environ, {"HATENA_USERNAME": "testuser"})
    def test_validate_configuration_missing_fields(self):
        """不完全な設定の検証テスト"""
        config_manager = ConfigManager()
        is_valid, errors = config_manager.validate_configuration()

        assert is_valid is False
        assert "HATENA_BLOG_ID が設定されていません" in errors
        assert "HATENA_API_KEY が設定されていません" in errors

    @patch.dict(os.environ, {}, clear=True)
    def test_validate_configuration_all_missing(self):
        """全ての設定が不足している場合のテスト"""
        config_manager = ConfigManager()
        is_valid, errors = config_manager.validate_configuration()

        assert is_valid is False
        assert "HATENA_USERNAME が設定されていません" in errors
        assert "HATENA_BLOG_ID が設定されていません" in errors
        assert "HATENA_API_KEY が設定されていません" in errors

    def test_create_config_error(self):
        """設定エラー作成テスト"""
        config_manager = ConfigManager()
        errors = ["エラー1", "エラー2"]

        error_info = config_manager.create_config_error(errors)

        assert error_info.error_type == ErrorType.VALIDATION_ERROR
        assert error_info.message == "認証情報の設定が不完全です"
        assert "errors" in error_info.details
        assert error_info.details["errors"] == errors
        assert "steps" in error_info.details

    def test_generate_env_template(self):
        """環境変数テンプレート生成テスト"""
        config_manager = ConfigManager()
        template = config_manager.generate_env_template()

        assert "HATENA_USERNAME=" in template
        assert "HATENA_BLOG_ID=" in template
        assert "HATENA_API_KEY=" in template
        assert "# Hatena Blog MCP Server Configuration" in template

    @patch("hatena_blog_mcp.config.HatenaBlogSettings")
    def test_load_settings_validation_error(self, mock_settings):
        """設定読み込み時のバリデーションエラーテスト"""
        from pydantic import ValidationError

        mock_settings.side_effect = ValidationError.from_exception_data(
            "HatenaBlogSettings",
            [{"type": "missing", "loc": ("field",), "msg": "Field required"}]
        )

        config_manager = ConfigManager()

        with pytest.raises(ValueError, match="設定読み込みエラー"):
            config_manager.load_settings()

    @patch.dict(os.environ, {}, clear=True)
    def test_multiple_operations_without_settings(self):
        """設定未読み込み状態での複数操作テスト"""
        config_manager = ConfigManager()

        # 複数の操作で設定が自動読み込みされることを確認
        is_valid1, _ = config_manager.validate_configuration()
        is_valid2, _ = config_manager.validate_configuration()

        assert is_valid1 == is_valid2
        assert config_manager._settings is not None
