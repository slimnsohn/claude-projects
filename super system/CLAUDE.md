# Claude Projects Monorepo

## 7 Claude Rules (Global Standards)
1. First think through the problem, read the codebase for relevant files, and write a plan to tasks/todo.md.
2. The plan should have a list of todo items that you can check off as you complete them
3. Before you begin working, check in with me and I will verify the plan.
4. Then, begin working on the todo items, marking them as complete as you go.
5. Please every step of the way just give me a high level explanation of what changes you made, very brief, like 1-2 lines at most
6. Make every task and code change you do as simple as possible. We want to avoid making any massive or complex changes. Every change should impact as little code as possible. Everything is about simplicity.
7. Finally, add a review section to the todo.md file with a summary of the changes you made and any other relevant information.

## Repository Structure
```
claude-projects/
├── shared-libs/          # Reusable libraries and utilities
├── projects/            # Individual project directories
├── docs/               # Global documentation
├── .github/workflows/  # GitHub Actions and CI/CD
└── README.md          # Repository overview
```

## Development Workflow
- **Planning**: Always create todo lists and get approval before starting
- **Simplicity**: Keep all changes simple and minimal - avoid complex modifications
- **Code Reuse**: Prefer using shared libraries over duplicating code
- **Documentation**: Update relevant docs when making changes

## Project Standards
- Each project must have its own CLAUDE.md with specific requirements
- Use consistent naming conventions across all projects
- Follow existing code patterns and conventions
- All projects should leverage shared-libs when possible

## Git Workflow
- Use descriptive commit messages
- Keep commits atomic and focused
- Use branches for feature development
- Always test before committing

## Claude Code Integration
- Use @claude commands for GitHub integration
- Leverage Claude Code's project management features
- Follow security best practices
- Never commit secrets or sensitive information

## Important Instructions
- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary for achieving your goal
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files unless explicitly requested
- whenever you create a file or reference a script, give me the folder path so I can always know which folder it is in

## Odds and Ends
- never use emojis in any of the code
- always start each session by trying to do read, write, copy, touch access web or anything else you can think of that will require authorization from me
- after every change, remove test and debug files.  don't create "_fixed" or "_improved" versions of scripts, just fix the main version -- I don't want a lot of junk files floating around.  you can make a scratch folder to put tested files and other things into