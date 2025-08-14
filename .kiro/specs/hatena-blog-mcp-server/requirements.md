# Requirements Document

## Introduction
はてなブログAPIを活用して記事の投稿・更新機能を提供するMCPサーバーを開発する。このサーバーは、Claude Code等のAIアシスタントがはてなブログに対して記事の作成・更新操作を実行できるよう、MCPプロトコルに準拠したインターフェースを提供する。技術スタックとしてPython及びuvを使用し、はてなブログのAtomPub APIとの連携を実現する。

## Requirements

### Requirement 1: MCP サーバー基盤
**User Story:** As an AI assistant, I want to connect to a hatena blog MCP server, so that I can perform blog operations through standardized MCP protocol

#### Acceptance Criteria

1. WHEN MCP クライアントがサーバーに接続を要求する THEN システムは MCP プロトコルに準拠した接続を確立する SHALL
2. IF MCP サーバーが起動される THEN システムはサポートされるツールのリストを公開する SHALL
3. WHEN MCP クライアントがツール一覧を要求する THEN システムは利用可能な はてなブログ 操作ツールを返却する SHALL
4. IF 接続エラーが発生する THEN システムは適切なエラーメッセージを返却する SHALL

### Requirement 2: 認証・設定管理
**User Story:** As a blog author, I want to configure my hatena blog credentials, so that the MCP server can authenticate and access my blog

#### Acceptance Criteria

1. WHEN サーバーが起動される THEN システムはユーザーID、ブログID、APIキーの設定を読み込む SHALL
2. IF 必須の認証情報が不足している THEN システムは設定不備エラーを表示し、適切な設定方法を案内する SHALL
3. WHEN はてなブログAPI認証が実行される THEN システムはAtomPub認証を使用してAPIアクセスを認証する SHALL
4. IF 認証に失敗する THEN システムは認証エラーの詳細を含むエラーメッセージを返却する SHALL
5. WHERE セキュリティ要件において THE SYSTEM SHALL APIキー等の機密情報を環境変数またはセキュアな設定ファイルで管理する SHALL

### Requirement 3: 記事投稿機能
**User Story:** As an AI assistant, I want to create new blog posts, so that I can publish content to hatena blog on behalf of users

#### Acceptance Criteria

1. WHEN MCP クライアントが記事作成ツールを呼び出す THEN システムは必要なパラメータ（タイトル、本文、カテゴリ等）を受け取る SHALL
2. IF 記事作成リクエストが受信される THEN システムははてなブログAtomPub APIを使用して新規記事を投稿する SHALL
3. WHEN 記事投稿が成功する THEN システムは作成された記事のURL、記事ID、投稿日時を返却する SHALL
4. IF 投稿に必須なパラメータが不足している THEN システムは不足しているパラメータを明示したエラーを返却する SHALL
5. WHEN 記事にカテゴリが指定される THEN システムは指定されたカテゴリをブログ記事に適用する SHALL
6. IF はてなブログAPI制限に達している THEN システムはAPI制限エラーとリトライ推奨時間を返却する SHALL

#### Markdown からの投稿（拡張）

7. WHEN MCP クライアントがMarkdownファイル（.md）を指定する THEN システムはMarkdown本文をHTMLに変換し記事として投稿する SHALL
8. WHEN YAML Front Matter が含まれる THEN システムは title/summary/categories/tags/draft を適切に `BlogPost` にマッピングする SHALL
9. IF Front Matter に title が無ければ THEN システムは本文先頭の見出し（H1）またはファイル名をタイトルとして使用する SHOULD
10. IF Markdown が不正または変換に失敗する THEN システムはデータエラー（DETAIL に失敗理由）を返却する SHALL

### Requirement 4: 記事更新機能
**User Story:** As an AI assistant, I want to update existing blog posts, so that I can modify published content on hatena blog

#### Acceptance Criteria

1. WHEN MCP クライアントが記事更新ツールを呼び出す THEN システムは記事ID又はURLと更新内容を受け取る SHALL
2. IF 記事更新リクエストが受信される THEN システムは指定された記事の存在を確認してから更新を実行する SHALL
3. WHEN 記事更新が成功する THEN システムは更新された記事のURL、更新日時、変更サマリを返却する SHALL
4. IF 指定された記事が存在しない THEN システムは記事未発見エラーを返却する SHALL
5. IF 記事の編集権限がない THEN システムは権限不足エラーを返却する SHALL
6. WHEN 部分更新が要求される THEN システムは指定されたフィールドのみを更新し、他のフィールドは保持する SHALL

### Requirement 5: 記事情報取得機能
**User Story:** As an AI assistant, I want to retrieve blog post information, so that I can check current content before making updates

#### Acceptance Criteria

1. WHEN MCP クライアントが記事取得ツールを呼び出す THEN システムは記事ID又はURLを受け取る SHALL
2. IF 記事取得リクエストが受信される THEN システムははてなブログAPIから記事詳細を取得する SHALL
3. WHEN 記事取得が成功する THEN システムは記事のタイトル、本文、カテゴリ、投稿日時、更新日時を返却する SHALL
4. IF 指定された記事が存在しない THEN システムは記事未発見エラーを返却する SHALL
5. WHEN 記事一覧取得が要求される THEN システムは最新の記事リスト（タイトル、URL、投稿日時）を返却する SHALL

### Requirement 6: エラーハンドリング・ログ機能
**User Story:** As a system administrator, I want comprehensive error handling and logging, so that I can troubleshoot issues and monitor system performance

#### Acceptance Criteria

1. WHEN システムエラーが発生する THEN システムは適切なエラーレベル（ERROR、WARNING、INFO）でログを記録する SHALL
2. IF API呼び出しが失敗する THEN システムはHTTPステータスコード、エラーメッセージ、リトライ可否を含む詳細情報を返却する SHALL
3. WHEN ネットワーク接続エラーが発生する THEN システムは自動リトライ機能（最大3回、指数バックオフ）を実行する SHALL
4. WHERE デバッグモードにおいて THE SYSTEM SHALL リクエスト・レスポンスの詳細ログを出力する SHALL
5. IF 設定ファイルの読み込みに失敗する THEN システムは設定エラーの詳細と解決方法を表示する SHALL
6. WHEN レート制限に達した場合 THEN システムは `retry_after`（秒）を含む構造化エラー情報を返す SHALL

### Requirement 7: 技術仕様・パフォーマンス
**User Story:** As a system integrator, I want the MCP server to meet specific technical requirements, so that it can be reliably deployed and maintained

#### Acceptance Criteria

1. WHERE 実装環境において THE SYSTEM SHALL Python 3.12とuvパッケージマネージャーを使用する SHALL
2. WHEN サーバーが起動される THEN システムは10秒以内に初期化を完了し、MCPクライアント接続を受け入れる SHALL
3. IF 同時API呼び出し制限がある THEN システムははてなブログAPIの制限に準拠し、適切なレート制限を実装する SHALL
4. WHERE 依存関係管理において THE SYSTEM SHALL uvを使用してPython依存関係を管理し、再現可能な環境構築を可能にする SHALL
5. WHERE 依存制約において THE SYSTEM SHALL lxml<6 を用いて互換性問題を回避する SHOULD