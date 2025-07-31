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

---

## Project: hatena-blog-mcp-server

### Session Date: 2025-07-30

#### Rules Added Post-Development Start

##### 1. Branch Strategy & Version Control Rules
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