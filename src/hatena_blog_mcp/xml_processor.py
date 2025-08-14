"""
AtomPub XML Processing for Hatena Blog.
AtomPubフォーマットのXML生成・解析機能を提供します。
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from lxml import etree
from lxml.builder import ElementMaker

from .models import BlogPost, ErrorInfo, ErrorType


logger = logging.getLogger(__name__)


class AtomPubProcessor:
    """AtomPub XMLの生成・解析を担当するクラス"""
    
    # AtomPub名前空間
    ATOM_NS = "http://www.w3.org/2005/Atom"
    HATENA_NS = "http://www.hatena.ne.jp/info/xmlns#"
    
    # 名前空間マップ
    NSMAP = {
        None: ATOM_NS,  # デフォルト名前空間
        "hatena": HATENA_NS
    }
    
    def __init__(self):
        """AtomPub XMLプロセッサーを初期化します"""
        # ElementMakerを作成（Atom名前空間用）
        self.E = ElementMaker(namespace=self.ATOM_NS, nsmap=self.NSMAP)
        
        # はてな名前空間用のElementMaker
        self.H = ElementMaker(namespace=self.HATENA_NS, nsmap=self.NSMAP)

    def create_entry_xml(self, blog_post: BlogPost) -> etree._Element:
        """
        ブログ記事からAtomエントリXMLを生成します。

        Args:
            blog_post: ブログ記事データ

        Returns:
            etree._Element: AtomエントリXML要素

        Raises:
            ValueError: 必須フィールドが不足している場合
        """
        if not blog_post.title:
            raise ValueError("記事タイトルが必要です")
        if not blog_post.content:
            raise ValueError("記事内容が必要です")

        # エントリ要素の作成
        entry = self.E.entry()
        
        # タイトル
        entry.append(self.E.title(blog_post.title))
        
        # 作成者
        if blog_post.author:
            author = self.E.author()
            author.append(self.E.name(blog_post.author))
            entry.append(author)
        
        # コンテンツ
        content = self.E.content(blog_post.content, type="text/html")
        entry.append(content)
        
        # 概要（指定されている場合）
        if blog_post.summary:
            entry.append(self.E.summary(blog_post.summary))
        
        # カテゴリ（タグ）
        if blog_post.categories:
            for category in blog_post.categories:
                entry.append(self.E.category(term=category))
        
        # 公開日時
        if blog_post.published:
            published_str = blog_post.published.isoformat()
            entry.append(self.E.published(published_str))
        
        # 更新日時
        if blog_post.updated:
            updated_str = blog_post.updated.isoformat()
            entry.append(self.E.updated(updated_str))
        else:
            # 更新日時が指定されていない場合は現在時刻を使用
            now = datetime.now(timezone.utc).isoformat()
            entry.append(self.E.updated(now))
        
        # はてな固有の設定
        if blog_post.draft is not None:
            # 下書きフラグ
            draft_value = "yes" if blog_post.draft else "no"
            entry.append(self.H.draft(draft_value))
        
        # ID（更新時のみ）
        if blog_post.id:
            entry.append(self.E.id(blog_post.id))
        
        # 編集リンク（更新時のみ）
        if blog_post.edit_url:
            edit_link = self.E.link(rel="edit", href=blog_post.edit_url)
            entry.append(edit_link)
        
        # 自己リンク（参照用）
        if blog_post.self_url:
            self_link = self.E.link(rel="self", href=blog_post.self_url)
            entry.append(self_link)
        
        # 代替リンク（ブログ記事のURL）
        if blog_post.alternate_url:
            alt_link = self.E.link(rel="alternate", type="text/html", href=blog_post.alternate_url)
            entry.append(alt_link)

        return entry

    def parse_entry_xml(self, xml_content: Union[str, bytes, etree._Element]) -> BlogPost:
        """
        AtomエントリXMLからブログ記事データを解析します。

        Args:
            xml_content: AtomエントリXML（文字列、バイト列、またはElement）

        Returns:
            BlogPost: 解析されたブログ記事データ

        Raises:
            etree.XMLSyntaxError: XML解析エラー
            ValueError: 必須要素が見つからない場合
        """
        # XMLの解析
        if isinstance(xml_content, etree._Element):
            entry = xml_content
        else:
            if isinstance(xml_content, str):
                content_bytes = xml_content.encode('utf-8')
            else:
                content_bytes = xml_content
            
            try:
                entry = etree.fromstring(content_bytes)
            except etree.XMLSyntaxError as e:
                logger.error(f"XML解析エラー: {e}")
                raise

        # 名前空間を考慮した要素検索用
        ns = {'atom': self.ATOM_NS, 'hatena': self.HATENA_NS}
        
        # 必須要素の取得
        title_elem = entry.find('.//atom:title', ns)
        if title_elem is None or not title_elem.text:
            raise ValueError("タイトル要素が見つかりません")
        
        content_elem = entry.find('.//atom:content', ns)
        if content_elem is None:
            raise ValueError("コンテンツ要素が見つかりません")
        
        # BlogPostオブジェクトの構築
        blog_post = BlogPost(
            title=title_elem.text,
            content=content_elem.text or "",
        )
        
        # ID
        id_elem = entry.find('.//atom:id', ns)
        if id_elem is not None and id_elem.text:
            blog_post.id = id_elem.text
        
        # 作成者
        author_elem = entry.find('.//atom:author/atom:name', ns)
        if author_elem is not None and author_elem.text:
            blog_post.author = author_elem.text
        
        # 概要
        summary_elem = entry.find('.//atom:summary', ns)
        if summary_elem is not None and summary_elem.text:
            blog_post.summary = summary_elem.text
        
        # カテゴリ（タグ）
        category_elems = entry.findall('.//atom:category', ns)
        if category_elems:
            blog_post.categories = [
                elem.get('term') for elem in category_elems
                if elem.get('term')
            ]
        
        # 公開日時
        published_elem = entry.find('.//atom:published', ns)
        if published_elem is not None and published_elem.text:
            try:
                blog_post.published = datetime.fromisoformat(
                    published_elem.text.replace('Z', '+00:00')
                )
            except ValueError:
                logger.warning(f"公開日時の解析に失敗: {published_elem.text}")
        
        # 更新日時
        updated_elem = entry.find('.//atom:updated', ns)
        if updated_elem is not None and updated_elem.text:
            try:
                blog_post.updated = datetime.fromisoformat(
                    updated_elem.text.replace('Z', '+00:00')
                )
            except ValueError:
                logger.warning(f"更新日時の解析に失敗: {updated_elem.text}")
        
        # 下書きフラグ（はてな固有）
        draft_elem = entry.find('.//hatena:draft', ns)
        if draft_elem is not None and draft_elem.text:
            blog_post.draft = draft_elem.text.lower() == "yes"
        
        # リンク情報の解析
        self._parse_links(entry, blog_post, ns)
        
        return blog_post

    def _parse_links(self, entry: etree._Element, blog_post: BlogPost, ns: Dict[str, str]) -> None:
        """
        エントリからリンク情報を解析します。

        Args:
            entry: エントリXML要素
            blog_post: 更新対象のブログ記事オブジェクト
            ns: 名前空間マッピング
        """
        link_elems = entry.findall('.//atom:link', ns)
        
        for link in link_elems:
            rel = link.get('rel')
            href = link.get('href')
            
            if not href:
                continue
            
            if rel == 'edit':
                blog_post.edit_url = href
            elif rel == 'self':
                blog_post.self_url = href
            elif rel == 'alternate' and link.get('type') == 'text/html':
                blog_post.alternate_url = href

    def parse_feed_xml(self, xml_content: Union[str, bytes, etree._Element]) -> List[BlogPost]:
        """
        AtomフィードXMLから複数のブログ記事データを解析します。

        Args:
            xml_content: AtomフィードXML

        Returns:
            List[BlogPost]: 解析されたブログ記事のリスト

        Raises:
            etree.XMLSyntaxError: XML解析エラー
        """
        # XMLの解析
        if isinstance(xml_content, etree._Element):
            feed = xml_content
        else:
            if isinstance(xml_content, str):
                content_bytes = xml_content.encode('utf-8')
            else:
                content_bytes = xml_content
            
            try:
                feed = etree.fromstring(content_bytes)
            except etree.XMLSyntaxError as e:
                logger.error(f"フィードXML解析エラー: {e}")
                raise

        # 名前空間を考慮した要素検索用
        ns = {'atom': self.ATOM_NS, 'hatena': self.HATENA_NS}
        
        # エントリ要素を全て取得
        entry_elems = feed.findall('.//atom:entry', ns)
        
        blog_posts = []
        for entry_elem in entry_elems:
            try:
                blog_post = self.parse_entry_xml(entry_elem)
                blog_posts.append(blog_post)
            except (ValueError, etree.XMLSyntaxError) as e:
                logger.warning(f"エントリの解析をスキップ: {e}")
                continue
        
        return blog_posts

    def to_xml_string(
        self,
        element: etree._Element,
        pretty_print: bool = True,
        encoding: str = 'utf-8'
    ) -> str:
        """
        XML要素を文字列に変換します。

        Args:
            element: XML要素
            pretty_print: 整形出力するかどうか
            encoding: エンコーディング

        Returns:
            str: XML文字列
        """
        xml_bytes = etree.tostring(
            element,
            pretty_print=pretty_print,
            encoding=encoding,
            xml_declaration=True
        )
        # compact指定時、宣言以降の改行を除去して厳密にコンパクト化
        if not pretty_print:
            xml_str = xml_bytes.decode(encoding)
            header, sep, rest = xml_str.partition('?>')
            if sep:
                rest = rest.replace('\n', '')
                return header + sep + rest
            return xml_str
        return xml_bytes.decode(encoding)

    def validate_xml(self, xml_content: Union[str, bytes, etree._Element]) -> bool:
        """
        XMLの妥当性を検証します。

        Args:
            xml_content: 検証対象のXML

        Returns:
            bool: XMLが妥当な場合True
        """
        try:
            if isinstance(xml_content, etree._Element):
                return True
            
            if isinstance(xml_content, str):
                content_bytes = xml_content.encode('utf-8')
            else:
                content_bytes = xml_content
            
            etree.fromstring(content_bytes)
            return True
        except etree.XMLSyntaxError:
            return False

    def create_xml_error(
        self,
        message: str,
        original_error: Optional[Exception] = None
    ) -> ErrorInfo:
        """
        XML処理エラー情報を作成します。

        Args:
            message: エラーメッセージ
            original_error: 元の例外

        Returns:
            ErrorInfo: XML処理エラー情報
        """
        details = {}
        if original_error:
            # lxml の XMLSyntaxError は複雑だが、テストではインスタンス化時のTypeErrorが出ることがある
            # ここでは与えられたオブジェクトを安全に文字列化し、型名を格納する
            try:
                msg = getattr(original_error, 'msg', None)
            except Exception:
                msg = None
            try:
                details["original_error"] = (msg if isinstance(msg, str) and msg else str(original_error))
                details["error_type"] = type(original_error).__name__
            except Exception:
                details["original_error"] = ""
                details["error_type"] = original_error.__class__.__name__

        return ErrorInfo(
            error_type=ErrorType.DATA_ERROR,
            message=message,
            details=details,
            retry_after=None
        )