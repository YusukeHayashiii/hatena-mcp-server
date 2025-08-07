"""
Tests for AtomPub XML Processing.
AtomPub XML処理機能のユニットテストです。
"""

import pytest
from datetime import datetime, timezone
from lxml import etree

from hatena_blog_mcp.xml_processor import AtomPubProcessor
from hatena_blog_mcp.models import BlogPost, ErrorType


@pytest.fixture
def processor():
    """AtomPubプロセッサーのフィクスチャ"""
    return AtomPubProcessor()


@pytest.fixture
def sample_blog_post():
    """サンプルブログ記事のフィクスチャ"""
    return BlogPost(
        title="テストブログ記事",
        content="<p>これはテスト記事です。</p>",
        author="testuser",
        summary="テスト記事の概要",
        categories=["テスト", "プログラミング"],
        published=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        updated=datetime(2024, 1, 2, 15, 30, 0, tzinfo=timezone.utc),
        draft=False
    )


class TestAtomPubProcessor:
    """AtomPubProcessorのテストクラス"""

    def test_init(self, processor):
        """初期化のテスト"""
        assert processor.ATOM_NS == "http://www.w3.org/2005/Atom"
        assert processor.HATENA_NS == "http://www.hatena.ne.jp/info/xmlns#"
        assert processor.E is not None
        assert processor.H is not None

    def test_create_entry_xml_basic(self, processor, sample_blog_post):
        """基本的なエントリXML生成のテスト"""
        entry = processor.create_entry_xml(sample_blog_post)
        
        # XML要素の存在確認
        assert entry.tag == f"{{{processor.ATOM_NS}}}entry"
        
        # 名前空間設定
        ns = {'atom': processor.ATOM_NS, 'hatena': processor.HATENA_NS}
        
        # タイトル
        title = entry.find('.//atom:title', ns)
        assert title is not None
        assert title.text == "テストブログ記事"
        
        # コンテンツ
        content = entry.find('.//atom:content', ns)
        assert content is not None
        assert content.text == "<p>これはテスト記事です。</p>"
        assert content.get('type') == "text/html"
        
        # 作成者
        author = entry.find('.//atom:author/atom:name', ns)
        assert author is not None
        assert author.text == "testuser"
        
        # 概要
        summary = entry.find('.//atom:summary', ns)
        assert summary is not None
        assert summary.text == "テスト記事の概要"
        
        # カテゴリ
        categories = entry.findall('.//atom:category', ns)
        assert len(categories) == 2
        terms = [cat.get('term') for cat in categories]
        assert "テスト" in terms
        assert "プログラミング" in terms
        
        # 公開日時
        published = entry.find('.//atom:published', ns)
        assert published is not None
        assert "2024-01-01T12:00:00" in published.text
        
        # 更新日時
        updated = entry.find('.//atom:updated', ns)
        assert updated is not None
        assert "2024-01-02T15:30:00" in updated.text
        
        # 下書きフラグ
        draft = entry.find('.//hatena:draft', ns)
        assert draft is not None
        assert draft.text == "no"

    def test_create_entry_xml_minimal(self, processor):
        """最小限のエントリXML生成のテスト"""
        minimal_post = BlogPost(
            title="最小記事",
            content="最小内容"
        )
        
        entry = processor.create_entry_xml(minimal_post)
        
        ns = {'atom': processor.ATOM_NS, 'hatena': processor.HATENA_NS}
        
        # 必須要素の確認
        title = entry.find('.//atom:title', ns)
        assert title.text == "最小記事"
        
        content = entry.find('.//atom:content', ns)
        assert content.text == "最小内容"
        
        # 更新日時は自動で設定される
        updated = entry.find('.//atom:updated', ns)
        assert updated is not None

    def test_create_entry_xml_draft(self, processor):
        """下書き記事のXML生成テスト"""
        draft_post = BlogPost(
            title="下書き記事",
            content="下書き内容",
            draft=True
        )
        
        entry = processor.create_entry_xml(draft_post)
        
        ns = {'atom': processor.ATOM_NS, 'hatena': processor.HATENA_NS}
        draft = entry.find('.//hatena:draft', ns)
        assert draft is not None
        assert draft.text == "yes"

    def test_create_entry_xml_with_urls(self, processor):
        """URL情報付きエントリXML生成のテスト"""
        post_with_urls = BlogPost(
            title="URL付き記事",
            content="内容",
            id="tag:example.com,2024:entry-123",
            edit_url="https://blog.hatena.ne.jp/user/blog/atom/entry/123",
            self_url="https://blog.hatena.ne.jp/user/blog/atom/entry/123",
            alternate_url="https://user.hatenablog.com/entry/2024/01/01/120000"
        )
        
        entry = processor.create_entry_xml(post_with_urls)
        
        ns = {'atom': processor.ATOM_NS}
        
        # ID
        id_elem = entry.find('.//atom:id', ns)
        assert id_elem is not None
        assert id_elem.text == "tag:example.com,2024:entry-123"
        
        # リンク
        links = entry.findall('.//atom:link', ns)
        assert len(links) >= 3
        
        link_map = {link.get('rel'): link.get('href') for link in links}
        assert link_map.get('edit') == "https://blog.hatena.ne.jp/user/blog/atom/entry/123"
        assert link_map.get('self') == "https://blog.hatena.ne.jp/user/blog/atom/entry/123"
        assert link_map.get('alternate') == "https://user.hatenablog.com/entry/2024/01/01/120000"

    def test_create_entry_xml_missing_title(self, processor):
        """タイトル未設定時のエラーテスト"""
        post_without_title = BlogPost(
            title="",  # 空のタイトル
            content="内容"
        )
        
        with pytest.raises(ValueError, match="記事タイトルが必要です"):
            processor.create_entry_xml(post_without_title)

    def test_create_entry_xml_missing_content(self, processor):
        """内容未設定時のエラーテスト"""
        post_without_content = BlogPost(
            title="タイトル",
            content=""  # 空の内容
        )
        
        with pytest.raises(ValueError, match="記事内容が必要です"):
            processor.create_entry_xml(post_without_content)

    def test_parse_entry_xml_basic(self, processor):
        """基本的なエントリXML解析のテスト"""
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom" xmlns:hatena="http://www.hatena.ne.jp/info/xmlns#">
            <id>tag:example.com,2024:entry-123</id>
            <title>解析テスト記事</title>
            <content type="text/html">&lt;p&gt;解析テスト内容&lt;/p&gt;</content>
            <author>
                <name>testuser</name>
            </author>
            <summary>テスト概要</summary>
            <category term="テスト" />
            <category term="XML" />
            <published>2024-01-01T12:00:00Z</published>
            <updated>2024-01-02T15:30:00Z</updated>
            <hatena:draft>no</hatena:draft>
            <link rel="edit" href="https://blog.hatena.ne.jp/user/blog/atom/entry/123" />
            <link rel="self" href="https://blog.hatena.ne.jp/user/blog/atom/entry/123" />
            <link rel="alternate" type="text/html" href="https://user.hatenablog.com/entry/2024/01/01/120000" />
        </entry>'''
        
        blog_post = processor.parse_entry_xml(xml_content)
        
        assert blog_post.id == "tag:example.com,2024:entry-123"
        assert blog_post.title == "解析テスト記事"
        assert blog_post.content == "<p>解析テスト内容</p>"
        assert blog_post.author == "testuser"
        assert blog_post.summary == "テスト概要"
        assert blog_post.categories == ["テスト", "XML"]
        assert blog_post.published.year == 2024
        assert blog_post.published.month == 1
        assert blog_post.published.day == 1
        assert blog_post.updated.year == 2024
        assert blog_post.updated.month == 1
        assert blog_post.updated.day == 2
        assert blog_post.draft is False
        assert blog_post.edit_url == "https://blog.hatena.ne.jp/user/blog/atom/entry/123"
        assert blog_post.self_url == "https://blog.hatena.ne.jp/user/blog/atom/entry/123"
        assert blog_post.alternate_url == "https://user.hatenablog.com/entry/2024/01/01/120000"

    def test_parse_entry_xml_minimal(self, processor):
        """最小限のエントリXML解析のテスト"""
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom">
            <title>最小記事</title>
            <content type="text/html">最小内容</content>
        </entry>'''
        
        blog_post = processor.parse_entry_xml(xml_content)
        
        assert blog_post.title == "最小記事"
        assert blog_post.content == "最小内容"
        assert blog_post.id is None
        assert blog_post.author is None
        assert blog_post.categories == []

    def test_parse_entry_xml_draft(self, processor):
        """下書き記事XML解析のテスト"""
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom" xmlns:hatena="http://www.hatena.ne.jp/info/xmlns#">
            <title>下書き記事</title>
            <content type="text/html">下書き内容</content>
            <hatena:draft>yes</hatena:draft>
        </entry>'''
        
        blog_post = processor.parse_entry_xml(xml_content)
        
        assert blog_post.title == "下書き記事"
        assert blog_post.draft is True

    def test_parse_entry_xml_element(self, processor):
        """XMLエレメントからの解析テスト"""
        entry = etree.Element("{http://www.w3.org/2005/Atom}entry")
        entry.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation", "http://www.w3.org/2005/Atom")
        
        title = etree.SubElement(entry, "{http://www.w3.org/2005/Atom}title")
        title.text = "エレメント記事"
        
        content = etree.SubElement(entry, "{http://www.w3.org/2005/Atom}content")
        content.set("type", "text/html")
        content.text = "エレメント内容"
        
        blog_post = processor.parse_entry_xml(entry)
        
        assert blog_post.title == "エレメント記事"
        assert blog_post.content == "エレメント内容"

    def test_parse_entry_xml_missing_title(self, processor):
        """タイトル要素がないXMLの解析エラーテスト"""
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom">
            <content type="text/html">内容のみ</content>
        </entry>'''
        
        with pytest.raises(ValueError, match="タイトル要素が見つかりません"):
            processor.parse_entry_xml(xml_content)

    def test_parse_entry_xml_missing_content(self, processor):
        """コンテンツ要素がないXMLの解析エラーテスト"""
        xml_content = '''<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom">
            <title>タイトルのみ</title>
        </entry>'''
        
        with pytest.raises(ValueError, match="コンテンツ要素が見つかりません"):
            processor.parse_entry_xml(xml_content)

    def test_parse_entry_xml_invalid_xml(self, processor):
        """不正なXMLの解析エラーテスト"""
        invalid_xml = "<entry><title>不正XML</entry>"  # 閉じタグが不正
        
        with pytest.raises(etree.XMLSyntaxError):
            processor.parse_entry_xml(invalid_xml)

    def test_parse_feed_xml(self, processor):
        """フィードXML解析のテスト"""
        feed_xml = '''<?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <title>テストフィード</title>
            <entry>
                <title>記事1</title>
                <content type="text/html">内容1</content>
            </entry>
            <entry>
                <title>記事2</title>
                <content type="text/html">内容2</content>
            </entry>
        </feed>'''
        
        blog_posts = processor.parse_feed_xml(feed_xml)
        
        assert len(blog_posts) == 2
        assert blog_posts[0].title == "記事1"
        assert blog_posts[0].content == "内容1"
        assert blog_posts[1].title == "記事2"
        assert blog_posts[1].content == "内容2"

    def test_parse_feed_xml_with_invalid_entry(self, processor):
        """一部不正なエントリを含むフィードXML解析のテスト"""
        feed_xml = '''<?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
            <title>テストフィード</title>
            <entry>
                <title>正常記事</title>
                <content type="text/html">正常内容</content>
            </entry>
            <entry>
                <!-- タイトルがない不正なエントリ -->
                <content type="text/html">内容のみ</content>
            </entry>
        </feed>'''
        
        blog_posts = processor.parse_feed_xml(feed_xml)
        
        # 正常なエントリのみが解析される
        assert len(blog_posts) == 1
        assert blog_posts[0].title == "正常記事"

    def test_to_xml_string(self, processor, sample_blog_post):
        """XML文字列変換のテスト"""
        entry = processor.create_entry_xml(sample_blog_post)
        xml_string = processor.to_xml_string(entry)
        
        assert '<?xml version=' in xml_string
        assert 'テストブログ記事' in xml_string
        assert 'これはテスト記事です' in xml_string
        
        # pretty_print=Falseのテスト
        compact_xml = processor.to_xml_string(entry, pretty_print=False)
        assert '\n' not in compact_xml.split('?>')[1]  # XML宣言以降に改行がない

    def test_validate_xml_valid(self, processor):
        """有効なXMLの検証テスト"""
        valid_xml = '''<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom">
            <title>有効記事</title>
            <content>有効内容</content>
        </entry>'''
        
        assert processor.validate_xml(valid_xml) is True

    def test_validate_xml_invalid(self, processor):
        """無効なXMLの検証テスト"""
        invalid_xml = "<entry><title>無効</entry>"  # 閉じタグが不正
        
        assert processor.validate_xml(invalid_xml) is False

    def test_validate_xml_element(self, processor):
        """XMLエレメントの検証テスト"""
        entry = etree.Element("entry")
        
        assert processor.validate_xml(entry) is True

    def test_create_xml_error(self, processor):
        """XML処理エラー作成のテスト"""
        original_error = etree.XMLSyntaxError("Syntax error")
        
        error_info = processor.create_xml_error(
            "XML解析に失敗しました",
            original_error
        )
        
        assert error_info.error_type == ErrorType.DATA_ERROR
        assert error_info.message == "XML解析に失敗しました"
        assert error_info.details["original_error"] == "Syntax error"
        assert error_info.details["error_type"] == "XMLSyntaxError"

    def test_round_trip_conversion(self, processor, sample_blog_post):
        """XML生成・解析の往復変換テスト"""
        # BlogPost -> XML -> BlogPost
        entry_xml = processor.create_entry_xml(sample_blog_post)
        xml_string = processor.to_xml_string(entry_xml)
        parsed_post = processor.parse_entry_xml(xml_string)
        
        # 基本的な情報が保持されることを確認
        assert parsed_post.title == sample_blog_post.title
        assert parsed_post.content == sample_blog_post.content
        assert parsed_post.author == sample_blog_post.author
        assert parsed_post.summary == sample_blog_post.summary
        assert set(parsed_post.categories) == set(sample_blog_post.categories)
        assert parsed_post.draft == sample_blog_post.draft
        
        # 日時は精度が多少変わる可能性があるため、日付レベルで確認
        assert parsed_post.published.date() == sample_blog_post.published.date()
        assert parsed_post.updated.date() == sample_blog_post.updated.date()