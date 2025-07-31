# Project Structure

## Root Directory Organization
```
hatena_mcp_dev/
├── .kiro/                    # Kiro framework files
│   ├── steering/            # Always-included project context (NEW)
│   └── specs/               # Feature-specific specifications
├── .claude/                 # Claude Code configuration
│   └── commands/            # Custom slash commands
└── share/                   # Shared documentation and resources
    ├── CLAUDE.md            # Main project specification
    ├── img/                 # Documentation images
    ├── 心理的安全性を咀嚼してみる.md  # Psychological safety document
    └── 心理的安全性を咀嚼してみる.pdf # PDF version
```

## Subdirectory Structures

### `.kiro/steering/` - Project Context Documents
Always included in AI interactions to provide consistent project knowledge:
- `product.md` - Product overview, features, and value proposition
- `tech.md` - Technology stack and development environment
- `structure.md` - This file, describing project organization
- Custom steering files (created via `/kiro:steering-custom`)

### `.kiro/specs/` - Feature Specifications
Feature-specific development specifications following 3-phase workflow:
- Requirements documents
- Design documents  
- Task breakdowns
- Progress tracking

### `.claude/commands/` - Claude Code Integration
Custom slash commands for the Kiro workflow implementation.

### `share/` - Documentation and Resources
- **CLAUDE.md**: Central specification document describing the entire Kiro workflow
- **img/**: PNG images supporting documentation (primarily for psychological safety doc)
- **Japanese documents**: Psychological safety content in Japanese with supporting images

## Code Organization Patterns
This project uses a **documentation-first approach**:
1. **Separation of Concerns**: Steering (project-wide) vs Specs (feature-specific)
2. **Hierarchical Context**: Steering always loaded, specs loaded as needed
3. **Workflow-Driven**: Directory structure mirrors the development process phases
4. **Multilingual Support**: English workflow with Japanese content support

## File Naming Conventions
- **Steering files**: `[domain].md` (e.g., `product.md`, `tech.md`)
- **Specification files**: `[feature]-[phase].md` pattern expected
- **Documentation**: Descriptive names, Japanese titles allowed
- **Images**: Sequential numbering (`image-000.png` through `image-022.png`)

## Import Organization
- **Document References**: Use `@filename.md` syntax for cross-references
- **Image References**: Relative paths from document location (`img/image-000.png`)
- **Workflow References**: Slash commands prefixed with `/kiro:`

## Key Architectural Principles
1. **Always Available Context**: Steering documents loaded in every AI interaction
2. **Phase-Gated Development**: Requirements → Design → Tasks → Implementation
3. **Human Approval Points**: Interactive prompts at each phase transition  
4. **Documentation as Code**: Structured markdown serves as the application logic
5. **Cultural Inclusivity**: Support for multilingual content and psychological safety principles
6. **Tool Integration**: Deep integration with Claude Code's capabilities (slash commands, hooks, agents)

## Inclusion Mode Strategy
- **Always**: All steering documents (consistent project context)
- **Conditional**: Specification documents (when working on related features)
- **Manual**: Reference documents (loaded with `@filename` syntax)