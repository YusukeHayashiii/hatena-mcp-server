# Task Completion Checklist

## Code Quality Checks (Always Required)
When completing any coding task, always run these commands:

### 1. Linting and Formatting
```bash
ruff check .              # Check for linting issues
ruff format .             # Format code according to project style
ruff check --fix .        # Auto-fix any fixable linting issues
```

### 2. Type Checking
```bash
mypy src/                 # Type check source code
```

### 3. Testing
```bash
pytest                    # Run all tests
pytest --cov=src/         # Run tests with coverage
```

## Code Review Checklist
- [ ] All functions have proper type hints
- [ ] Docstrings are present for public functions/classes
- [ ] Error handling is implemented where appropriate
- [ ] Logging is used for important operations
- [ ] Tests are written for new functionality
- [ ] No hard-coded secrets or credentials

## MCP-Specific Checks
- [ ] MCP tools are properly decorated with `@mcp.tool()`
- [ ] Tool parameters use `Annotated` with descriptions
- [ ] Tool docstrings clearly describe functionality
- [ ] Error responses are user-friendly

## Git and Version Control
- [ ] Changes are committed with descriptive commit messages
- [ ] Branch naming follows project conventions (feature/task-name)
- [ ] No sensitive information is committed

## Documentation Updates
- [ ] Update README.md if new features are added
- [ ] Update configuration examples if settings change
- [ ] Document any new environment variables or setup steps

## Integration Testing
- [ ] Test MCP server startup
- [ ] Verify tool registration and discovery
- [ ] Test actual tool functionality if applicable

## Performance Considerations
- [ ] Async patterns are used for I/O operations
- [ ] Resource cleanup is handled properly
- [ ] No blocking operations in async contexts

## Security Checks
- [ ] Authentication credentials are handled securely
- [ ] Input validation is implemented
- [ ] Error messages don't expose sensitive information
- [ ] API keys are managed through environment variables

## Before Pull Request
- [ ] All tests pass
- [ ] Code coverage meets standards (≥85% for this project)
- [ ] No type errors from mypy
- [ ] Ruff checks pass
- [ ] Feature is complete according to specifications
- [ ] Documentation is updated