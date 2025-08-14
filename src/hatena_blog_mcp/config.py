"""
Configuration Manager for Hatena Blog MCP Server.
設定ファイル読み込みと環境変数管理を提供します。
"""

from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from .models import AuthConfig, BlogConfig, ErrorInfo, ErrorType


class HatenaBlogSettings(BaseSettings):
    """環境変数と設定ファイルからの設定読み込み"""

    # はてなブログ認証情報
    hatena_username: str = ""
    hatena_blog_id: str = ""
    hatena_api_key: str = ""

    # 設定ファイル
    model_config = SettingsConfigDict(
        # .env も環境変数も許可するが、テストのため大小区別なし
        case_sensitive=False,
        extra='ignore'
    )


class ConfigManager:
    """設定管理クラス"""

    def __init__(self, config_path: Path | None = None) -> None:
        """
        設定マネージャーを初期化します。

        Args:
            config_path: 設定ファイルのパス（省略時は.envを使用）
        """
        self._use_file = config_path is not None
        self.config_path = config_path or Path(".env")
        self._settings: HatenaBlogSettings | None = None

    def load_settings(self) -> HatenaBlogSettings:
        """
        設定を読み込みます。

        Returns:
            HatenaBlogSettings: 読み込まれた設定

        Raises:
            ValueError: 設定読み込みに失敗した場合
        """
        try:
            # まずは環境変数から読み込み（_env_file=Noneを明示）
            self._settings = HatenaBlogSettings(_env_file=None)

            # 明示的にファイルパスが指定された場合のみ、.env をマージ（環境変数が優先）
            if self._use_file and self.config_path.exists():
                file_settings = HatenaBlogSettings(
                    _env_file=str(self.config_path),
                    _env_file_encoding='utf-8'
                )
                # 空文字は上書きしないように条件付きで統合
                if file_settings.hatena_username:
                    self._settings.hatena_username = file_settings.hatena_username
                if file_settings.hatena_blog_id:
                    self._settings.hatena_blog_id = file_settings.hatena_blog_id
                if file_settings.hatena_api_key:
                    self._settings.hatena_api_key = file_settings.hatena_api_key

            return self._settings
        except ValidationError as e:
            raise ValueError(f"設定読み込みエラー: {e}")

    def get_auth_config(self) -> AuthConfig:
        """
        認証設定を取得します。

        Returns:
            AuthConfig: 認証設定

        Raises:
            ValueError: 必須の認証情報が不足している場合
        """
        if not self._settings:
            self.load_settings()

        assert self._settings is not None

        if not self._settings.hatena_username:
            raise ValueError("HATENA_USERNAME が設定されていません")
        if not self._settings.hatena_api_key:
            raise ValueError("HATENA_API_KEY が設定されていません")

        return AuthConfig(
            username=self._settings.hatena_username,
            password=self._settings.hatena_api_key
        )

    def get_blog_config(self) -> BlogConfig:
        """
        ブログ設定を取得します。

        Returns:
            BlogConfig: ブログ設定

        Raises:
            ValueError: 必須の設定が不足している場合
        """
        if not self._settings:
            self.load_settings()

        assert self._settings is not None

        if not self._settings.hatena_username:
            raise ValueError("HATENA_USERNAME が設定されていません")
        if not self._settings.hatena_blog_id:
            raise ValueError("HATENA_BLOG_ID が設定されていません")
        if not self._settings.hatena_api_key:
            raise ValueError("HATENA_API_KEY が設定されていません")

        return BlogConfig(
            username=self._settings.hatena_username,
            blog_id=self._settings.hatena_blog_id,
            api_key=self._settings.hatena_api_key
        )

    def validate_configuration(self) -> tuple[bool, list[str]]:
        """
        設定の妥当性を検証します。

        Returns:
            tuple[bool, list[str]]: (有効性, エラーメッセージ一覧)
        """
        errors = []

        try:
            self.load_settings()
        except ValueError as e:
            errors.append(str(e))
            return False, errors

        # 必須項目チェック
        assert self._settings is not None
        if not self._settings.hatena_username:
            errors.append("HATENA_USERNAME が設定されていません")
        if not self._settings.hatena_blog_id:
            errors.append("HATENA_BLOG_ID が設定されていません")
        if not self._settings.hatena_api_key:
            errors.append("HATENA_API_KEY が設定されていません")

        return len(errors) == 0, errors

    def create_config_error(self, errors: list[str]) -> ErrorInfo:
        """
        設定エラー情報を作成します。

        Args:
            errors: エラーメッセージ一覧

        Returns:
            ErrorInfo: 設定エラー情報
        """
        setup_guide = {
            "message": "以下の手順で認証情報を設定してください",
            "steps": [
                "1. プロジェクトルートに .env ファイルを作成",
                "2. 以下の形式で認証情報を記載:",
                "   HATENA_USERNAME=your_username",
                "   HATENA_BLOG_ID=your_blog_id",
                "   HATENA_API_KEY=your_api_key",
                "3. MCPサーバーを再起動"
            ],
            "errors": errors
        }

        return ErrorInfo(
            error_type=ErrorType.VALIDATION_ERROR,
            message="認証情報の設定が不完全です",
            details=setup_guide,
            retry_after=None
        )

    def generate_env_template(self) -> str:
        """
        .envファイルのテンプレートを生成します。

        Returns:
            str: .envファイルテンプレート
        """
        return """# Hatena Blog MCP Server Configuration
# はてなブログMCPサーバー設定

# はてなユーザーID
HATENA_USERNAME=your_username_here

# ブログID（ブログのURLから取得: https://your_blog_id.hatenablog.com/）
HATENA_BLOG_ID=your_blog_id_here

# APIキー（はてなブログの設定→詳細設定→AtomPub APIキーから取得）
HATENA_API_KEY=your_api_key_here
"""
