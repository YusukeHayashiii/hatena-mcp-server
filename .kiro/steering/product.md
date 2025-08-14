# Product Overview

## Product Overview
This project implements Kiro-style Spec-Driven Development methodology using Claude Code. It provides a structured framework for software development that emphasizes psychological safety, clear specifications, and systematic progress tracking through AI-assisted development workflows.

## Core Features
- **Spec-Driven Development Workflow**: Multi-phase development process with requirements, design, and task phases
- **AI-Assisted Development**: Integration with Claude Code slash commands, hooks, and agents
- **Progress Tracking**: Systematic task management and specification compliance checking
- **Psychological Safety Framework**: Documentation and principles for creating psychologically safe development environments
- **Steering Document Management**: Project-wide context and rule management for AI interactions
- **Multi-language Support**: Supports thinking in English while generating responses in Japanese

## Target Use Case
This framework is designed for development teams who want to:
- Implement systematic, specification-driven development processes
- Leverage AI assistance while maintaining human oversight and approval gates
- Create psychologically safe environments for collaborative development
- Ensure consistent project knowledge sharing through steering documents
- Track development progress systematically across multiple phases

## Key Value Proposition
- **Structured Development Process**: Prevents skipping phases and ensures thorough planning before implementation
- **AI-Human Collaboration**: Combines AI efficiency with human judgment through approval workflows
- **Knowledge Preservation**: Steering documents maintain consistent project context across all AI interactions
- **Cultural Emphasis**: Focuses on psychological safety and human-centered development practices
- **Flexibility**: Optional steering phase allows adaptation to different project needs

## Project Addendum: Hatena Blog MCP Server

To support real-world authoring workflows, this project now targets a concrete use case: an MCP server that posts to Hatena Blog via AtomPub. A new Markdown-first authoring flow has been aligned across requirements, design, and tasks.

- User value: Author in Markdown locally, publish via MCP with correct categories/draft/state
- Approach: Keep blog posting core HTML-based, add a Markdown Importer that converts Markdown (+ YAML Front Matter) into a `BlogPost` domain entity and HTML content
- Safety: Importer is optional and decoupled; service layer remains stable for other content sources

This addendum is reflected in:
- `.kiro/specs/hatena-blog-mcp-server/requirements.md`: Markdown投稿の受け入れ基準（Front Matter マッピング、失敗時エラー）
- `.kiro/specs/hatena-blog-mcp-server/design.md`: `Markdown Importer` コンポーネントと Optional MCP Tool 追加
- `.kiro/specs/hatena-blog-mcp-server/tasks.md`: Importer 実装・ツール・テストのサブタスク

## Development Philosophy
The framework emphasizes:
1. Human approval at each development phase
2. Psychological safety as a foundation for effective teamwork
3. Clear separation between steering (project context) and specifications (feature details)
4. Continuous progress tracking and specification compliance
5. Cultural awareness and inclusive development practices