# GitHub Copilot Agents Configuration

This directory contains initialization files for GitHub Copilot agents working on this repository.

## Files

### init.md
The primary initialization file that GitHub Copilot agents automatically load when starting. This file contains:
- Project overview and architecture
- Development workflow and conventions  
- Code standards and best practices
- Testing strategies
- Security practices
- Common tasks and guidelines

## How It Works

When GitHub Copilot agents are invoked (either through GitHub Actions or Copilot Workspace), they automatically load `.github/agents/init.md` to understand the project context, conventions, and guidelines. This ensures consistent behavior across all agent interactions.

## Maintenance

- Keep `init.md` updated with current project conventions
- Update when significant architectural changes occur
- Ensure guidelines remain actionable and specific
- Review regularly to remove outdated information

## Related Files

- `.github/agent.md` - Original comprehensive agent configuration (kept for reference)
- `.github/agents/init.md` - Active initialization file used by GitHub Copilot

Last updated: 2025-12-23
