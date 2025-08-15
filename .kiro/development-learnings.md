# Development Learnings Log

This document captures rules, best practices, and insights discovered during development that should be included in initial project setup for future projects.

## Project: hatena_mcp_dev

### Session Date: 2025-07-31

#### Configuration Improvements

##### 1. MCP Tool Guidelines Added to CLAUDE.md
**Added to**: `CLAUDE.md` - Development Guidelines section
**Reason**: Need to standardize tool usage across development sessions
**Rules Added**:
- **Use Serena MCP tools**: Prioritize using Serena's semantic coding tools (mcp__serena__*) for codebase search, analysis, and editing operations for efficient and precise code manipulation
- **Use Gemini Google Search**: Prioritize using mcp__gemini-google-search__google_search for web searches to gather information and research

**For Next Project**: Include MCP tool usage guidelines in initial CLAUDE.md setup

#### Process Documentation

##### 1. Tool Selection Standardization
**Issue**: Multiple tools available for similar tasks (search, analysis, web research)
**Learning**: Establish clear tool preferences to ensure consistent, efficient workflows
**Action for Next Project**: Document preferred tools for common operations in CLAUDE.md from project start

##### 2. Development Guidelines Evolution
**Issue**: Guidelines need to evolve based on available toolsets
**Learning**: Keep development guidelines living document that adapts to tooling improvements
**Action for Next Project**: Regular review and update of development guidelines

### Session Date: 2025-08-15

#### Implementation Phase Learnings

##### 1. Markdown Importer Integration Pattern
**Learning**: Markdown processing with Front Matter requires careful state management
**Issue**: `markdown` processor extensions can leak state between conversions
**Solution**: Always call `processor.reset()` before each conversion
**For Next Project**: Document state management patterns for external libraries

##### 2. MCP Tool Implementation Strategy
**Learning**: Implement core services first, then MCP tool wrappers
**Success Pattern**: 
- Core business logic in service layer (`BlogPostService`)
- Thin MCP tool wrappers that call service methods
- Consistent error handling across both layers
**For Next Project**: Establish service-first, tools-second implementation order

##### 3. Test-Driven Development with External APIs
**Learning**: Mock external API calls early and comprehensively
**Success Pattern**: 
- Mock HTTP responses at httpx level
- Separate unit tests (mocked) from integration tests (real API)
- Use test fixtures for consistent API response data
**For Next Project**: Set up API mocking infrastructure before implementation

##### 4. Configuration Management Complexity
**Learning**: Multiple configuration sources require careful precedence handling
**Issue**: Environment variable pollution between tests
**Solution**: Explicit configuration source specification in tests
**For Next Project**: Design configuration hierarchy upfront and test isolation patterns

---

## Project: hatena-blog-mcp-server

### Session Date: 2025-08-08

#### Rules Added Post-Development Start

##### 1. Markdown Importer Should Be Decoupled From Core CRUD
**Added to**: `.kiro/specs/hatena-blog-mcp-server/{requirements.md, design.md, tasks.md}`
**Reason**: Users author in Markdown; API requires HTML/AtomPub. Decoupling keeps services testable and reusable.
**Rule Added**:
- Keep service layer HTML-first; add a separate `MarkdownImporter` to map Front Matter and convert Markdown→HTML
- Provide `create_post_from_markdown(path)` as a thin integration layer; failures return DATA_ERROR with details
- Document libraries early (`markdown`, `python-frontmatter`) and add tests for edge cases (no title, invalid front matter)

##### 2. Configuration Loader Must Not Auto-Load `.env` In Tests
**Added to**: `.kiro/steering/tech.md`, `hatena_blog_mcp/config.py`
**Reason**: `.env` leakage broke tests and masked missing-field errors.
**Rule Added**:
- Default: do not auto-load `.env` in code paths used by tests; allow explicit `_env_file` control
- Test cases use environment patching to inject values deterministically

##### 3. Rate Limiter Error Contract Consistency
**Issue**: `retry_after` expected int, code provided float; and backoff multiplier handling affected expectations
**Learning**: Align model types and backoff math with tests/specs
**Action for Next Project**: Define numeric types precisely in models; document backoff behavior and headers precedence

##### 4. Mocking httpx Responses Carefully
**Issue**: Tests mocking `httpx.Response` must ensure `status_code` is an int; some code paths compared directly and failed when a Mock slipped through.
**Learning**: When comparing status codes, guard against non-int or use `int(status_code)`; or ensure test doubles set correct spec/attributes.
**Action**: Prefer `Mock(spec=httpx.Response)` with `status_code=int` and avoid nested Mock for `response` inside `HTTPStatusError` where direct comparison occurs.
**Added to**: `.kiro/steering/tech.md`
**Reason**: No explicit branch strategy was defined initially, causing uncertainty about workflow
**Rule Added**:
- Branch naming conventions: `feature/[task-number]-[description]`
- Pull request approval gates required
- Phase-based development workflow
- Sequential integration to main branch

**For Next Project**: Add branch strategy section to tech.md during steering phase

##### 2. Development Session Planning Structure
**Added to**: `.kiro/specs/[feature]/tasks.md`
**Reason**: Initial tasks didn't clearly separate AI work from human work
**Rule Added**:
- Separate development session steps into:
  - Step 1: AI-assisted technical work
  - Step 2: Human project management work (PR approval, CI/CD setup)
  - Step 3: Next phase preparation
- Clear status tracking: "未完了" vs "部分完了" vs "完了"

**For Next Project**: Include human/AI work separation in task planning phase

#### Process Improvements Identified

##### 1. Library Investigation Should Precede Implementation
**Issue**: MCP library import errors discovered during implementation
**Learning**: Research actual library usage patterns before writing code
**Action for Next Project**: Add library research phase to tasks

##### 2. Reference Project Analysis Early
**Issue**: Could have avoided import errors by checking zenn_mcp_dev earlier
**Learning**: Identify and analyze reference implementations during design phase
**Action for Next Project**: Add reference project analysis to design phase

##### 3. Specification Status Tracking Needs Regular Updates
**Issue**: Tasks.md status became outdated during development
**Learning**: Regularly update specification status to reflect actual progress
**Action for Next Project**: Add status update checkpoints to development workflow

#### Documentation Structure Learnings

##### 1. Language Consistency in Technical Documents
**Issue**: Mixed Japanese/English in tech.md
**Learning**: Maintain language consistency within individual documents
**Action for Next Project**: Establish language policy per document type during steering

##### 2. Development Context Preservation
**Issue**: Need to track what was completed vs what was attempted
**Learning**: Distinguish between "attempted but failed" and "partially completed"
**Action for Next Project**: Define status terminology more precisely

#### Tools and Commands to Develop

##### 1. Slash Commands for Future Development
Based on this project's experience, the following slash commands should be created:

- `/kiro:branch-setup` - Initialize branch strategy in tech.md
- `/kiro:reference-analysis [project-name]` - Analyze reference project patterns
- `/kiro:library-research [tech-stack]` - Research library usage before implementation
- `/kiro:status-sync [feature]` - Sync actual progress with specification documents
- `/kiro:session-plan [feature]` - Generate structured development session plan
- `/kiro:learning-capture` - Add learnings to this log file

##### 2. Hook Improvements
- Pre-implementation hook: Check library imports
- Post-commit hook: Update task status automatically
- Pre-PR hook: Verify specification alignment

---

## Template for Future Sessions

### Rules to Add During Initial Setup
1. **Branch Strategy** (tech.md)
   - Naming conventions
   - Approval gates
   - Development flow

2. **Development Session Structure** (tasks.md)
   - AI vs Human work separation
   - Status terminology definitions
   - Progress tracking methods

3. **Reference Project Analysis** (design.md)
   - Identify similar implementations
   - Extract patterns and best practices
   - Document library usage patterns

4. **Library Research Phase** (tasks.md)
   - Add explicit library investigation tasks
   - Verify import patterns before coding
   - Test basic functionality early

### Checklist for Steering Phase
- [ ] Define branch strategy and workflow
- [ ] Establish language policy per document type
- [ ] Identify reference projects for analysis
- [ ] Plan library research methodology
- [ ] Set up development session structure
- [ ] Define progress tracking terminology

---

## Next Project Improvements

Based on this project's learnings, future projects should:

1. **Start with complete branch strategy** - Add to tech.md during steering
2. **Include reference analysis** - Research similar projects during design
3. **Plan library verification** - Test imports before main implementation
4. **Structure session planning** - Separate AI and human work clearly
5. **Maintain living documentation** - Regular status updates throughout development

This log should be reviewed and incorporated into the steering documents of future projects.