"""
Hatena Blog MCP Server using FastMCP for simplified implementation.
"""

import asyncio
import logging
from typing import Annotated, Optional

from mcp.server.fastmcp import FastMCP


def run_async_safely(coro):
    """既存のイベントループを考慮して非同期処理を安全に実行する"""
    try:
        # 既存のイベントループが実行中かチェック
        loop = asyncio.get_running_loop()
        # 実行中の場合は新しいスレッドで実行
        import concurrent.futures
        import threading
        
        result = None
        exception = None
        
        def run_in_thread():
            nonlocal result, exception
            try:
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result = new_loop.run_until_complete(coro)
                finally:
                    new_loop.close()
                    # スレッド終了時にイベントループをクリア
                    asyncio.set_event_loop(None)
            except Exception as e:
                exception = e
        
        thread = threading.Thread(target=run_in_thread)
        thread.start()
        thread.join()
        
        if exception:
            raise exception
        return result
        
    except RuntimeError:
        # イベントループが実行中でない場合は直接実行
        return asyncio.run(coro)

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
async def create_blog_post(
    title: Annotated[str, "記事のタイトル"],
    content: Annotated[str, "記事の本文（HTML形式）"],
    categories: Annotated[Optional[list[str]], "記事のカテゴリリスト"] = None,
) -> str:
    """はてなブログに新しい記事を投稿します"""
    

    
    from hatena_blog_mcp.error_handler import handle_mcp_errors, validate_required_params
    
    @handle_mcp_errors
    async def _create_blog_post():
        logger.info(f"Creating blog post: {title}")

        
        # パラメータ検証
        params = {"title": title, "content": content}
        validation_error = validate_required_params(params, ["title", "content"])
        if validation_error:
            raise ValueError(validation_error)
        
        # サービス層との統合
        from hatena_blog_mcp.service_factory import get_blog_service
        
        service = get_blog_service()

        result = await service.create_post(
            title=title,
            content=content,
            categories=categories or []
        )
        
        draft_status = "📝 下書き" if result.draft else "📢 公開済み"
        return f"✅ 記事を投稿しました!\n📄 タイトル: {result.title}\n🔗 URL: {result.post_url}\n🆔 記事ID: {result.id}\n📅 投稿日時: {result.created_at}\n🔄 ステータス: {draft_status}"
    
    return await _create_blog_post()


@mcp.tool()
async def update_blog_post(
    post_id: Annotated[str, "更新する記事のID"],
    title: Annotated[Optional[str], "新しいタイトル"] = None,
    content: Annotated[Optional[str], "新しい本文（HTML形式）"] = None,
    categories: Annotated[Optional[list[str]], "新しいカテゴリリスト"] = None,
) -> str:
    """既存のブログ記事を更新します"""
    
    from hatena_blog_mcp.error_handler import handle_mcp_errors, validate_required_params
    
    @handle_mcp_errors
    async def _update_blog_post():
        logger.info(f"Updating blog post: {post_id}")
        
        # パラメータ検証
        params = {"post_id": post_id}
        validation_error = validate_required_params(params, ["post_id"])
        if validation_error:
            raise ValueError(validation_error)
        
        # 少なくとも1つの更新項目が必要
        update_fields = [title, content, categories]
        if all(field is None for field in update_fields):
            raise ValueError("更新する項目を少なくとも1つ指定してください。")
        
        from hatena_blog_mcp.service_factory import get_blog_service
        
        service = get_blog_service()

        result = await service.update_post(
            post_id=post_id,
            title=title,
            content=content,
            categories=categories
        )
        
        return f"✅ 記事を更新しました!\n📄 タイトル: {result.title}\n🔗 URL: {result.post_url}\n🆔 記事ID: {result.id}\n📅 更新日時: {result.updated_at}"
    
    return await _update_blog_post()


@mcp.tool()
async def get_blog_post(
    post_id: Annotated[str, "取得する記事のID"],
) -> str:
    """指定したIDのブログ記事を取得します"""
    
    from hatena_blog_mcp.error_handler import handle_mcp_errors, validate_required_params
    
    @handle_mcp_errors
    async def _get_blog_post():
        logger.info(f"Getting blog post: {post_id}")
        
        # パラメータ検証
        params = {"post_id": post_id}
        validation_error = validate_required_params(params, ["post_id"])
        if validation_error:
            raise ValueError(validation_error)
        
        from hatena_blog_mcp.service_factory import get_blog_service
        
        service = get_blog_service()

        result = await service.get_post(post_id)
        
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
    
    return await _get_blog_post()


@mcp.tool()
async def list_blog_posts(
    limit: Annotated[int, "取得する記事数の上限"] = 10,
) -> str:
    """ブログ記事の一覧を取得します"""
    
    from hatena_blog_mcp.error_handler import handle_mcp_errors
    
    @handle_mcp_errors
    async def _list_blog_posts():
        logger.info(f"Listing blog posts (limit: {limit})")
        
        # パラメータ検証
        if limit < 1 or limit > 100:
            raise ValueError("limitは1以上100以下で指定してください。")
        
        from hatena_blog_mcp.service_factory import get_blog_service
        
        service = get_blog_service()

        results = await service.list_posts(limit=limit)
        
        if not results:
            return "📭 記事が見つかりませんでした。"
        
        # 結果を読みやすい形式で返す（コピー&ペースト用に最適化）
        posts_info = [f"📚 ブログ記事一覧 ({len(results)}件):"]
        posts_info.append("")  # 空行
        
        for i, post in enumerate(results, 1):
            categories_str = ", ".join(post.categories) if post.categories else "なし"
            draft_status = "📝" if post.draft else "📢"
            
            # 記事IDから数字部分を抽出（get_blog_postで使いやすくするため）
            if post.id.startswith("tag:blog.hatena.ne.jp"):
                numeric_id = post.id.split("-")[-1]
            else:
                numeric_id = post.id
            
            posts_info.append(f"""{i}. {draft_status} {post.title}
   📋 簡単ID: {numeric_id}
   🆔 完全ID: {post.id}
   📅 投稿日: {post.created_at or "不明"}
   🏷️ カテゴリ: {categories_str}
   🔗 URL: {post.post_url or "取得失敗"}

   👆 get_blog_post に使用: "{numeric_id}" または "{post.id}"
   """)
        
        posts_info.append("💡 使用方法: get_blog_post(post_id=\"簡単ID\") でコピー&ペースト可能")
        return '\n'.join(posts_info)
    
    return await _list_blog_posts()


@mcp.tool()
async def create_blog_post_from_markdown(
    path: Annotated[str, "Markdownファイルのパス"],
) -> str:
    """Markdownファイルから新しいブログ記事を投稿します"""
    
    from hatena_blog_mcp.error_handler import handle_mcp_errors, validate_required_params, validate_file_path
    
    @handle_mcp_errors
    async def _create_blog_post_from_markdown():
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
        
        from hatena_blog_mcp.service_factory import get_blog_service
        
        service = get_blog_service()

        result = await service.create_post_from_markdown(path)
        
        return f"✅ Markdownから記事を投稿しました!\n📄 タイトル: {result.title}\n🔗 URL: {result.post_url}\n🆔 記事ID: {result.id}\n📁 ソースファイル: {path}\n📅 投稿日時: {result.created_at}"
    
    return await _create_blog_post_from_markdown()


@mcp.tool()
async def delete_blog_post(
    post_id: Annotated[str, "削除する記事のID（簡単ID/完全IDどちらも可）"],
) -> str:
    """指定したIDのブログ記事を削除します"""

    from hatena_blog_mcp.error_handler import handle_mcp_errors, validate_required_params

    @handle_mcp_errors
    async def _delete_blog_post():
        logger.info(f"Deleting blog post: {post_id}")

        # パラメータ検証
        params = {"post_id": post_id}
        validation_error = validate_required_params(params, ["post_id"])
        if validation_error:
            raise ValueError(validation_error)

        from hatena_blog_mcp.service_factory import get_blog_service

        service = get_blog_service()

        success = await service.delete_post(post_id)

        if success:
            return f"🗑️ 記事を削除しました!\n🆔 記事ID: {post_id}"
        return f"⚠️ 記事の削除に失敗しました。\n🆔 記事ID: {post_id}"

    return await _delete_blog_post()


async def cleanup_on_exit():
    """サーバー終了時のクリーンアップ処理"""
    from hatena_blog_mcp.service_factory import cleanup_services
    try:
        await cleanup_services()
        logger.info("サービスのクリーンアップが完了しました")
    except Exception as e:
        logger.error(f"クリーンアップ中にエラーが発生: {e}")


def main() -> None:
    """Main entry point for the MCP server"""
    import atexit
    import signal
    
    def signal_handler(signum, frame):
        """シグナルハンドラー"""
        logger.info("サーバー終了シグナルを受信しました")
        try:
            run_async_safely(cleanup_on_exit())
        except Exception as e:
            logger.error(f"終了処理中にエラー: {e}")
    
    # シグナルハンドラーを登録
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Hatena Blog MCP Server with FastMCP")
    
    try:
        mcp.run()
    finally:
        # 正常終了時もクリーンアップ
        try:
            run_async_safely(cleanup_on_exit())
        except Exception as e:
            logger.error(f"終了処理中にエラー: {e}")


if __name__ == "__main__":
    main()
