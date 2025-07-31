# Suggested Commands for Development

## Project Setup and Environment
```bash
# Install dependencies with uv
uv sync

# Activate virtual environment (if needed)
source .venv/bin/activate  # macOS/Linux
```

## Code Quality Commands
```bash
# Run linting and formatting
ruff check .                # Check for linting issues
ruff format .              # Format code
ruff check --fix .         # Auto-fix linting issues

# Type checking
mypy src/                  # Type check source code
mypy .                     # Type check entire project
```

## Testing Commands
```bash
# Run tests
pytest                     # Run all tests
pytest tests/unit/         # Run unit tests only
pytest -v                  # Verbose test output
pytest --cov=src/          # Run with coverage report
pytest --cov=src/ --cov-report=html  # Generate HTML coverage report
```

## Development Server
```bash
# Run the MCP server
python -m hatena_blog_mcp.server
# or using the installed command
hatena-mcp-server

# Run with development entry point
python main.py
```

## Package Management
```bash
# Add dependencies
uv add package_name        # Add runtime dependency
uv add --dev package_name  # Add development dependency

# Update dependencies
uv sync                    # Sync dependencies with lock file
uv lock                    # Update lock file
```

## Git and Version Control
```bash
# Standard git commands for macOS
git status
git add .
git commit -m "message"
git push

# Branch management (following Kiro workflow)
git checkout -b feature/task-name
git checkout main
```

## Utility Commands (macOS/Darwin)
```bash
# File operations
ls -la                     # List files with details
find . -name "*.py"        # Find Python files
grep -r "pattern" src/     # Search in source code

# Process management
ps aux | grep python       # Find Python processes
kill -9 PID               # Kill process by PID

# System information
uname -a                   # System information
python --version           # Python version
```

## Testing MCP Server Connectivity
```bash
# Test the hello_world tool (example command structure)
# Actual MCP client commands would depend on the MCP client being used
```

## Build and Distribution
```bash
# Build package
uv build                   # Build distribution packages

# Install in development mode
pip install -e .           # Install in editable mode
```

## Kiro Workflow Commands
```bash
# Check specification status
/kiro:spec-status hatena-blog-mcp-server

# Other Kiro commands available in Claude Code interface
/kiro:learning-capture
/kiro:branch-setup
```