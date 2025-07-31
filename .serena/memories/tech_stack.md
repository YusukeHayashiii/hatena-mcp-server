# Technology Stack

## Core Technologies
- **Python**: 3.12 (specified in .python-version)
- **Package Manager**: uv (modern Python package manager)
- **MCP Framework**: FastMCP from `mcp[cli]>=1.12.2`

## Key Dependencies
### Runtime Dependencies
- `mcp[cli]>=1.12.2` - MCP server framework
- `httpx>=0.25.0` - Async HTTP client for API calls
- `lxml>=4.9.0` - XML processing for AtomPub
- `pydantic>=2.0.0` - Data validation and settings
- `pydantic-settings>=2.0.0` - Configuration management
- `python-dotenv>=1.0.0` - Environment variable loading

### Development Dependencies
- `pytest>=7.0.0` - Testing framework
- `pytest-asyncio>=0.21.0` - Async testing support
- `pytest-mock>=3.10.0` - Mocking utilities
- `mypy>=1.0.0` - Static type checking
- `ruff>=0.1.0` - Linting and formatting
- `coverage>=7.0.0` - Code coverage

## Build System
- **Build Backend**: Hatchling
- **Entry Point**: `hatena-mcp-server` command pointing to `hatena_blog_mcp.server:main`

## Development Tools
- **Type Checking**: mypy with strict mode enabled
- **Linting/Formatting**: Ruff with Python 3.12 target
- **Testing**: pytest with asyncio support
- **CI/CD**: GitHub Actions with Claude Code integration

## Architecture
- **MCP Protocol**: Uses FastMCP for simplified MCP server implementation
- **Async Programming**: Async/await pattern for HTTP operations
- **AtomPub API**: XML-based communication with Hatena Blog
- **WSSE Authentication**: Secure authentication headers for API access