# Hatena Blog MCP Server - Project Overview

## Purpose
This project implements an MCP (Model Context Protocol) server for Hatena Blog API integration. It allows AI assistants like Claude to interact with Hatena Blog's AtomPub API for creating, updating, and retrieving blog posts.

## Key Features
- **MCP Server**: Provides standardized MCP protocol interface for blog operations
- **Hatena Blog Integration**: Uses AtomPub API for blog post management
- **Authentication**: WSSE authentication for secure API access
- **Blog Operations**: Create, update, retrieve, and list blog posts

## Project Structure
```
hatena-mcp-server/
├── src/hatena_blog_mcp/     # Main source code
│   ├── server.py           # MCP server implementation (currently minimal)
│   └── __init__.py         # Package initialization
├── tests/unit/             # Unit tests
├── .kiro/                  # Kiro spec-driven development files
│   ├── steering/           # Project-wide context documents
│   └── specs/              # Feature specifications
├── .github/workflows/      # GitHub Actions CI/CD
├── pyproject.toml         # Project configuration and dependencies
└── CLAUDE.md              # Development workflow specification
```

## Current Status
- **Phase**: Ready for implementation
- **Basic MCP Server**: Minimal server with hello_world tool implemented
- **Specifications**: Complete requirements, design, and task specifications available
- **Next Steps**: Implementation of core Hatena Blog functionality

## Development Context
This is a Kiro-style spec-driven development project with comprehensive planning documents and Claude Code integration for AI-assisted development.