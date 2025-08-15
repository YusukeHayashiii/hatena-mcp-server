"""
サービスファクトリ - 依存性注入とサービス管理
"""

import asyncio
from functools import lru_cache
from typing import Optional

from .auth import AuthenticationManager
from .blog_service import BlogPostService
from .config import ConfigManager
from .http_client import HatenaHttpClient


class ServiceFactory:
    """BlogPostService とその依存関係を管理するファクトリクラス"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self._config_manager = config_manager or ConfigManager()
        self._blog_service: Optional[BlogPostService] = None
    
    @property
    def config_manager(self) -> ConfigManager:
        """設定マネージャーを取得"""
        return self._config_manager
    
    def create_blog_service(self) -> BlogPostService:
        """BlogPostService インスタンスを作成（再利用可能）"""
        if self._blog_service is None:
            # 設定を読み込み
            # 認証設定を読み込み
            auth_config = self._config_manager.get_auth_config()
            
            # 認証マネージャーを作成
            auth_manager = AuthenticationManager(auth_config)
            
            # ブログ設定を読み込み
            blog_config = self._config_manager.get_blog_config()
            
            # HTTPクライアントを作成
            http_client = HatenaHttpClient(auth_manager, auth_config.username, blog_config.blog_id)
            
            # BlogPostService を作成
            self._blog_service = BlogPostService(
                auth_manager=auth_manager, 
                username=blog_config.username,
                blog_id=blog_config.blog_id,
                http_client=http_client
            )
        
        return self._blog_service
    
    async def close(self):
        """リソースのクリーンアップ"""
        if self._blog_service:
            await self._blog_service.close()
            self._blog_service = None


# グローバルファクトリインスタンス（シングルトン）
_global_factory: Optional[ServiceFactory] = None


def get_service_factory() -> ServiceFactory:
    """グローバルサービスファクトリを取得"""
    global _global_factory
    if _global_factory is None:
        _global_factory = ServiceFactory()
    return _global_factory


def get_blog_service() -> BlogPostService:
    """BlogPostService インスタンスを取得"""
    factory = get_service_factory()
    return factory.create_blog_service()


async def cleanup_services():
    """全サービスのクリーンアップ"""
    global _global_factory
    if _global_factory:
        await _global_factory.close()
        _global_factory = None