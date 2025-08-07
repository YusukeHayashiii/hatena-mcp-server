"""
Tests for HTTP Client with WSSE Authentication.
HTTPクライアントとWSSE認証のユニットテストです。
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

import httpx
from lxml import etree

from hatena_blog_mcp.http_client import HatenaHttpClient
from hatena_blog_mcp.auth import AuthenticationManager
from hatena_blog_mcp.models import AuthConfig, BlogPost
from hatena_blog_mcp.rate_limiter import RateLimiter


@pytest.fixture
def auth_config():
    """認証設定のフィクスチャ"""
    return AuthConfig(
        username="testuser",
        password="testkey123"
    )


@pytest.fixture
def auth_manager(auth_config):
    """認証マネージャーのフィクスチャ"""
    return AuthenticationManager(auth_config)


@pytest.fixture
def rate_limiter():
    """レート制限器のフィクスチャ"""
    return RateLimiter(max_requests_per_minute=60)  # テスト用に緩い制限


@pytest.fixture
async def http_client(auth_manager, rate_limiter):
    """HTTPクライアントのフィクスチャ"""
    client = HatenaHttpClient(
        auth_manager=auth_manager,
        username="testuser",
        blog_id="testblog",
        rate_limiter=rate_limiter
    )
    yield client
    await client.close()


class TestHatenaHttpClient:
    """HatenaHttpClientのテストクラス"""

    def test_init(self, auth_manager, rate_limiter):
        """初期化のテスト"""
        client = HatenaHttpClient(
            auth_manager=auth_manager,
            username="testuser",
            blog_id="testblog",
            timeout=15.0,
            max_retries=2,
            rate_limiter=rate_limiter
        )
        
        assert client.username == "testuser"
        assert client.blog_id == "testblog"
        assert client.timeout == 15.0
        assert client.max_retries == 2
        assert client.rate_limiter is rate_limiter
        assert client.atom_base_url == "https://blog.hatena.ne.jp/testuser/testblog/atom"

    def test_build_url(self, http_client):
        """URL構築のテスト"""
        # パスが/で始まる場合
        url = http_client._build_url("/entry")
        assert url == "https://blog.hatena.ne.jp/testuser/testblog/atom/entry"
        
        # パスが/で始まらない場合
        url = http_client._build_url("entry")
        assert url == "https://blog.hatena.ne.jp/testuser/testblog/atom/entry"
        
        # 複雑なパス
        url = http_client._build_url("entry/12345")
        assert url == "https://blog.hatena.ne.jp/testuser/testblog/atom/entry/12345"

    @pytest.mark.asyncio
    async def test_successful_request(self, http_client):
        """成功するリクエストのテスト"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        
        with patch.object(http_client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            response = await http_client._make_request("GET", "https://example.com")
            
            assert response is mock_response
            mock_request.assert_called_once()
            
            # 認証ヘッダーが含まれているかチェック
            call_kwargs = mock_request.call_args[1]
            headers = call_kwargs['headers']
            assert 'X-WSSE' in headers
            assert 'Content-Type' in headers
            assert 'User-Agent' in headers

    @pytest.mark.asyncio
    async def test_retry_on_server_error(self, http_client):
        """サーバーエラー時のリトライテスト"""
        # 最初の2回は500エラー、3回目は成功
        server_error = httpx.HTTPStatusError(
            message="Server Error",
            request=Mock(),
            response=Mock(status_code=500)
        )
        
        success_response = Mock(spec=httpx.Response)
        success_response.status_code = 200
        success_response.raise_for_status.return_value = None
        
        with patch.object(http_client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = [
                Mock(raise_for_status=Mock(side_effect=server_error)),
                Mock(raise_for_status=Mock(side_effect=server_error)),
                success_response
            ]
            
            # レート制限器の acquire メソッドをモック
            with patch.object(http_client.rate_limiter, 'acquire', new_callable=AsyncMock):
                # sleepをモックして高速化
                with patch('asyncio.sleep', new_callable=AsyncMock):
                    response = await http_client._make_request("GET", "https://example.com")
            
            assert response is success_response
            assert mock_request.call_count == 3

    @pytest.mark.asyncio
    async def test_no_retry_on_client_error(self, http_client):
        """クライアントエラー時はリトライしないテスト"""
        client_error = httpx.HTTPStatusError(
            message="Not Found",
            request=Mock(),
            response=Mock(status_code=404)
        )
        
        with patch.object(http_client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = Mock(raise_for_status=Mock(side_effect=client_error))
            
            # レート制限器の acquire メソッドをモック
            with patch.object(http_client.rate_limiter, 'acquire', new_callable=AsyncMock):
                with pytest.raises(httpx.HTTPStatusError):
                    await http_client._make_request("GET", "https://example.com")
            
            # リトライせずに1回だけ呼ばれる
            assert mock_request.call_count == 1

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, http_client):
        """レート制限処理のテスト"""
        rate_limit_error = httpx.HTTPStatusError(
            message="Too Many Requests",
            request=Mock(),
            response=Mock(status_code=429, headers={"Retry-After": "60"})
        )
        
        with patch.object(http_client._client, 'request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = Mock(raise_for_status=Mock(side_effect=rate_limit_error))
            
            # レート制限器の acquire メソッドをモック
            with patch.object(http_client.rate_limiter, 'acquire', new_callable=AsyncMock):
                # handle_response メソッドがレート制限を処理することを確認
                with patch.object(http_client.rate_limiter, 'handle_response') as mock_handle:
                    with pytest.raises(httpx.HTTPStatusError):
                        await http_client._make_request("GET", "https://example.com")
                    
                    # レート制限器のhandle_responseが呼ばれることを確認
                    assert mock_handle.call_count >= 1

    @pytest.mark.asyncio
    async def test_get_request(self, http_client):
        """GETリクエストのテスト"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        
        with patch.object(http_client, '_make_request', new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response
            
            response = await http_client.get("/entry", params={"page": 1})
            
            assert response is mock_response
            mock_make.assert_called_once_with(
                "GET",
                "https://blog.hatena.ne.jp/testuser/testblog/atom/entry",
                params={"page": 1},
                headers=None
            )

    @pytest.mark.asyncio
    async def test_post_request_with_xml_element(self, http_client):
        """XMLエレメントを使ったPOSTリクエストのテスト"""
        # テスト用XMLエレメント作成
        entry = etree.Element("entry")
        title = etree.SubElement(entry, "title")
        title.text = "Test Entry"
        
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 201
        
        with patch.object(http_client, '_make_request', new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response
            
            response = await http_client.post("/entry", entry)
            
            assert response is mock_response
            
            # XMLがバイト列に変換されて送信されることを確認
            call_args = mock_make.call_args
            assert call_args[0][0] == "POST"
            assert call_args[0][1] == "https://blog.hatena.ne.jp/testuser/testblog/atom/entry"
            
            # contentがバイト列であることを確認
            content = call_args[1]['content']
            assert isinstance(content, bytes)
            assert b"Test Entry" in content

    @pytest.mark.asyncio
    async def test_post_request_with_string(self, http_client):
        """文字列を使ったPOSTリクエストのテスト"""
        xml_string = '<?xml version="1.0"?><entry><title>Test</title></entry>'
        
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 201
        
        with patch.object(http_client, '_make_request', new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response
            
            response = await http_client.post("/entry", xml_string)
            
            assert response is mock_response
            
            # 文字列がバイト列に変換されて送信されることを確認
            call_args = mock_make.call_args
            content = call_args[1]['content']
            assert isinstance(content, bytes)
            assert content == xml_string.encode('utf-8')

    @pytest.mark.asyncio
    async def test_put_request(self, http_client):
        """PUTリクエストのテスト"""
        xml_bytes = b'<?xml version="1.0"?><entry><title>Updated</title></entry>'
        
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        
        with patch.object(http_client, '_make_request', new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response
            
            response = await http_client.put("/entry/123", xml_bytes)
            
            assert response is mock_response
            mock_make.assert_called_once_with(
                "PUT",
                "https://blog.hatena.ne.jp/testuser/testblog/atom/entry/123",
                content=xml_bytes,
                headers=None
            )

    @pytest.mark.asyncio
    async def test_delete_request(self, http_client):
        """DELETEリクエストのテスト"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 204
        
        with patch.object(http_client, '_make_request', new_callable=AsyncMock) as mock_make:
            mock_make.return_value = mock_response
            
            response = await http_client.delete("/entry/123")
            
            assert response is mock_response
            mock_make.assert_called_once_with(
                "DELETE",
                "https://blog.hatena.ne.jp/testuser/testblog/atom/entry/123",
                headers=None
            )

    def test_create_network_error(self, http_client):
        """ネットワークエラー作成のテスト"""
        original_error = httpx.ConnectError("Connection failed")
        
        error_info = http_client.create_network_error(
            "ネットワーク接続に失敗しました",
            original_error
        )
        
        assert error_info.error_type.name == "NETWORK_ERROR"
        assert error_info.message == "ネットワーク接続に失敗しました"
        assert error_info.details["original_error"] == "Connection failed"
        assert error_info.details["error_type"] == "ConnectError"

    @pytest.mark.asyncio
    async def test_context_manager(self, auth_manager):
        """コンテキストマネージャーのテスト"""
        async with HatenaHttpClient(
            auth_manager=auth_manager,
            username="testuser",
            blog_id="testblog"
        ) as client:
            assert client is not None
            assert client._client is not None
        
        # コンテキスト終了後はクライアントが閉じられている
        # （実際のクローズ状態の確認は実装依存）

    @pytest.mark.asyncio
    async def test_custom_base_url(self, auth_manager):
        """カスタムベースURLのテスト"""
        custom_url = "https://test.example.com"
        
        async with HatenaHttpClient(
            auth_manager=auth_manager,
            username="testuser",
            blog_id="testblog",
            base_url=custom_url
        ) as client:
            assert client.base_url == custom_url
            assert client.atom_base_url == f"{custom_url}/testuser/testblog/atom"