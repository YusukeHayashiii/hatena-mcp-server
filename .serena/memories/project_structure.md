# Project Structure and Architecture

## Directory Layout
```
hatena-mcp-server/
├── .github/
│   └── workflows/
│       └── claude-code.yml        # Claude Code GitHub Action
├── .kiro/                         # Kiro spec-driven development
│   ├── steering/                  # Project-wide context (product.md, tech.md, structure.md)
│   └── specs/                     # Feature specifications
│       └── hatena-blog-mcp-server/
│           ├── spec.json          # Specification metadata
│           ├── requirements.md    # Requirements document
│           ├── design.md          # Technical design
│           └── tasks.md           # Implementation tasks
├── .claude/                       # Claude Code configuration
│   └── commands/                  # Custom slash commands
├── src/                           # Source code
│   └── hatena_blog_mcp/
│       ├── __init__.py           # Package initialization
│       └── server.py             # Main MCP server implementation
├── tests/                         # Test suite
│   └── unit/
│       └── test_server.py        # Unit tests
├── pyproject.toml                # Project configuration and dependencies
├── uv.lock                       # Dependency lock file
├── .python-version               # Python version specification (3.12)
├── .gitignore                    # Git ignore patterns
├── CLAUDE.md                     # Development workflow specification
├── README.md                     # Project documentation
└── main.py                       # Alternative entry point
```

## Package Structure
- **Main Package**: `hatena_blog_mcp`
- **Entry Point**: `hatena_blog_mcp.server:main`
- **Console Script**: `hatena-mcp-server`

## Current Implementation Status
### Completed
- ✅ Basic project structure
- ✅ MCP server foundation with FastMCP
- ✅ Hello world tool for testing
- ✅ Unit test framework
- ✅ Development environment setup

### Planned (from specifications)
- 🔄 Authentication manager (WSSE for Hatena Blog)
- 🔄 Blog post service (CRUD operations)
- 🔄 AtomPub XML handling
- 🔄 Configuration management
- 🔄 Error handling and logging
- 🔄 MCP tools for blog operations

## Design Patterns
- **MCP Server Pattern**: Using FastMCP for simplified MCP implementation
- **Service Layer**: Planned separation of concerns (auth, blog service, etc.)
- **Configuration Management**: Pydantic settings with multiple sources
- **Async Programming**: For HTTP operations and MCP server

## Integration Points
- **MCP Protocol**: Standard interface for AI assistant integration
- **Hatena Blog API**: AtomPub-based REST API
- **GitHub Actions**: CI/CD with Claude Code integration
- **Kiro Workflow**: Spec-driven development methodology