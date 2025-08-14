"""
Tests for BlogPostService (service layer CRUD).
"""

import pytest
from unittest.mock import Mock, AsyncMock

import httpx

from hatena_blog_mcp.blog_service import BlogPostService
from hatena_blog_mcp.auth import AuthenticationManager
from hatena_blog_mcp.models import AuthConfig
from hatena_blog_mcp.xml_processor import AtomPubProcessor


@pytest.fixture
def auth_manager():
    return AuthenticationManager(AuthConfig(username="test_user", password="mock_api_key_for_tests"))


@pytest.fixture
def xml_processor():
    return AtomPubProcessor()


@pytest.mark.asyncio
async def test_create_post_success(auth_manager, xml_processor):
    # Mock HTTP client
    mock_client = Mock()
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 201
    mock_response.text = (
        """<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom">
            <id>tag:example.com,2024:entry-1</id>
            <title>新規記事</title>
            <content type="text/html">本文</content>
        </entry>"""
    )
    mock_client.post = AsyncMock(return_value=mock_response)

    service = BlogPostService(
        auth_manager=auth_manager,
        username="test_user",
        blog_id="testblog",
        http_client=mock_client,
        xml_processor=xml_processor,
    )

    result = await service.create_post(title="新規記事", content="本文")

    assert result.title == "新規記事"
    assert result.content == "本文"
    mock_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_post_success(auth_manager, xml_processor):
    mock_client = Mock()
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 200
    mock_response.text = (
        """<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom">
            <id>tag:example.com,2024:entry-2</id>
            <title>取得記事</title>
            <content type="text/html">本文2</content>
        </entry>"""
    )
    mock_client.get = AsyncMock(return_value=mock_response)

    service = BlogPostService(
        auth_manager=auth_manager,
        username="test_user",
        blog_id="testblog",
        http_client=mock_client,
        xml_processor=xml_processor,
    )

    post = await service.get_post("entry-2")
    assert post.id == "tag:example.com,2024:entry-2"
    assert post.title == "取得記事"
    mock_client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_post_partial(auth_manager, xml_processor):
    mock_client = Mock()

    # GET current
    current_response = Mock(spec=httpx.Response)
    current_response.status_code = 200
    current_response.text = (
        """<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom">
            <id>tag:example.com,2024:entry-3</id>
            <title>旧タイトル</title>
            <content type="text/html">旧本文</content>
        </entry>"""
    )

    # PUT updated
    updated_response = Mock(spec=httpx.Response)
    updated_response.status_code = 200
    updated_response.text = (
        """<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom">
            <id>tag:example.com,2024:entry-3</id>
            <title>新タイトル</title>
            <content type="text/html">旧本文</content>
        </entry>"""
    )

    mock_client.get = AsyncMock(return_value=current_response)
    mock_client.put = AsyncMock(return_value=updated_response)

    service = BlogPostService(
        auth_manager=auth_manager,
        username="test_user",
        blog_id="testblog",
        http_client=mock_client,
        xml_processor=xml_processor,
    )

    updated = await service.update_post(post_id="entry-3", title="新タイトル")
    assert updated.title == "新タイトル"
    assert updated.content == "旧本文"
    mock_client.get.assert_awaited_once()
    mock_client.put.assert_awaited_once()


@pytest.mark.asyncio
async def test_list_posts_with_limit(auth_manager, xml_processor):
    mock_client = Mock()
    feed_response = Mock(spec=httpx.Response)
    feed_response.status_code = 200
    feed_response.text = (
        """<?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <title>feed</title>
            <entry><title>記事1</title><content type="text/html">a</content></entry>
            <entry><title>記事2</title><content type="text/html">b</content></entry>
            <entry><title>記事3</title><content type="text/html">c</content></entry>
        </feed>"""
    )
    mock_client.get = AsyncMock(return_value=feed_response)

    service = BlogPostService(
        auth_manager=auth_manager,
        username="test_user",
        blog_id="testblog",
        http_client=mock_client,
        xml_processor=xml_processor,
    )

    posts = await service.list_posts(limit=2)
    assert len(posts) == 2
    assert posts[0].title == "記事1"
    assert posts[1].title == "記事2"


@pytest.mark.asyncio
async def test_delete_post_success(auth_manager, xml_processor):
    mock_client = Mock()
    mock_response = Mock(spec=httpx.Response)
    mock_response.status_code = 204
    mock_client.delete = AsyncMock(return_value=mock_response)

    service = BlogPostService(
        auth_manager=auth_manager,
        username="test_user",
        blog_id="testblog",
        http_client=mock_client,
        xml_processor=xml_processor,
    )

    ok = await service.delete_post("entry-9")
    assert ok is True
    mock_client.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_post_missing_content_raises(auth_manager, xml_processor):
    mock_client = Mock()
    # POSTは到達しない想定だが、念のため設定
    mock_client.post = AsyncMock()

    service = BlogPostService(
        auth_manager=auth_manager,
        username="test_user",
        blog_id="testblog",
        http_client=mock_client,
        xml_processor=xml_processor,
    )

    with pytest.raises(ValueError):
        await service.create_post(title="t", content="")
