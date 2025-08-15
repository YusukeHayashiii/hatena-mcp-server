# Implementation Plan

## 実装タスク概要
はてなブログMCPサーバーの段階的実装プラン。テスト駆動開発を採用し、各フェーズで動作確認を行いながら進行します。

## Tasks

- [ ] **1. プロジェクト基盤セットアップ**
  - **リモートリポジトリ**: https://github.com/YusukeHayashiii/hatena-mcp-server
  - uvを使用したPython 3.12プロジェクト初期化
  - MCPライブラリ: `mcp[cli]` を依存関係に追加
  - 基本的なディレクトリ構造とパッケージ構成の作成
  - 開発・テスト環境の構築とCI/CD基盤の準備
  - **GitHub Actions**: Claude Code Actionの導入（参考：`zenn_mcp_dev/.github/workflows/claude-code.yml`、`zenn_mcp_dev/docs/github-actions-setup.md`）
  - _Requirements: REQ-7.1, REQ-7.4_

### **Phase 1: コア機能実装**

- [ ] **2. データモデルとコア設定の実装**
  - `BlogPost`, `BlogConfig`, `ApiResponse`, `ErrorInfo`データクラスの作成
  - Pydantic-settingsを使用した設定管理システムの実装
  - 基本的なデータバリデーションとシリアライゼーションのテスト作成
  - _Requirements: REQ-2.1, REQ-2.2, REQ-7.1_

- [ ] **3. 認証マネージャーの実装**
  - WSSE認証ヘッダー生成機能の実装
  - 設定ファイル（.env, JSON, INI）からの認証情報読み込み機能
  - インタラクティブセットアップスクリプトの作成
  - 認証情報検証とエラーハンドリングのテスト作成
  - _Requirements: REQ-2.1, REQ-2.2, REQ-2.3, REQ-2.4, REQ-2.5_

### **Phase 2: API通信層実装**

- [ ] **4. はてなブログAPI通信基盤の実装**
  - httpxを使用したHTTPクライアントの実装
  - AtomPub XMLパーシング・生成機能（lxml使用）
  - ネットワークエラー処理と自動リトライ機能の実装
  - API制限対応とレート制限機能のテスト作成
  - _Requirements: REQ-6.2, REQ-6.3, REQ-7.3_

- [ ] **5. ブログサービス層の実装**
  - `BlogPostService`クラスの基本CRUD操作実装
  - 記事投稿機能：`create_post`メソッドとAtomPub XML生成
  - 記事更新機能：`update_post`メソッドと部分更新サポート
  - 記事取得機能：`get_post`, `list_posts`メソッドの実装
  - 各操作のユニットテストとモックAPI応答テストの作成
  - _Requirements: REQ-3.1, REQ-3.2, REQ-3.3, REQ-3.5, REQ-4.1, REQ-4.2, REQ-4.3, REQ-4.6, REQ-5.1, REQ-5.2, REQ-5.3, REQ-5.5_

  - 追加（Markdown取り込み拡張）
    - `MarkdownImporter` ユーティリティの設計・実装（Front Matter解析 + Markdown→HTML変換）
    - `create_post_from_markdown(path: str)` 高レベルヘルパー（サービス層経由）
    - 失敗時のデータエラー整形（失敗理由・位置情報などを details に格納）
    - ユニットテスト：Front Matter 有/無、title の自動補完（H1/ファイル名）、draft/categories/tags のマッピング
    - _Requirements: REQ-3（拡張7-10）_

### **Phase 3: MCPサーバー統合**

- [ ] **6. MCPサーバーコアの実装**
  - MCP SDK統合とプロトコル準拠の基本サーバー実装
  - ツールレジストリとMCPツール定義の作成
  - 接続処理とエラーハンドリングの実装
  - サーバー起動・停止プロセスとヘルスチェック機能
  - _Requirements: REQ-1.1, REQ-1.2, REQ-1.3, REQ-1.4, REQ-7.2_

- [ ] **7. MCPツール実装**
  - `create_blog_post`ツール：MCPクライアントからの記事投稿
  - `update_blog_post`ツール：既存記事の更新処理
  - `get_blog_post`ツール：記事詳細取得機能
  - `list_blog_posts`ツール：記事一覧取得機能
  - 各ツールのパラメータバリデーションとレスポンス形式の統一
  - _Requirements: REQ-3.1, REQ-3.4, REQ-4.1, REQ-4.4, REQ-5.1, REQ-5.4_

  - 追加（Markdown取り込み拡張）
    - `create_blog_post_from_markdown` ツール（path: str）
    - エラーハンドリング：変換失敗時はDATA_ERROR返却
    - 統合テスト：Markdownファイル→ツール→投稿までのE2E（APIはモック）

### **Phase 4: エラーハンドリングとログ機能**

- [ ] **8. 包括的エラーハンドリングシステム**
  - `ErrorHandler`クラス：認証、API制限、ネットワーク、データエラーの統一処理
  - 構造化ログシステム（loguru）の実装
  - デバッグモードとプロダクションログレベル設定
  - エラー分類と適切なHTTPステータスコード返却
  - _Requirements: REQ-6.1, REQ-6.2, REQ-6.4, REQ-6.5_

### **Phase 5: 統合テスト・パフォーマンステスト**

- [ ] **9. 統合テストスイートの実装**
  - MCPクライアント-サーバー間の通信テスト
  - はてなブログAPI統合テスト（モック環境）
  - エンドツーエンドワークフローテスト：記事作成→更新→取得
  - 設定管理とフォールバック機能のテスト
  - _Requirements: ALL (統合検証)_

- [ ] **10. パフォーマンス・負荷テスト**
  - サーバー起動時間（10秒以内）のテスト
  - メモリ使用量（100MB以下）の監視テスト
  - 同時接続処理性能テスト
  - API応答時間とスループットの計測
  - _Requirements: REQ-7.2, REQ-7.4_

### **Phase 6: 最終統合・デプロイメント準備**

- [ ] **11. プロダクション対応とドキュメント**
  - 設定ファイルテンプレート（.env.example）の作成
  - セットアップガイドとトラブルシューティング文書
  - パッケージング（pyproject.toml）とインストール手順
  - ヘルスチェック・モニタリング機能の最終調整
  - _Requirements: REQ-2.2, REQ-6.5, REQ-7.1_

- [ ] **12. 全機能統合テスト・本番環境検証**
  - 全フェーズ機能の統合テスト実行
  - 実際のはてなブログAPIを使用した動作確認
  - セキュリティ・認証フローの最終検証  
  - パフォーマンス要件の最終確認とボトルネック解消
  - _Requirements: ALL (最終検証)_

### **Phase 7: 開発プロセス改善・ナレッジ蓄積**

- [ ] **13. スラッシュコマンド整備**
  - 今回の開発で得た知見を基にスラッシュコマンドを作成
  - `/kiro:branch-setup` - ブランチ戦略をtech.mdに初期化
  - `/kiro:reference-analysis [project-name]` - 参考プロジェクトパターン分析
  - `/kiro:library-research [tech-stack]` - 実装前ライブラリ調査
  - `/kiro:status-sync [feature]` - 仕様書と実際の進捗を同期
  - `/kiro:session-plan [feature]` - 構造化された開発セッション計画生成
  - `/kiro:learning-capture` - 開発中の学びをログファイルに記録
  - _Purpose: 次回以降の開発効率向上_

- [ ] **14. 開発プロセス文書化・改善提案**
  - 今回の開発で発見したルールを次回初期セットアップに反映
  - development-learnings.mdの内容をステアリングドキュメントに統合
  - フック機能の改善提案（ライブラリチェック、ステータス自動更新等）
  - 次回プロジェクトでの初期セットアップチェックリスト作成
  - _Purpose: プロジェクト開始時のドキュメント整備効率化_

## Implementation Notes

### テスト駆動開発の原則
- 各実装タスクで最初にテストを作成
- レッドグリーンリファクタリングサイクルの遵守
- モック・スタブを活用した単体テスト
- 統合テストによる実際のAPI動作確認

### 段階的検証ポイント
- Phase 1完了時：基本データ構造とコンフィギュレーションの動作確認
- Phase 2完了時：はてなブログAPI通信の動作確認
- Phase 3完了時：MCPクライアントとの通信確認
- Phase 4完了時：エラーシナリオの全パターンテスト
- Phase 5完了時：性能要件充足の確認
- Phase 6完了時：本番デプロイメント準備完了

### 品質基準
- **コードカバレッジ**: 85%以上
- **型安全性**: mypyによる型チェッククリア
- **コード品質**: Ruffによるリンティングクリア
- **セキュリティ**: 認証情報の安全な管理
- **パフォーマンス**: 設計仕様の性能要件充足

---

## 🚀 Next Steps for Implementation

### ✅ 完了済み実装状況（2025-08-14 更新）

#### **✅ タスク1: プロジェクト基盤セットアップ** - **完了**
- ✅ リモートリポジトリのクローンと初期化
- ✅ Python 3.12プロジェクト初期化（uv使用）
- ✅ MCP依存関係の追加（mcp[cli] + 関連ライブラリ）
- ✅ 基本的なディレクトリ構造作成（src/tests/docs）
- ✅ pyproject.toml設定（開発依存関係、ビルド設定含む）

#### **✅ タスク6: MCPサーバーコア実装** - **完了**
- ✅ `src/hatena_blog_mcp/server.py` - FastMCP実装
- ✅ hello_worldツール付きMCPサーバー
- ✅ MCPライブラリインポートエラー修正
- ✅ 基本的なツールレジストリとハンドラー実装

#### **✅ タスク3: 認証マネージャー実装** - **完了**
- ✅ WSSE認証ヘッダー生成機能の実装
- ✅ 設定ファイル（.env, JSON, INI）からの認証情報読み込み機能
- ✅ インタラクティブセットアップスクリプトの作成
- ✅ 認証情報検証とエラーハンドリングのテスト作成
- ✅ データモデル（AuthConfig, BlogConfig, ErrorInfo等）実装
- ✅ 包括的テストスイート（53テストケース）作成

#### **✅ タスク4: はてなブログAPI通信基盤の実装** - **完了**
- ✅ HTTPクライアント（httpx）とWSSE認証の統合実装
- ✅ AtomPub XMLパーシング・生成機能（lxml使用）
- ✅ ネットワークエラー処理と自動リトライ機能
- ✅ API制限対応とレート制限機能（RateLimiter）
- ✅ 統合テスト作成（エンドツーエンドテスト含む）
- ✅ セキュリティ強化（GitGuardian対応、ハードコードパスワード削除）
- ✅ レートリミッター堅牢化（モック互換、バックオフ更新順序の調整）
- ✅ HTTPクライアントのエラーハンドリング洗練（再試行・ログ）

#### **✅ タスク5: ブログサービス層の実装** - **完了**
- ✅ `BlogPostService` の基本CRUD（create/update/get/list/delete）
- ✅ AtomPub XML との橋渡し実装（`AtomPubProcessor` 利用）
- ✅ ユニットテスト整備（モックHTTP応答）

### 🔄 次回開発セッション手順（最新）

#### **Step 1: mainブランチ同期とブランチ作成**
```bash
cd hatena-mcp-server
git checkout main
git pull origin main
git checkout -b feature/markdown-importer-and-tools
```

#### **Step 2: 依存追加（Markdown + Front Matter）**
```bash
uv add markdown python-frontmatter
```

#### **Step 3: Markdown Importer 実装**
- `src/hatena_blog_mcp/markdown_importer.py` を新規作成
- `load_from_file(path)` / `convert(markdown_text, filename?)` を実装
- Front Matter の `title/summary/categories/tags/draft` を `BlogPost` にマッピング
- Markdown→HTML 変換（`markdown`）

#### **Step 4: サービス層との結合**
- `BlogPostService` に `create_post_from_markdown(path: str)` ヘルパー追加
- 変換失敗時は DATA_ERROR を返すユーティリティを用意

#### **Step 5: ツール追加**
- `server.py` に `create_blog_post_from_markdown(path: str)` ツールを追加
- 既存ツール群（create/update/get/list）公開の下準備（未実装なら TODO）

#### **Step 6: テスト**
- ユニット: `tests/unit/test_markdown_importer.py`（Front Matter 有/無、タイトル補完、ドラフト/カテゴリ）
- 統合: Markdown→ツール→投稿（HTTPはモック）
- 実行: `uv run pytest -q`

#### **Step 7: コミット/PR**
```bash
git add -A
git commit -m "Add Markdown Importer and tool integration"
git push -u origin feature/markdown-importer-and-tools
# PR作成（GitHub CLI 使用可）
```

### 📋 次回実装タスクの優先度（更新）

#### 🔥 **高優先度**
1. MCPツール群の本実装と`BlogPostService`への統合
   - `create_blog_post`/`update_blog_post`/`get_blog_post`/`list_blog_posts`/`create_blog_post_from_markdown`
   - 非同期呼び出しの整備（イベントループ/実行コンテキスト）
   - パラメータ検証と戻り値の標準化
2. エラーハンドリングの詳細化
   - 変換失敗や検証エラーを`DATA_ERROR`に正規化
   - 構造化エラー（`ErrorInfo`）のMCPレスポンス反映
3. 統合テスト（E2E）の追加
   - Markdownファイル→Importer→Service→MCPツール経由の一連フロー（HTTPはモック）
4. 設定/DIの導入
   - サービスファクトリ（環境変数や設定ファイルから`BlogPostService`生成）
5. README整備（クイックスタート）
   - セットアップ（`uv sync --extra dev`）、テスト実行、サーバー起動方法
   - MCP接続手順（`npx -y mcp-remote https://mcp.atlassian.com/v1/sse`）

#### 🎯 **中優先度**
6. タイトル抽出の強化（Setext形式H1の検出を追加）
7. 観測性と品質ゲート
   - ログ整備、CIでの`ruff`/`mypy`/カバレッジ閾値の確認

#### ⏳ 保留（将来）
8. `tags` サポートの検討（要件決定後にモデル/Importer/テスト拡張）

### 🛠️ 技術仕様参考

**はてなブログ AtomPub API**:
- ベースURL: `https://blog.hatena.ne.jp/{username}/{blog_id}/atom`
- 認証: WSSE認証（実装済み）
- フォーマット: AtomPub XML

**使用ライブラリ**:
- httpx: 非同期HTTP通信
- lxml: XML処理
- pydantic: データ検証（実装済み）

### 📚 参考資料
- [はてなブログAtomPub API](https://kita127.hatenablog.com/entry/2023/05/17/004937)
- 認証設定: `.env.example`ファイル参照

### 📊 現在の実装進捗

**✅ 完了済み**:
- タスク1: プロジェクト基盤セットアップ
- タスク3: 認証マネージャーの実装  
- タスク4: はてなブログAPI通信基盤の実装
- タスク6: MCPサーバーコア

**🔄 次回実装予定**:
- **タスク7**: MCPツール実装
- **タスク9-12**: テスト・統合・ドキュメント

**次回の開始コマンド**:
```bash
cd hatena-mcp-server
git checkout main && git pull origin main
git checkout -b feature/markdown-importer-and-tools
uv add markdown python-frontmatter
```

### 🎯 本日の成果（2025-08-14）

#### **テストグリーン化**: 全125テスト通過
- レートリミッターの挙動を仕様・テスト期待に整合
- `ConfigManager` の `.env` 読み込みを明示指定時のみマージへ変更（テスト汚染防止）
- `XML Processor` のコンパクト出力とエラー情報の堅牢化
- `pyproject.toml` で `lxml<6` に固定（互換性確保）

#### **サービス層**:
- `BlogPostService` CRUD 実装とユニットテスト整備

#### **次の一手**:
- Markdown Importer と MCPツール群の追加実装（Step 2-6 に従う）

---

## 変更履歴（2025-08-15 反映）

- fix: `MarkdownImporter.convert()` 実行前に `markdown_processor.reset()` を呼び出し、拡張の内部状態リーク（特に `toc`）を防止
- docs: `tags` は一旦未対応として統一（実装・モデル・テストから除外）
- docs: `README.md` を暫定作成（空）。`pyproject.toml` の `readme` 参照によるビルド失敗の回避

影響範囲:
- `src/hatena_blog_mcp/markdown_importer.py`: 未使用インポート削除、ドキュメントから`tags`記載を削除、`reset()` 追加
- 既存テストは全てグリーン（`uv run pytest -q` にて 140 passed）