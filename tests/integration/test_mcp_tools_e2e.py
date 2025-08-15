"""
MCP ツール群のE2E統合テスト
"""

import os
import tempfile
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from hatena_blog_mcp.server import (
    create_blog_post,
    update_blog_post,
    get_blog_post,
    list_blog_posts,
    create_blog_post_from_markdown
)
from hatena_blog_mcp.models import BlogPost
from datetime import datetime


class TestMCPToolsE2E:
    """MCP ツール群のエンドツーエンドテスト"""
    
    @pytest.fixture
    def mock_blog_service(self):
        """BlogPostService のモック"""
        mock_service = AsyncMock()
        
        # create_post のモック応答
        mock_service.create_post.return_value = BlogPost(
            id="test-id-123",
            title="テスト記事",
            content="<p>テスト本文</p>",
            categories=["テスト"],
            summary="テスト要約",
            draft=False,
            created_at=datetime(2025, 8, 15, 12, 0, 0),
            updated_at=datetime(2025, 8, 15, 12, 0, 0),
            post_url="https://test.hatenablog.com/entry/test-id-123"
        )
        
        # update_post のモック応答
        mock_service.update_post.return_value = BlogPost(
            id="test-id-123",
            title="更新されたテスト記事",
            content="<p>更新されたテスト本文</p>",
            categories=["更新テスト"],
            summary="更新された要約",
            draft=False,
            created_at=datetime(2025, 8, 15, 12, 0, 0),
            updated_at=datetime(2025, 8, 15, 12, 30, 0),
            post_url="https://test.hatenablog.com/entry/test-id-123"
        )
        
        # get_post のモック応答
        mock_service.get_post.return_value = BlogPost(
            id="test-id-123",
            title="取得テスト記事",
            content="<p>取得テスト本文です。これは長い本文のテストです。</p>" * 10,
            categories=["取得テスト", "カテゴリ2"],
            summary="取得テスト要約",
            draft=True,
            created_at=datetime(2025, 8, 15, 12, 0, 0),
            updated_at=datetime(2025, 8, 15, 12, 0, 0),
            post_url="https://test.hatenablog.com/entry/test-id-123"
        )
        
        # list_posts のモック応答
        mock_service.list_posts.return_value = [
            BlogPost(
                id="test-id-1",
                title="記事1",
                content="本文1",
                categories=["カテゴリ1"],
                summary="要約1",
                draft=False,
                created_at=datetime(2025, 8, 15, 10, 0, 0),
                updated_at=datetime(2025, 8, 15, 10, 0, 0),
                post_url="https://test.hatenablog.com/entry/test-id-1"
            ),
            BlogPost(
                id="test-id-2",
                title="記事2",
                content="本文2",
                categories=[],
                summary="要約2",
                draft=True,
                created_at=datetime(2025, 8, 15, 11, 0, 0),
                updated_at=datetime(2025, 8, 15, 11, 0, 0),
                post_url="https://test.hatenablog.com/entry/test-id-2"
            )
        ]
        
        # create_post_from_markdown のモック応答
        mock_service.create_post_from_markdown.return_value = BlogPost(
            id="markdown-id-123",
            title="Markdownテスト記事",
            content="<h1>Markdownから生成</h1><p>本文です。</p>",
            categories=["Markdown"],
            summary="Markdownテスト",
            draft=False,
            created_at=datetime(2025, 8, 15, 13, 0, 0),
            updated_at=datetime(2025, 8, 15, 13, 0, 0),
            post_url="https://test.hatenablog.com/entry/markdown-id-123"
        )
        
        return mock_service
    
    @pytest.fixture
    def markdown_file(self):
        """テスト用Markdownファイルを作成"""
        content = """---
title: Markdownテスト記事
categories: [Markdown, テスト]
draft: false
---

# Markdownから生成

これはMarkdownファイルからの投稿テストです。

## セクション2

- リスト項目1
- リスト項目2
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        yield temp_path
        
        # クリーンアップ
        os.unlink(temp_path)
    
    def test_create_blog_post_success(self, mock_blog_service):
        """記事投稿の正常フロー"""
        with patch('hatena_blog_mcp.service_factory.get_blog_service', return_value=mock_blog_service):
            result = create_blog_post(
                title="テスト記事",
                content="<p>テスト本文</p>",
                categories=["テスト"],
                summary="テスト要約",
                draft=False
            )
        
        assert "✅ 記事を投稿しました!" in result
        assert "テスト記事" in result
        assert "https://test.hatenablog.com/entry/test-id-123" in result
        assert "test-id-123" in result
        
        # サービスが正しく呼ばれたことを確認
        mock_blog_service.create_post.assert_called_once_with(
            title="テスト記事",
            content="<p>テスト本文</p>",
            categories=["テスト"],
            summary="テスト要約",
            draft=False
        )
    
    def test_create_blog_post_missing_title(self):
        """必須パラメータ不足エラーのテスト"""
        result = create_blog_post(
            title="",  # 空のタイトル
            content="<p>テスト本文</p>"
        )
        
        assert "❌" in result
        assert "必須パラメータが不足しています" in result
        assert "title" in result
    
    def test_update_blog_post_success(self, mock_blog_service):
        """記事更新の正常フロー"""
        with patch('hatena_blog_mcp.service_factory.get_blog_service', return_value=mock_blog_service):
            result = update_blog_post(
                post_id="test-id-123",
                title="更新されたテスト記事",
                content="<p>更新されたテスト本文</p>",
                categories=["更新テスト"]
            )
        
        assert "✅ 記事を更新しました!" in result
        assert "更新されたテスト記事" in result
        assert "test-id-123" in result
        
        mock_blog_service.update_post.assert_called_once_with(
            post_id="test-id-123",
            title="更新されたテスト記事",
            content="<p>更新されたテスト本文</p>",
            categories=["更新テスト"],
            summary=None,
            draft=None
        )
    
    def test_update_blog_post_no_updates(self):
        """更新項目なしエラーのテスト"""
        result = update_blog_post(post_id="test-id-123")
        
        assert "❌" in result
        assert "更新する項目を少なくとも1つ指定してください" in result
    
    def test_get_blog_post_success(self, mock_blog_service):
        """記事取得の正常フロー"""
        with patch('hatena_blog_mcp.service_factory.get_blog_service', return_value=mock_blog_service):
            result = get_blog_post(post_id="test-id-123")
        
        assert "📄 記事情報:" in result
        assert "取得テスト記事" in result
        assert "📝 下書き" in result  # draft=True
        assert "取得テスト, カテゴリ2" in result
        assert "📖 本文プレビュー:" in result
        
        mock_blog_service.get_post.assert_called_once_with("test-id-123")
    
    def test_list_blog_posts_success(self, mock_blog_service):
        """記事一覧取得の正常フロー"""
        with patch('hatena_blog_mcp.service_factory.get_blog_service', return_value=mock_blog_service):
            result = list_blog_posts(limit=2)
        
        assert "📚 ブログ記事一覧 (2件):" in result
        assert "📢 記事1" in result  # draft=False
        assert "📝 記事2" in result  # draft=True
        assert "test-id-1" in result
        assert "test-id-2" in result
        
        mock_blog_service.list_posts.assert_called_once_with(limit=2)
    
    def test_list_blog_posts_invalid_limit(self):
        """無効なlimitパラメータのテスト"""
        result = list_blog_posts(limit=0)
        
        assert "❌" in result
        assert "limitは1以上100以下で指定してください" in result
        
        result = list_blog_posts(limit=101)
        
        assert "❌" in result
        assert "limitは1以上100以下で指定してください" in result
    
    def test_create_blog_post_from_markdown_success(self, mock_blog_service, markdown_file):
        """Markdown記事投稿の正常フロー"""
        with patch('hatena_blog_mcp.service_factory.get_blog_service', return_value=mock_blog_service):
            result = create_blog_post_from_markdown(path=markdown_file)
        
        assert "✅ Markdownから記事を投稿しました!" in result
        assert "Markdownテスト記事" in result
        assert markdown_file in result
        assert "markdown-id-123" in result
        
        mock_blog_service.create_post_from_markdown.assert_called_once_with(markdown_file)
    
    def test_create_blog_post_from_markdown_file_not_found(self):
        """存在しないファイルのエラーテスト"""
        result = create_blog_post_from_markdown(path="/nonexistent/file.md")
        
        assert "❌" in result
        assert "ファイルが見つかりません" in result
        assert "/nonexistent/file.md" in result
    
    def test_create_blog_post_from_markdown_invalid_extension(self, tmp_path):
        """非Markdownファイルのエラーテスト"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("テストファイル")
        
        result = create_blog_post_from_markdown(path=str(txt_file))
        
        assert "❌" in result
        assert "Markdownファイル（.md）を指定してください" in result
    
    def test_error_classification_auth_error(self, mock_blog_service):
        """認証エラーの分類テスト"""
        mock_blog_service.create_post.side_effect = Exception("WSSE authentication failed")
        
        with patch('hatena_blog_mcp.service_factory.get_blog_service', return_value=mock_blog_service):
            result = create_blog_post(
                title="テスト記事",
                content="<p>テスト本文</p>"
            )
        
        assert "❌ 認証に失敗しました" in result
        assert "💡 解決方法:" in result
        assert "HATENA_USER_ID" in result
        assert "📋 エラーコード: AUTH_FAILED" in result
    
    def test_error_classification_network_error(self, mock_blog_service):
        """ネットワークエラーの分類テスト"""
        mock_blog_service.create_post.side_effect = Exception("Connection timeout")
        
        with patch('hatena_blog_mcp.service_factory.get_blog_service', return_value=mock_blog_service):
            result = create_blog_post(
                title="テスト記事",
                content="<p>テスト本文</p>"
            )
        
        assert "❌ ネットワーク接続エラーが発生しました" in result
        assert "💡 解決方法:" in result
        assert "インターネット接続を確認" in result
        assert "📋 エラーコード: NETWORK_FAILED" in result
    
    def test_error_classification_rate_limit_error(self, mock_blog_service):
        """API制限エラーの分類テスト"""
        mock_blog_service.create_post.side_effect = Exception("Rate limit exceeded")
        
        with patch('hatena_blog_mcp.service_factory.get_blog_service', return_value=mock_blog_service):
            result = create_blog_post(
                title="テスト記事",
                content="<p>テスト本文</p>"
            )
        
        assert "❌ API呼び出し制限に達しました" in result
        assert "💡 解決方法:" in result
        assert "数分間待ってから再試行" in result
        assert "📋 エラーコード: RATE_LIMITED" in result
    
    @pytest.mark.asyncio
    async def test_service_factory_integration(self):
        """ServiceFactory の統合テスト"""
        from hatena_blog_mcp.service_factory import ServiceFactory, get_service_factory, cleanup_services
        
        # 設定を準備
        with patch.dict(os.environ, {
            'HATENA_USERNAME': 'testuser',
            'HATENA_BLOG_ID': 'testblog',
            'HATENA_API_KEY': 'testkey'
        }):
            factory = ServiceFactory()
            
            # BlogPostService を作成
            service = factory.create_blog_service()
            assert service is not None
            
            # 同じインスタンスが返されることを確認
            service2 = factory.create_blog_service()
            assert service is service2
            
            # クリーンアップ
            await factory.close()
        
        # グローバルファクトリのテスト
        global_factory = get_service_factory()
        assert global_factory is not None
        
        await cleanup_services()
    
    def test_comprehensive_workflow(self, mock_blog_service, markdown_file):
        """包括的なワークフローテスト"""
        with patch('hatena_blog_mcp.service_factory.get_blog_service', return_value=mock_blog_service):
            # 1. 記事作成
            create_result = create_blog_post(
                title="ワークフローテスト",
                content="<p>テスト内容</p>",
                categories=["テスト"]
            )
            assert "✅ 記事を投稿しました!" in create_result
            
            # 2. 記事取得
            get_result = get_blog_post(post_id="test-id-123")
            assert "📄 記事情報:" in get_result
            
            # 3. 記事更新
            update_result = update_blog_post(
                post_id="test-id-123",
                title="更新されたタイトル"
            )
            assert "✅ 記事を更新しました!" in update_result
            
            # 4. 一覧取得
            list_result = list_blog_posts(limit=5)
            assert "📚 ブログ記事一覧" in list_result
            
            # 5. Markdown投稿
            markdown_result = create_blog_post_from_markdown(path=markdown_file)
            assert "✅ Markdownから記事を投稿しました!" in markdown_result
        
        # 各サービスメソッドが呼び出されたことを確認
        mock_blog_service.create_post.assert_called()
        mock_blog_service.get_post.assert_called()
        mock_blog_service.update_post.assert_called()
        mock_blog_service.list_posts.assert_called()
        mock_blog_service.create_post_from_markdown.assert_called()