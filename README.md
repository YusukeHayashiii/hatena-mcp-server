# Hatena Blog MCP Server

はてなブログに記事を投稿・更新するためのMCP（Model Context Protocol）サーバーです。Claude CodeなどのAIアシスタントが、はてなブログと連携して記事管理を行えるようになります。

## 🚀 主な機能

- **記事投稿**: 新しいブログ記事の投稿
- **記事更新**: 既存記事の編集・更新
- **記事取得**: 指定した記事の詳細情報を取得
- **記事一覧**: ブログ記事の一覧表示
- **Markdown対応**: Markdownファイルから直接記事投稿
- **Front Matter対応**: YAML Front Matterによるメタデータ管理

## 📋 必要な準備

### 1. はてなブログAPIキーの取得

1. [はてなブログ](https://blog.hatena.ne.jp/)にログイン
2. ブログ設定 → 詳細設定 → AtomPub から APIキーを取得
3. ブログのユーザーIDとブログIDを確認

### 2. 環境設定

プロジェクトルートに `.env` ファイルを作成し、以下の情報を設定してください：

```bash
HATENA_USER_ID=your_username
HATENA_BLOG_ID=your_blog_id
HATENA_API_KEY=your_api_key_here
```

## 🛠️ セットアップ

### 前提条件

- Python 3.12以上
- uv（Python パッケージマネージャー）

### インストール手順

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/YusukeHayashiii/hatena-mcp-server.git
   cd hatena-mcp-server
   ```

2. **依存関係のインストール**
   ```bash
   uv sync --extra dev
   ```

3. **環境設定**
   ```bash
   cp .env.example .env
   # .env ファイルを編集して認証情報を設定
   ```

4. **テスト実行**
   ```bash
   uv run pytest -q
   ```

## 🏃 使用方法

### MCPサーバーの起動

```bash
uv run python -m src.hatena_blog_mcp.server
```

### Claude Code での使用

1. Claude Code で MCP サーバーに接続
2. 利用可能なツールを確認
3. ツールを使用してブログ操作を実行

## 🔧 利用可能なMCPツール

### `create_blog_post`
新しいブログ記事を投稿します。

**パラメータ:**
- `title` (必須): 記事のタイトル
- `content` (必須): 記事の本文（HTML形式）
- `categories` (任意): カテゴリのリスト
- `summary` (任意): 記事の要約
- `draft` (任意): 下書き状態（デフォルト: false）

**使用例:**
```python
create_blog_post(
    title="新しい記事",
    content="<p>記事の本文です。</p>",
    categories=["技術", "Python"],
    draft=False
)
```

### `update_blog_post`
既存の記事を更新します。

**パラメータ:**
- `post_id` (必須): 更新する記事のID
- `title` (任意): 新しいタイトル
- `content` (任意): 新しい本文
- `categories` (任意): 新しいカテゴリ
- `summary` (任意): 新しい要約
- `draft` (任意): 下書き状態

### `get_blog_post`
指定した記事の詳細情報を取得します。

**パラメータ:**
- `post_id` (必須): 取得する記事のID

### `list_blog_posts`
ブログ記事の一覧を取得します。

**パラメータ:**
- `limit` (任意): 取得する記事数の上限（デフォルト: 10、最大: 100）

### `create_blog_post_from_markdown`
Markdownファイルから記事を投稿します。

**パラメータ:**
- `path` (必須): Markdownファイルのパス

**Front Matter例:**
```yaml
---
title: 記事のタイトル
categories: [技術, Python]
summary: 記事の要約
draft: false
---

# 記事本文

Markdownで記述された本文がHTMLに変換されます。
```

## 🧪 テスト

### 全テストの実行
```bash
uv run pytest -v
```

### ユニットテストのみ実行
```bash
uv run pytest tests/unit/ -v
```

### 統合テストのみ実行
```bash
uv run pytest tests/integration/ -v
```

### カバレッジ付きテスト
```bash
uv run pytest --cov=src --cov-report=html
```

## 📁 プロジェクト構造

```
hatena-mcp-server/
├── src/
│   └── hatena_blog_mcp/
│       ├── server.py              # MCP サーバーのメイン実装
│       ├── auth.py                # WSSE 認証管理
│       ├── blog_service.py        # ブログ操作サービス
│       ├── config.py              # 設定管理
│       ├── error_handler.py       # エラーハンドリング
│       ├── http_client.py         # HTTP クライアント
│       ├── markdown_importer.py   # Markdown インポーター
│       ├── models.py              # データモデル
│       ├── rate_limiter.py        # レート制限
│       ├── service_factory.py     # サービスファクトリ
│       └── xml_processor.py       # AtomPub XML 処理
├── tests/
│   ├── unit/                      # ユニットテスト
│   └── integration/               # 統合テスト
├── .env.example                   # 環境変数テンプレート
├── pyproject.toml                 # プロジェクト設定
└── README.md                      # このファイル
```

## 🛠️ 開発

### 開発環境のセットアップ

```bash
# 開発用依存関係込みでインストール
uv sync --extra dev

# プリコミットフックの設定
uv run pre-commit install
```

### コード品質チェック

```bash
# リンティング
uv run ruff check src tests

# 型チェック  
uv run mypy src

# フォーマット
uv run ruff format src tests
```

## 🐛 トラブルシューティング

### 認証エラーが発生する場合

1. `.env` ファイルの設定値を確認
2. はてなブログの設定画面でAPIキーが有効か確認
3. ユーザーIDとブログIDが正しいか確認

### ネットワークエラーが発生する場合

1. インターネット接続を確認
2. ファイアウォール設定を確認
3. プロキシ設定が必要な場合は環境変数を設定

### テストが失敗する場合

```bash
# テスト用環境変数を設定
export HATENA_USER_ID=test_user
export HATENA_BLOG_ID=test_blog  
export HATENA_API_KEY=test_key

# テスト実行
uv run pytest -v
```

## 📚 参考資料

- [はてなブログAtomPub API](https://developer.hatena.ne.jp/ja/documents/blog/apis/atom)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)

## 📝 ライセンス

MIT License

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📧 お問い合わせ

質問や提案がある場合は、[Issues](https://github.com/YusukeHayashiii/hatena-mcp-server/issues) でお知らせください。