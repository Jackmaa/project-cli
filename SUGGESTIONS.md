# Project CLI - Improvement Suggestions

This document contains ideas for enhancing the project-cli tool, organized by implementation difficulty.

> **🔥 Major Update:** Phases 1, 2, and 3 completed! Interactive mode, IDE integration, advanced git features, AND full TUI dashboard are now live!

## ✅ Completed Features

These features have been successfully implemented (November 2025):

### ✅ 1. Interactive Project Selector & IDE Opener (DONE)
- ✅ Interactive list mode with `projects list -i`
- ✅ Direct open command: `projects open project-name`
- ✅ Config management: `projects config`
- ✅ Auto-detection of installed IDEs (nvim, vim, code, cursor, etc.)
- ✅ IDE preference stored in `~/.config/project-cli/config.json`

### ✅ 5. Configuration File for Preferences (DONE)
- ✅ Config file at `~/.config/project-cli/config.json`
- ✅ IDE preference storage
- ✅ Interactive configuration command

### ✅ 6. TUI (Text User Interface) Dashboard (DONE) 🔥
- ✅ Full-screen interactive dashboard with `projects dashboard`
- ✅ Multi-panel layout (stats, git overview, projects table, quick actions, footer)
- ✅ Vim-style keyboard shortcuts displayed in footer
- ✅ Live fuzzy search with real-time filtering
- ✅ Status/priority changes with single keypress (a/p/c/x, 1/2/3)
- ✅ Direct IDE opening (o/Enter)
- ✅ Manual git refresh (r)
- ✅ Reactive UI with instant updates
- ✅ Built with Textual library

### ✅ 7. Enhanced Git Integration (DONE)
- ✅ Git status displayed in `list` command (branch, ahead/behind, uncommitted)
- ✅ Smart caching with 5-minute TTL
- ✅ Manual refresh with `projects refresh`
- ✅ GitHub command enhanced with local vs remote comparison
- ✅ Recommendations for pull/push actions
- ✅ Remote tracking and sync status

---

## 🔮 Future Improvements

These features are still available for implementation:

## Easy Wins (Beginner-Friendly)

### 1. Quick Switch/CD Helper

**Description:** Generate shell commands to quickly change directory to a project.

**Implementation:**
- Generate shell function: `eval $(python3 -m projects.cli cd "project-name")`
- Or create shell aliases automatically in `.bashrc`/`.zshrc`

**Benefits:**
- Navigate to projects instantly from anywhere in terminal

### 2. Better Filtering Options

**Description:** Enhanced filtering and sorting capabilities.

**Implementation:**
- Combine multiple filters: `--status active --priority high --tag web`
- Search by name: `--search "react"`
- Sort options: `--sort last-activity` or `--sort name`

**Benefits:**
- Find projects faster in large collections
- More flexible querying

### 3. Export/Import Functionality

**Description:** Backup and restore project database.

**Implementation:**
- `export --format json` to backup project database
- `import projects.json` to restore or share configurations

**Benefits:**
- Data portability
- Easy migration between machines
- Share project configurations with team

## Intermediate Improvements

### 4. Smart Project Templates

**Description:** Bootstrap new projects with predefined structures.

**Implementation:**
- `projects.cli init "new-project" --template python-cli`
- Creates directory structure, git init, requirements.txt, etc.
- Store templates in `~/.config/project-cli/templates/`

**Benefits:**
- Consistent project structure
- Faster project initialization
- Best practices enforcement

### 5. Recently Accessed Tracking

**Description:** Track which projects you interact with.

**Implementation:**
- Auto-update `last_activity` when running commands on a project
- New `recent` command to show recently interacted projects
- Store access history in database

**Benefits:**
- Quick access to frequently used projects
- Better understanding of work patterns

## Advanced Features

### 6. TUI (Text User Interface)

**Description:** Full-screen interactive interface for project management.

**Implementation:**
- Use `textual` library for TUI
- Navigate projects with arrow keys
- Update status with hotkeys (a=active, p=paused, etc.)
- Split view: project list + details panel
- Live search/filter

**Benefits:**
- Much faster workflow
- Visual overview of all projects
- Mouse and keyboard navigation

### 7. Task Tracking Per Project

**Description:** Manage todos within specific projects.

**Implementation:**
- Add todos to projects: `todo add "project-name" "Fix bug #123"`
- Show pending todos in `list` output
- Mark todos as complete
- New database table: `project_tasks`

**Benefits:**
- Keep context within project management tool
- Track what needs to be done for each project

### 8. Time Tracking

**Description:** Track time spent on each project.

**Implementation:**
- `timer start "project-name"` - start tracking time
- `timer stop` - stop current timer
- Store time entries in database
- Generate weekly/monthly time reports
- Integration with `log` command to auto-log time entries

**Benefits:**
- Understand time allocation
- Billing for client projects
- Productivity insights

### 9. Git Hooks Integration

**Description:** Automatically log git activity.

**Implementation:**
- Auto-log commits to activity_logs
- Install post-commit hook:
  ```bash
  echo 'python3 -m projects.cli log "$(basename $PWD)" --auto "Committed: $(git log -1 --pretty=%B)"' > .git/hooks/post-commit
  ```
- `setup-hooks "project-name"` command to install hooks
- Optional: pre-commit hook to update project status

**Benefits:**
- Automatic activity tracking
- No manual logging needed
- Better project history

## Python Capabilities Reference

Python is excellent for CLI tools! Here are some capabilities you can leverage:

### Subprocess Management
- Run any shell command: `subprocess.run(["code", path])`
- Open URLs, editors, file managers
- Execute git commands programmatically

### File System Monitoring
- Use `watchdog` library to monitor project directories
- Auto-update database when files change
- Detect new git commits automatically

### Async Operations
- Use `asyncio` to fetch GitHub stats for all projects in parallel
- Speed up bulk operations (scan, stats, etc.)
- Non-blocking UI updates in TUI

### Packaging & Distribution
- Use `pyproject.toml` + `pip install -e .` for development
- Make globally available as `projects` command (instead of `python3 -m projects.cli`)
- Distribute via PyPI for easy installation: `pip install project-cli`

### Rich Terminal Features
- Progress bars for long operations (scanning directories)
- Interactive prompts and menus
- Colored output and tables (already using Rich)
- Live updating displays

### External Integrations
- GitHub API (already partially implemented)
- GitLab, Bitbucket APIs
- Slack/Discord notifications for project updates
- Integration with project management tools (Jira, Trello)

## Implementation Priority Suggestions

### ✅ Phase 1 - Quick Wins (COMPLETED!)
1. ~~Interactive project selector with IDE opener~~ ✅
2. ~~Configuration file~~ ✅
3. Better filtering and sorting
4. Export/import functionality

### ✅ Phase 2 - Enhanced Workflow (COMPLETED!)
5. ~~Enhanced git integration~~ ✅
6. Recently accessed tracking

### ✅ Phase 3 - Advanced Features (COMPLETED!)
7. ~~TUI interface (big improvement to UX)~~ ✅ 🔥
8. Task tracking
9. Project templates

### Phase 4 - Automation
10. Git hooks integration
11. Time tracking
12. File system monitoring

## Notes

- Start with features that provide immediate value (Phase 1)
- Test each feature thoroughly before moving to the next
- Keep the CLI simple and focused - don't over-engineer
- Maintain backward compatibility with existing database
- Consider creating a migration system for database schema changes

## Contributing

If you implement any of these suggestions, please:
1. Update the README.md with new features
2. Add documentation in COMMANDES.md
3. Create tests if applicable
4. Update ARCHITECTURE.md if adding new modules
