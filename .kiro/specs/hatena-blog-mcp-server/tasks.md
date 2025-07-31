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

### ✅ 完了済み実装状況（2025-07-30）

#### **✅ Step 1: プロジェクト基盤セットアップ（タスク1）** - **完了**
- ✅ リモートリポジトリのクローンと初期化
- ✅ Python 3.12プロジェクト初期化（uv使用）
- ✅ MCP依存関係の追加（mcp[cli] + 関連ライブラリ）
- ✅ 基本的なディレクトリ構造作成（src/tests/docs）
- ✅ pyproject.toml設定（開発依存関係、ビルド設定含む）

#### **✅ Step 2: 最小限のMCPサーバー実装** - **完了**
- ✅ `src/hatena_blog_mcp/server.py` - hello_worldツール付きMCPサーバー
- ✅ 基本的なツールレジストリとハンドラー実装
- ✅ 初期ユニットテスト作成（`tests/unit/test_server.py`）
- ✅ Git管理開始：`feature/initial-setup`ブランチでコミット・プッシュ完了

### 🔄 次回開発セッション手順（修正版）

#### **Step 1: feature/initial-setup ブランチでの残タスク完了**（AI支援）
```bash
cd hatena-mcp-server
git checkout feature/initial-setup
# 1. MCPライブラリインポートエラーの修正
# 2. 動作確認とテスト実行  
# 3. コミット・プッシュでブランチ作業完了
```

**⚠️ 緊急修正タスク：MCPライブラリインポートエラー対応**
- **現在のエラー**: `ImportError: cannot import name 'McpServer' from 'mcp'`
- **対応方法**: zenn_mcp_devプロジェクトの実装を参考に修正
- **参考ファイル**: `zenn_mcp_dev/src/zenn_mcp/server.py`

**MCPサーバー動作確認**
- インポートエラー修正後の動作テスト
- Hello Worldツールの実際の動作確認
- MCPクライアントとの通信テスト

#### **Step 2: プロジェクト管理作業**（開発者実施）
```bash
# 1. プルリクエストの作成・確認・承認
# 2. mainブランチへのマージ
# 3. Claude Code Action設定の確認・実施
```

**CI/CD設定**
- `.github/workflows/claude-code.yml` の設定
- 参考ファイル：`zenn_mcp_dev/.github/workflows/claude-code.yml`
- セットアップガイド：`zenn_mcp_dev/docs/github-actions-setup.md`

#### **Step 3: 次フェーズの実装開始**（AI支援）
```bash
# 新しいfeatureブランチで認証マネージャーの実装開始
```

### 実装優先度（手戻り最小化）
1. **高優先度**: タスク1（プロジェクト基盤） → タスク6（MCPサーバーコア）
2. **中優先度**: タスク3（認証マネージャー） → タスク7（MCPツール）
3. **低優先度**: タスク9-12（テスト・統合・ドキュメント）

### 開発時の注意点
- **小さな単位での実装**: 各機能を最小限で実装し、動作確認してから拡張
- **MCP SDK活用**: 公式ドキュメントとサンプルコードを参照
- **段階的検証**: 各フェーズで必ず動作確認を実施

### 手戻り発生時の対応
- 仕様書の更新が必要な場合：`requirements.md`, `design.md`, `tasks.md`を適宜修正
- アーキテクチャ変更が必要な場合：設計の見直しと相談

### 📋 現在の実装タスクステータス更新

**タスク1**: ✅ **完了** - プロジェクト基盤セットアップ  
**タスク6**: 🔄 **未完了** - MCPサーバーコア（インポートエラー要修正）  
**タスク3**: ⏳ **未着手** - 認証マネージャーの実装  
**タスク7**: ⏳ **未着手** - MCPツール実装  
**タスク13-14**: ⏳ **未着手** - 開発プロセス改善・ナレッジ蓄積

**現在の状況**: feature/initial-setupブランチでの作業が未完了、インポートエラー修正が最優先タスク

**次回の開始コマンド**:
```bash
cd hatena-mcp-server
git checkout feature/initial-setup
# MCPライブラリインポートエラーの修正から開始
```