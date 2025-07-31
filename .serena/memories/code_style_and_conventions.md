# Code Style and Conventions

## Python Code Style
Based on pyproject.toml configuration:

### Formatting and Linting (Ruff)
- **Line Length**: 88 characters
- **Target Version**: Python 3.12
- **Selected Rules**: E (errors), F (pyflakes), I (isort), N (naming), W (warnings), UP (pyupgrade)
- **Ignored**: E501 (line too long, handled by line-length setting)

### Type Checking (mypy)
- **Strict Mode**: Enabled
- **Python Version**: 3.12
- **Additional Checks**:
  - `warn_return_any = true`
  - `warn_unused_configs = true`

## Code Patterns Observed

### Function Documentation
```python
def hello_world(
    name: Annotated[str, "Name to say hello to"] = "World"
) -> str:
    """A simple hello world tool for testing MCP server connectivity"""
```

### Error Handling
```python
try:
    response_text = f"Hello, {name}! This is the Hatena Blog MCP Server."
    return response_text
except Exception as e:
    logger.error(f"Error in hello_world tool: {e}")
    return f"エラーが発生しました: {str(e)}"
```

### Logging
- Use structured logging with logger instances
- Configure logging at module level
- Include descriptive log messages in Japanese for errors

### MCP Tool Definition
```python
@mcp.tool()
def tool_name(param: Annotated[type, "description"]) -> return_type:
    """Tool description"""
```

## File Organization
- **Source Code**: `src/hatena_blog_mcp/`
- **Tests**: `tests/unit/` (with potential for integration tests)
- **Entry Points**: Defined in pyproject.toml

## Import Style
- Standard library imports first
- Third-party imports second
- Local imports last
- Use type annotations with `from typing import`

## Documentation
- Docstrings for all public functions and classes
- Type hints for all function parameters and return values
- Use `Annotated` for parameter descriptions in MCP tools