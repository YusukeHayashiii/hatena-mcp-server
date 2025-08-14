# Technology Stack

## Architecture
This project implements a documentation and workflow framework rather than a traditional software application. It consists of:
- **Documentation Framework**: Markdown-based specification and steering documents
- **Workflow Engine**: Claude Code slash commands and hooks integration
- **Content Management**: Structured document organization with clear separation of concerns

## Frontend
Not applicable - this is a documentation and workflow framework project.

## Backend  
Not applicable - this is a documentation and workflow framework project.

## Development Environment
- **Primary Tool**: Claude Code CLI for AI-assisted development
- **Documentation Format**: Markdown files with structured organization
- **File Organization**: Directory-based separation (`.kiro/steering/`, `.kiro/specs/`, `.claude/commands/`)
- **Version Control**: Git-compatible file structure with feature branch workflow

## Common Commands
Based on the CLAUDE.md specification:
- `/kiro:steering` - Create/update steering documents
- `/kiro:steering-custom` - Create custom steering for specialized contexts
- `/kiro:spec-init [detailed description]` - Initialize spec with detailed project description
- `/kiro:spec-requirements [feature]` - Generate requirements document
- `/kiro:spec-design [feature]` - Interactive design phase with approval workflow
- `/kiro:spec-tasks [feature]` - Interactive task generation with approval workflow
- `/kiro:spec-status [feature]` - Check current progress and phases

## Environment Variables
For the Hatena Blog MCP Server use case, define the following (managed via `.env`):

- `HATENA_USERNAME`: Hatena account user ID
- `HATENA_BLOG_ID`: Target blog ID
- `HATENA_API_KEY`: AtomPub API key

Note: Tests should not depend on real `.env`. The configuration loader must allow disabling default `.env` auto-loading to avoid test contamination.

## Port Configuration
Not applicable - this is a documentation framework, no services run on ports.

## Document Structure Technology
- **Markdown Processing**: Standard markdown with image support
- **Markdown Importer**: `markdown` (HTML conversion), `python-frontmatter` (YAML Front Matter parsing)
- **File References**: `@filename` syntax for document referencing
- **Multilingual Support**: Japanese content with English workflow instructions
- **Image Management**: PNG image storage in `share/img/` directory

## Integration Points
- **Claude Code**: Primary integration through slash commands and hooks
- **Version Control**: Git-ready file structure for team collaboration
- **Documentation Tools**: Compatible with standard markdown processors

## Branch Strategy & Version Control

### Branch Naming Conventions
- **Feature branches**: `feature/[task-number]-[description]` (e.g., `feature/task-3-auth-manager`)
- **Phase branches**: `feature/[phase]-[feature-name]` (e.g., `feature/setup-hatena-mcp`)
- **Main branch**: `main` (production-ready code)

### Branch Workflow
1. **Phase-based Development**: Create new feature branches for each implementation phase
2. **Task-based Separation**: Large tasks are managed in individual branches
3. **Pull Request Required**: All merges go through human approval gates
4. **Sequential Integration**: Merge to main branch after phase completion

### Branch Lifecycle Example
```
main
├── feature/initial-setup (foundation setup - currently in progress)
├── feature/auth-manager (authentication manager - next task 3)
├── feature/api-communication (API communication layer - tasks 4-5)
├── feature/mcp-tools (MCP tool implementation - task 7)
└── feature/integration-tests (integration testing - tasks 9-10)
```

### Development Flow
1. **Branch Creation**: `git checkout -b feature/task-X-description`
2. **Implementation & Commits**: Small, incremental commits
3. **Push**: `git push -u origin feature/task-X-description`
4. **Pull Request**: Human approval process
5. **Merge**: Integration to main branch
6. **Next Phase**: Continue with new feature branch

### Approval Gates
- **Code Review**: Human approval via pull requests
- **Phase Gates**: Kiro-style 3-phase approval (requirements → design → tasks)
- **Implementation Gates**: Functional verification at each task completion

## Technical Constraints
- All documents must be markdown-compatible
- Steering documents are always included in AI context
- Specifications follow 3-phase approval workflow (requirements → design → tasks)
- Feature branches require pull request approval before merging
- No external dependencies or runtime requirements