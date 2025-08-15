"""
Hatena Blog MCP Server using FastMCP for simplified implementation.
"""

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
    
    logger.info(f"Creating blog post: {title}")
    
    try:
        # TODO: 実際のBlogPostServiceとの統合
        # service = get_blog_service()
        # result = await service.create_post(
        #     title=title, 
        #     content=content, 
        #     categories=categories or [],
        #     summary=summary,
        #     draft=draft
        # )
        # return f"記事を投稿しました: {result.url}"
        
        return f"記事投稿予定: {title} (実装予定)"
        
    except Exception as e:
        logger.error(f"Error creating blog post: {e}")
        return f"記事投稿でエラーが発生しました: {str(e)}"


@mcp.tool()
def update_blog_post(
    post_id: Annotated[str, "更新する記事のID"],
    title: Annotated[str, "新しいタイトル"] = None,
    content: Annotated[str, "新しい本文（HTML形式）"] = None,
    categories: Annotated[list[str], "新しいカテゴリリスト"] = None,
    summary: Annotated[str, "新しい要約"] = None,
    draft: Annotated[bool, "下書き状態"] = None,
) -> str:
    """既存の記事を更新します"""
    
    logger.info(f"Updating blog post: {post_id}")
    
    try:
        # TODO: 実際のBlogPostServiceとの統合
        # service = get_blog_service()
        # result = await service.update_post(
        #     post_id=post_id,
        #     title=title,
        #     content=content,
        #     categories=categories,
        #     summary=summary,
        #     draft=draft
        # )
        # return f"記事を更新しました: {result.url}"
        
        return f"記事更新予定: {post_id} (実装予定)"
        
    except Exception as e:
        logger.error(f"Error updating blog post: {e}")
        return f"記事更新でエラーが発生しました: {str(e)}"


@mcp.tool()
def get_blog_post(
    post_id: Annotated[str, "取得する記事のID"],
) -> str:
    """記事の詳細情報を取得します"""
    
    logger.info(f"Getting blog post: {post_id}")
    
    try:
        # TODO: 実際のBlogPostServiceとの統合
        # service = get_blog_service()
        # result = await service.get_post(post_id)
        # return f"タイトル: {result.title}\nURL: {result.url}\nカテゴリ: {', '.join(result.categories)}"
        
        return f"記事取得予定: {post_id} (実装予定)"
        
    except Exception as e:
        logger.error(f"Error getting blog post: {e}")
        return f"記事取得でエラーが発生しました: {str(e)}"


@mcp.tool()
def list_blog_posts(
    limit: Annotated[int, "取得する記事数の上限"] = 10,
) -> str:
    """記事一覧を取得します"""
    
    logger.info(f"Listing blog posts (limit: {limit})")
    
    try:
        # TODO: 実際のBlogPostServiceとの統合
        # service = get_blog_service()
        # posts = await service.list_posts(limit=limit)
        # result = "\n".join([f"- {post.title} ({post.url})" for post in posts])
        # return f"記事一覧:\n{result}"
        
        return f"記事一覧取得予定（上限: {limit}件）(実装予定)"
        
    except Exception as e:
        logger.error(f"Error listing blog posts: {e}")
        return f"記事一覧取得でエラーが発生しました: {str(e)}"


@mcp.tool()
def create_blog_post_from_markdown(
    path: Annotated[str, "Markdownファイルのパス"],
) -> str:
    """Markdownファイルから記事を作成して投稿します"""
    
    logger.info(f"Creating blog post from markdown: {path}")
    
    try:
        # TODO: 実際のBlogPostServiceとの統合
        # service = get_blog_service()
        # result = await service.create_post_from_markdown(path)
        # return f"Markdownから記事を投稿しました: {result.url}"
        
        return f"Markdownから記事投稿予定: {path} (実装予定)"
        
    except Exception as e:
        logger.error(f"Error creating blog post from markdown: {e}")
        return f"Markdown記事投稿でエラーが発生しました: {str(e)}"


def main() -> None:
    """Main entry point for the MCP server"""
    logger.info("Starting Hatena Blog MCP Server with FastMCP")
    mcp.run()


if __name__ == "__main__":
    main()
