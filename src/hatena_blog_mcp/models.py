"""
Data models for Hatena Blog MCP Server.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    """エラータイプの列挙"""
    AUTH_ERROR = "auth_error"
    API_LIMIT_ERROR = "api_limit_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    NETWORK_ERROR = "network_error"
    DATA_ERROR = "data_error"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND_ERROR = "not_found_error"
    PERMISSION_ERROR = "permission_error"


class BlogConfig(BaseModel):
    """ブログ設定・認証情報"""
    username: str = Field(..., description="はてなユーザーID")
    blog_id: str = Field(..., description="ブログID")
    api_key: str = Field(..., description="APIキー", repr=False)

    model_config = {"extra": "forbid"}


class AuthConfig(BaseModel):
    """認証設定"""
    username: str = Field(..., description="はてなユーザーID")
    password: str = Field(..., description="APIキー（パスワード扱い）", repr=False)

    model_config = {"extra": "forbid"}


class BlogPost(BaseModel):
    """ブログ記事エンティティ"""
    title: str = Field(..., description="記事タイトル")
    content: str = Field(..., description="記事本文")
    categories: list[str] = Field(default_factory=list, description="カテゴリ一覧")
    
    # AtomPub用の追加フィールド
    id: str | None = Field(None, description="AtomエントリID")
    author: str | None = Field(None, description="記事作成者")
    summary: str | None = Field(None, description="記事概要")
    published: datetime | None = Field(None, description="公開日時")
    updated: datetime | None = Field(None, description="更新日時")
    draft: bool | None = Field(None, description="下書きフラグ")
    
    # URL情報
    edit_url: str | None = Field(None, description="編集URL")
    self_url: str | None = Field(None, description="自己参照URL")
    alternate_url: str | None = Field(None, description="代替URL（ブログ記事URL）")
    
    # 従来のフィールド（互換性のため）
    post_id: str | None = Field(None, description="記事ID")
    post_url: str | None = Field(None, description="記事URL")
    created_at: datetime | None = Field(None, description="作成日時")
    updated_at: datetime | None = Field(None, description="更新日時")

    model_config = {"extra": "forbid"}


class ErrorInfo(BaseModel):
    """エラー情報"""
    error_type: ErrorType = Field(..., description="エラータイプ")
    message: str = Field(..., description="エラーメッセージ")
    details: dict[str, Any] | None = Field(None, description="エラー詳細")
    retry_after: int | None = Field(None, description="リトライ推奨秒数")

    model_config = {"extra": "forbid"}


class ApiResponse(BaseModel):
    """API応答結果"""
    success: bool = Field(..., description="成功フラグ")
    data: dict[str, Any] | None = Field(None, description="レスポンスデータ")
    error: ErrorInfo | None = Field(None, description="エラー情報")

    model_config = {"extra": "forbid"}
