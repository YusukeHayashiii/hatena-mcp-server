"""
Service layer for Hatena Blog operations.
はてなブログ向けのサービス層（CRUD）を提供します。

Core responsibilities:
- Bridge between domain models and HTTP/XML layers
- Provide simple CRUD methods for blog posts
- Keep error handling straightforward (let callers decide)

Note about Markdown input:
- Core methods take structured arguments or BlogPost fields (HTML content expected)
- A Markdown ingestion helper can be added separately to parse front matter and convert to HTML
"""

from __future__ import annotations

from typing import Optional, List

import httpx

from .auth import AuthenticationManager
from .http_client import HatenaHttpClient
from .models import BlogPost
from .xml_processor import AtomPubProcessor


class BlogPostService:
    """ブログ記事のCRUDを担うサービスクラス"""

    def __init__(
        self,
        *,
        auth_manager: AuthenticationManager,
        username: str,
        blog_id: str,
        http_client: Optional[HatenaHttpClient] = None,
        xml_processor: Optional[AtomPubProcessor] = None,
    ) -> None:
        self._auth_manager = auth_manager
        self._username = username
        self._blog_id = blog_id
        self._xml = xml_processor or AtomPubProcessor()
        self._client_provided = http_client is not None
        self._client = http_client or HatenaHttpClient(
            auth_manager=auth_manager,
            username=username,
            blog_id=blog_id,
        )

    @property
    def xml(self) -> AtomPubProcessor:
        return self._xml

    @property
    def client(self) -> HatenaHttpClient:
        return self._client

    async def close(self) -> None:
        """内部HTTPクライアントをクローズ（外部提供クライアントは触らない）"""
        if not self._client_provided:
            await self._client.close()

    def _extract_numeric_id(self, post_id: str) -> str:
        """はてなブログの記事IDから数字部分を抽出
        
        Args:
            post_id: tag:blog.hatena.ne.jp,2013:blog-username-xxx-6802418398548165121 形式の記事ID
            
        Returns:
            str: 数字部分のみの記事ID（例: 6802418398548165121）
        """
        if post_id.startswith("tag:blog.hatena.ne.jp"):
            # 最後のハイフン以降の数字部分を抽出
            return post_id.split("-")[-1]
        else:
            # 既に数字形式の場合はそのまま使用
            return post_id

    async def create_post(
        self,
        *,
        title: str,
        content: str,
        categories: Optional[List[str]] = None,
        author: Optional[str] = None,
        summary: Optional[str] = None,
        draft: Optional[bool] = None,
    ) -> BlogPost:
        """記事を新規作成します（content は HTML 想定）。

        Raises:
            httpx.HTTPError: 通信またはHTTPエラー
            ValueError: XML生成に必要なフィールド不足
        """
        blog_post = BlogPost(
            title=title,
            content=content,
            categories=categories or [],
            author=author,
            summary=summary,
            draft=draft,
        )
        entry_xml = self.xml.create_entry_xml(blog_post)
        response = await self.client.post("/entry", entry_xml)
        return self.xml.parse_entry_xml(response.text)

    async def update_post(
        self,
        *,
        post_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        categories: Optional[List[str]] = None,
        summary: Optional[str] = None,
        draft: Optional[bool] = None,
        author: Optional[str] = None,
    ) -> BlogPost:
        """既存記事を更新します（部分更新サポート）。

        現在のエントリを取得し、指定フィールドだけを上書きしてPUTします。
        """
        # 1) 現状取得
        current = await self.get_post(post_id)

        # 2) 差分適用
        if title is not None:
            current.title = title
        if content is not None:
            current.content = content
        if categories is not None:
            current.categories = categories
        if summary is not None:
            current.summary = summary
        if draft is not None:
            current.draft = draft
        if author is not None:
            current.author = author

        # 3) AtomPubエントリ生成（ID/リンクがあれば維持）
        entry_xml = self.xml.create_entry_xml(current)

        # 4) 更新リクエスト
        numeric_id = self._extract_numeric_id(post_id)
        path = f"/entry/{numeric_id}"
        response = await self.client.put(path, entry_xml)
        return self.xml.parse_entry_xml(response.text)

    async def get_post(self, post_id: str) -> BlogPost:
        """記事IDで記事詳細を取得します。"""
        numeric_id = self._extract_numeric_id(post_id)
        path = f"/entry/{numeric_id}"
        response = await self.client.get(path)
        return self.xml.parse_entry_xml(response.text)

    async def list_posts(self, limit: int = 10) -> list[BlogPost]:
        """記事一覧を取得します（取得件数はクライアント側でスライス）。"""
        response = await self.client.get("/entry")
        posts = self.xml.parse_feed_xml(response.text)
        if limit is not None and limit > 0:
            return posts[:limit]
        return posts

    async def delete_post(self, post_id: str) -> bool:
        """記事を削除します。成功時 True を返します。"""
        path = f"/entry/{post_id}"
        response = await self.client.delete(path)
        return response.status_code in (200, 202, 204)

    async def create_post_from_markdown(self, markdown_path: str) -> BlogPost:
        """Markdownファイルから記事を作成します。
        
        Args:
            markdown_path: Markdownファイルのパス
            
        Returns:
            作成された記事のBlogPostオブジェクト
            
        Raises:
            FileNotFoundError: ファイルが見つからない場合
            ValueError: Markdown変換に失敗した場合
            httpx.HTTPError: API通信エラー
        """
        from .markdown_importer import MarkdownImporter
        
        try:
            # Markdownファイルを読み込みBlogPostに変換
            importer = MarkdownImporter(enable_front_matter=True)
            blog_post = importer.load_from_file(markdown_path)
            
            # はてなブログに投稿
            return await self.create_post(
                title=blog_post.title,
                content=blog_post.content,
                categories=blog_post.categories,
                summary=blog_post.summary,
                draft=blog_post.draft,
                author=blog_post.author,
            )
            
        except (FileNotFoundError, ValueError) as e:
            # ファイル読み込みやMarkdown変換エラーをDATA_ERRORとして再raise
            raise ValueError(f"Markdown processing failed: {e}")
        except Exception as e:
            # その他のエラーは元の例外をそのまま再raise
            raise
