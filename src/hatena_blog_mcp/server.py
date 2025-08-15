"""
Hatena Blog MCP Server using FastMCP for simplified implementation.
"""

import asyncio
import logging
from typing import Annotated

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hatena-mcp-server")

# Create FastMCP server
mcp = FastMCP("hatena-blog-mcp")


@mcp.tool()
def hello_world(
    name: Annotated[str, "Name to say hello to"] = "World"
) -> str:
    """A simple hello world tool for testing MCP server connectivity"""

    logger.info(f"Hello world tool called with name: {name}")

    try:
        response_text = f"Hello, {name}! This is the Hatena Blog MCP Server."
        return response_text
    except Exception as e:
        logger.error(f"Error in hello_world tool: {e}")
        return f"エラーが発生しました: {str(e)}"

@mcp.tool()
def create_blog_post(
    title: Annotated[str, "記事のタイトル"],
    content: Annotated[str, "記事の本文（HTML形式）"],
    categories: Annotated[list[str], "記事のカテゴリリスト"] = None,
    summary: Annotated[str, "記事の要約"] = None,
    draft: Annotated[bool, "下書き状態"] = False,
) -> str:
    """はてなブログに新しい記事を投稿します"""
    
    from .error_handler import handle_mcp_errors, validate_required_params
    
    @handle_mcp_errors
    def _create_blog_post():
        logger.info(f"Creating blog post: {title}")
        
        # パラメータ検証
        params = {"title": title, "content": content}
        validation_error = validate_required_params(params, ["title", "content"])
        if validation_error:
            raise ValueError(validation_error)
        
        # サービス層との統合
        from .service_factory import get_blog_service
        
        service = get_blog_service()
        
        # asyncio.run を使って非同期処理を実行
        result = asyncio.run(service.create_post(
            title=title, 
            content=content, 
            categories=categories or [],
            summary=summary,
            draft=draft
        ))
        
        return f"✅ 記事を投稿しました!\n📄 タイトル: {result.title}\n🔗 URL: {result.post_url}\n🆔 記事ID: {result.id}\n📅 投稿日時: {result.created_at}"
    
    return _create_blog_post()


@mcp.tool()
def update_blog_post(
    post_id: Annotated[str, "更新する記事のID"],
    title: Annotated[str, "新しいタイトル"] = None,
    content: Annotated[str, "新しい本文（HTML形式）"] = None,
    categories: Annotated[list[str], "新しいカテゴリリスト"] = None,
    summary: Annotated[str, "新しい要約"] = None,
    draft: Annotated[bool, "下書き状態"] = None,
) -> str:
    """既存のブログ記事を更新します"""
    
    from .error_handler import handle_mcp_errors, validate_required_params
    
    @handle_mcp_errors
    def _update_blog_post():
        logger.info(f"Updating blog post: {post_id}")
        
        # パラメータ検証
        params = {"post_id": post_id}
        validation_error = validate_required_params(params, ["post_id"])
        if validation_error:
            raise ValueError(validation_error)
        
        # 少なくとも1つの更新項目が必要
        update_fields = [title, content, categories, summary, draft]
        if all(field is None for field in update_fields):
            raise ValueError("更新する項目を少なくとも1つ指定してください。")
        
        from .service_factory import get_blog_service
        
        service = get_blog_service()
        
        result = asyncio.run(service.update_post(
            post_id=post_id,
            title=title,
            content=content,
            categories=categories,
            summary=summary,
            draft=draft
        ))
        
        return f"✅ 記事を更新しました!\n📄 タイトル: {result.title}\n🔗 URL: {result.post_url}\n🆔 記事ID: {result.id}\n📅 更新日時: {result.updated_at}"
    
    return _update_blog_post()


@mcp.tool()
def get_blog_post(
    post_id: Annotated[str, "取得する記事のID"],
) -> str:
    """指定したIDのブログ記事を取得します"""
    
    from .error_handler import handle_mcp_errors, validate_required_params
    
    @handle_mcp_errors
    def _get_blog_post():
        logger.info(f"Getting blog post: {post_id}")
        
        # パラメータ検証
        params = {"post_id": post_id}
        validation_error = validate_required_params(params, ["post_id"])
        if validation_error:
            raise ValueError(validation_error)
        
        from .service_factory import get_blog_service
        
        service = get_blog_service()
        
        result = asyncio.run(service.get_post(post_id))
        
        # 結果を読みやすい形式で返す
        categories_str = ", ".join(result.categories) if result.categories else "なし"
        draft_status = "📝 下書き" if result.draft else "📢 公開済み"
        
        content_preview = result.content[:300] + "..." if len(result.content) > 300 else result.content
        
        return f"""📄 記事情報:
🏷️ タイトル: {result.title}
🆔 記事ID: {result.id}
🔗 URL: {result.post_url}
📅 投稿日: {result.created_at}
📝 更新日: {result.updated_at}
🏷️ カテゴリ: {categories_str}
🔄 ステータス: {draft_status}

📖 本文プレビュー:
{content_preview}"""
    
    return _get_blog_post()


@mcp.tool()
def list_blog_posts(
    limit: Annotated[int, "取得する記事数の上限"] = 10,
) -> str:
    """ブログ記事の一覧を取得します"""
    
    from .error_handler import handle_mcp_errors
    
    @handle_mcp_errors
    def _list_blog_posts():
        logger.info(f"Listing blog posts (limit: {limit})")
        
        # パラメータ検証
        if limit < 1 or limit > 100:
            raise ValueError("limitは1以上100以下で指定してください。")
        
        from .service_factory import get_blog_service
        
        service = get_blog_service()
        
        results = asyncio.run(service.list_posts(limit=limit))
        
        if not results:
            return "📭 記事が見つかりませんでした。"
        
        # 結果を読みやすい形式で返す
        posts_info = [f"📚 ブログ記事一覧 ({len(results)}件):"]
        
        for i, post in enumerate(results, 1):
            categories_str = ", ".join(post.categories) if post.categories else "なし"
            draft_status = "📝" if post.draft else "📢"
            
            posts_info.append(f"""
{i}. {draft_status} {post.title}
   🆔 ID: {post.id}
   📅 投稿日: {post.created_at}
   🏷️ カテゴリ: {categories_str}
   🔗 URL: {post.post_url}""")
        
        return '\n'.join(posts_info)
    
    return _list_blog_posts()


@mcp.tool()
def create_blog_post_from_markdown(
    path: Annotated[str, "Markdownファイルのパス"],
) -> str:
    """Markdownファイルから新しいブログ記事を投稿します"""
    
    from .error_handler import handle_mcp_errors, validate_required_params, validate_file_path
    
    @handle_mcp_errors
    def _create_blog_post_from_markdown():
        logger.info(f"Creating blog post from markdown: {path}")
        
        # パラメータ検証
        params = {"path": path}
        validation_error = validate_required_params(params, ["path"])
        if validation_error:
            raise ValueError(validation_error)
        
        # ファイルパス検証
        file_validation_error = validate_file_path(path)
        if file_validation_error:
            raise ValueError(file_validation_error)
        
        from .service_factory import get_blog_service
        
        service = get_blog_service()
        
        result = asyncio.run(service.create_post_from_markdown(path))
        
        return f"✅ Markdownから記事を投稿しました!\n📄 タイトル: {result.title}\n🔗 URL: {result.post_url}\n🆔 記事ID: {result.id}\n📁 ソースファイル: {path}\n📅 投稿日時: {result.created_at}"
    
    return _create_blog_post_from_markdown()


def main() -> None:
    """Main entry point for the MCP server"""
    logger.info("Starting Hatena Blog MCP Server with FastMCP")
    mcp.run()


if __name__ == "__main__":
    main()
