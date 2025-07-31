# Development Guidelines and Patterns

## Kiro Spec-Driven Development
This project follows the Kiro methodology for systematic development:

### Workflow Phases
1. **Requirements** → **Design** → **Tasks** → **Implementation**
2. Each phase requires approval before proceeding
3. Current status: Ready for implementation (all phases approved)

### Key Principles
- **Human approval required** at each phase transition
- **No skipping phases**: Design requires approved requirements; Tasks require approved design
- **Documentation as code**: Structured markdown serves as application logic
- **AI-human collaboration**: AI efficiency with human judgment

## Code Development Patterns

### MCP Tool Implementation
```python
@mcp.tool()
def tool_name(
    param: Annotated[type, "Parameter description"]
) -> ReturnType:
    """Clear description of what the tool does"""
    logger.info(f"Tool called with param: {param}")
    
    try:
        # Implementation
        return result
    except Exception as e:
        logger.error(f"Error in tool_name: {e}")
        return f"エラーが発生しました: {str(e)}"
```

### Error Handling Strategy
- Use try-catch blocks for all external operations
- Log errors with descriptive messages
- Return user-friendly error messages (in Japanese)
- Include original error details in logs

### Authentication Pattern (Planned)
- WSSE authentication for Hatena Blog API
- Configuration through environment variables
- Secure credential management
- Multiple configuration sources (env, .env, JSON, interactive)

### Testing Strategy
- **Unit Tests**: Test individual functions/methods
- **Integration Tests**: Test MCP protocol integration
- **Mock External APIs**: Use pytest-mock for HTTP calls
- **Async Testing**: pytest-asyncio for async functions

## Language and Communication
- **Thinking**: English (for development efficiency)
- **User Communication**: Japanese (project requirement)
- **Error Messages**: Japanese for end users
- **Code Comments**: English
- **Documentation**: Mixed (English for technical, Japanese for user-facing)

## Branch Strategy
- **Feature branches**: `feature/task-name`
- **Pull request workflow**: Required for merging
- **Main branch**: `main` (production-ready)
- **CI/CD**: GitHub Actions with Claude Code integration

## Quality Standards
- **Type Safety**: Full mypy strict mode compliance
- **Code Coverage**: ≥85% target
- **Performance**: <10s startup, <2s API response (p95)
- **Memory Usage**: <100MB operational

## Security Guidelines
- **No hardcoded secrets**: Use environment variables
- **Secure logging**: Don't log sensitive information
- **Input validation**: Validate all external inputs
- **Error disclosure**: Don't expose internal details to users

## Async Programming
- Use `async/await` for I/O operations
- Proper resource cleanup with context managers
- No blocking operations in async contexts
- Connection pooling for HTTP clients