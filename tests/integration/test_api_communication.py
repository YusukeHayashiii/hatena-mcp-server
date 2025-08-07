"""
Integration tests for API Communication Infrastructure.
API通信基盤の統合テストです。
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timezone

import httpx

from hatena_blog_mcp.auth import AuthenticationManager
from hatena_blog_mcp.http_client import HatenaHttpClient
from hatena_blog_mcp.xml_processor import AtomPubProcessor
from hatena_blog_mcp.rate_limiter import RateLimiter
from hatena_blog_mcp.models import AuthConfig, BlogPost


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
def xml_processor():
    """XML処理器のフィクスチャ"""
    return AtomPubProcessor()


@pytest.fixture
def sample_blog_post():
    """サンプルブログ記事のフィクスチャ"""
    return BlogPost(
        title="統合テスト記事",
        content="<p>これは統合テストの記事です。</p>",
        author="testuser",
        summary="統合テスト用の記事",
        categories=["テスト", "統合"],
        published=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        draft=False
    )


class TestApiCommunicationIntegration:
    """API通信基盤の統合テストクラス"""

    @pytest.mark.asyncio
    async def test_end_to_end_blog_post_creation(self, auth_manager, xml_processor, sample_blog_post):
        """エンドツーエンドのブログ記事作成フローのテスト"""
        
        # 1. BlogPost -> XML変換
        entry_xml = xml_processor.create_entry_xml(sample_blog_post)
        xml_string = xml_processor.to_xml_string(entry_xml)
        
        # XMLの内容を検証
        assert "統合テスト記事" in xml_string
        assert "これは統合テストの記事です" in xml_string
        assert "testuser" in xml_string
        
        # 2. HTTPクライアントでのPOSTリクエストシミュレート
        async with HatenaHttpClient(
            auth_manager=auth_manager,
            username="testuser",
            blog_id="testblog"
        ) as client:
            
            # レスポンスをモック
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 201
            mock_response.text = """<?xml version="1.0" encoding="utf-8"?>
            <entry xmlns="http://www.w3.org/2005/Atom">
                <id>tag:example.com,2024:entry-123</id>
                <title>統合テスト記事</title>
                <content type="text/html">&lt;p&gt;これは統合テストの記事です。&lt;/p&gt;</content>
                <author><name>testuser</name></author>
                <published>2024-01-01T12:00:00Z</published>
                <updated>2024-01-01T12:00:00Z</updated>
                <link rel="edit" href="https://blog.hatena.ne.jp/testuser/testblog/atom/entry/123" />
                <link rel="alternate" type="text/html" href="https://testuser.hatenablog.com/entry/2024/01/01/120000" />
            </entry>"""
            
            with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                # POSTリクエスト実行
                response = await client.post("/entry", entry_xml)
                
                # リクエストが正しく呼ばれたことを確認
                assert response.status_code == 201
                
                # 呼び出し確認（XMLフォーマットの違いは無視）
                mock_request.assert_called_once()
                call_args = mock_request.call_args
                assert call_args[0][0] == "POST"
                assert call_args[0][1] == "https://blog.hatena.ne.jp/testuser/testblog/atom/entry"
                assert call_args[1]['headers'] is None
                
                # XMLコンテンツの基本確認
                content = call_args[1]['content']
                assert isinstance(content, bytes)
                assert "統合テスト記事".encode('utf-8') in content
        
        # 3. レスポンスXMLの解析
        response_post = xml_processor.parse_entry_xml(mock_response.text)
        
        # 解析結果の検証
        assert response_post.id == "tag:example.com,2024:entry-123"
        assert response_post.title == "統合テスト記事"
        assert response_post.author == "testuser"
        assert "blog.hatena.ne.jp" in response_post.edit_url
        assert "hatenablog.com" in response_post.alternate_url

    @pytest.mark.asyncio
    async def test_authentication_integration(self, auth_manager):
        """認証統合のテスト"""
        async with HatenaHttpClient(
            auth_manager=auth_manager,
            username="testuser",
            blog_id="testblog"
        ) as client:
            
            # 認証ヘッダーが正しく生成されることを確認
            auth_headers = auth_manager.get_auth_headers()
            
            assert "X-WSSE" in auth_headers
            assert "Content-Type" in auth_headers
            assert "User-Agent" in auth_headers
            
            # WSSEヘッダーの形式確認
            wsse_header = auth_headers["X-WSSE"]
            assert "UsernameToken" in wsse_header
            assert "Username=" in wsse_header
            assert "PasswordDigest=" in wsse_header
            assert "Nonce=" in wsse_header
            assert "Created=" in wsse_header
            assert "testuser" in wsse_header

    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, auth_manager):
        """レート制限統合のテスト"""
        rate_limiter = RateLimiter(
            max_requests_per_minute=2,  # 厳しい制限でテスト
            max_concurrent_requests=1,
            base_delay=0.01  # テスト用に短い遅延
        )
        
        async with HatenaHttpClient(
            auth_manager=auth_manager,
            username="testuser",
            blog_id="testblog",
            rate_limiter=rate_limiter
        ) as client:
            
            # モックレスポンスの準備
            success_response = Mock(spec=httpx.Response)
            success_response.status_code = 200
            success_response.raise_for_status.return_value = None
            
            with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = success_response
                
                # 複数のリクエストを実行
                responses = []
                for i in range(3):
                    response = await client.get(f"/entry/{i}")
                    responses.append(response)
                
                # すべてのリクエストが成功することを確認
                assert len(responses) == 3
                assert all(r.status_code == 200 for r in responses)
                
                # レート制限器の状態確認
                status = rate_limiter.get_status()
                assert status["current_requests"] == 3

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, auth_manager, xml_processor):
        """エラーハンドリング統合のテスト"""
        async with HatenaHttpClient(
            auth_manager=auth_manager,
            username="testuser",
            blog_id="testblog",
            max_retries=1
        ) as client:
            
            # サーバーエラーのシミュレート
            server_error = httpx.HTTPStatusError(
                message="Internal Server Error",
                request=Mock(),
                response=Mock(status_code=500)
            )
            
            # 最初はエラー、次は成功
            success_response = Mock(spec=httpx.Response)
            success_response.status_code = 200
            success_response.raise_for_status.return_value = None
            
            with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
                mock_request.side_effect = [
                    Mock(raise_for_status=Mock(side_effect=server_error)),
                    success_response
                ]
                
                # レート制限器の acquire をモック
                with patch.object(client.rate_limiter, 'acquire', new_callable=AsyncMock):
                    # sleepをモックして高速化
                    with patch('asyncio.sleep', new_callable=AsyncMock):
                        response = await client.get("/entry")
                
                # リトライ後に成功することを確認
                assert response.status_code == 200
                assert mock_request.call_count == 2

    @pytest.mark.asyncio
    async def test_xml_round_trip_with_http_client(self, auth_manager, xml_processor, sample_blog_post):
        """XMLとHTTPクライアントの往復変換テスト"""
        async with HatenaHttpClient(
            auth_manager=auth_manager,
            username="testuser",
            blog_id="testblog"
        ) as client:
            
            # 1. BlogPost -> XML -> HTTPリクエスト
            entry_xml = xml_processor.create_entry_xml(sample_blog_post)
            
            # XMLがlxml Elementであることを確認
            assert hasattr(entry_xml, 'tag')
            assert "entry" in entry_xml.tag
            
            # 2. HTTPクライアントでのXML送信（POST）
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 201
            
            with patch.object(client, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_response
                
                # XMLエレメントを直接送信
                response = await client.post("/entry", entry_xml)
                
                # リクエストが正しく処理されることを確認
                assert response.status_code == 201
                
                # コンテンツがバイト列に変換されていることを確認
                call_args = mock_request.call_args
                content = call_args[1]['content']
                assert isinstance(content, bytes)
                assert b"<?xml version=" in content
                assert "統合テスト記事".encode('utf-8') in content

    @pytest.mark.asyncio
    async def test_concurrent_requests_with_rate_limiting(self, auth_manager):
        """並行リクエストとレート制限のテスト"""
        import asyncio
        
        rate_limiter = RateLimiter(
            max_requests_per_minute=10,
            max_concurrent_requests=2,
            base_delay=0.01
        )
        
        async with HatenaHttpClient(
            auth_manager=auth_manager,
            username="testuser",
            blog_id="testblog",
            rate_limiter=rate_limiter
        ) as client:
            
            success_response = Mock(spec=httpx.Response)
            success_response.status_code = 200
            success_response.raise_for_status.return_value = None
            
            with patch.object(client._client, 'request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = success_response
                
                # 複数の並行リクエストを実行
                async def make_request(i):
                    return await client.get(f"/entry/{i}")
                
                tasks = [make_request(i) for i in range(5)]
                responses = await asyncio.gather(*tasks)
                
                # すべてのリクエストが成功することを確認
                assert len(responses) == 5
                assert all(r.status_code == 200 for r in responses)
                
                # リクエストが実際に送信されたことを確認
                assert mock_request.call_count == 5

    def test_xml_processor_validation(self, xml_processor):
        """XML処理器の検証機能テスト"""
        # 有効なXML
        valid_xml = """<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom">
            <title>有効なタイトル</title>
            <content>有効な内容</content>
        </entry>"""
        
        assert xml_processor.validate_xml(valid_xml) is True
        
        # 無効なXML
        invalid_xml = "<entry><title>不正なXML</entry>"
        assert xml_processor.validate_xml(invalid_xml) is False
        
        # XMLエラー情報の作成
        error_info = xml_processor.create_xml_error("テストエラー")
        assert error_info.error_type.name == "DATA_ERROR"
        assert error_info.message == "テストエラー"

    def test_rate_limiter_status_reporting(self):
        """レート制限器の状態レポート機能テスト"""
        rate_limiter = RateLimiter(max_requests_per_minute=5)
        
        # 初期状態
        status = rate_limiter.get_status()
        assert status["current_requests"] == 0
        assert status["remaining_requests"] == 5
        assert status["temporary_limit_active"] is False
        
        # リクエストを記録
        rate_limiter._record_request()
        rate_limiter._record_request()
        
        status = rate_limiter.get_status()
        assert status["current_requests"] == 2
        assert status["remaining_requests"] == 3