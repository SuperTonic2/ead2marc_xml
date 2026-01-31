#!/bin/bash
# setup-claude-project.sh
# Setup script for initializing Claude Code projects
# Works for both existing users and new team member onboarding
#
# Usage:
#   ./setup-claude-project.sh [project-dir] [project-name]
#   ./setup-claude-project.sh --install-tools   # Install Claude Code + MCP servers globally
#   ./setup-claude-project.sh --help

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_step() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

show_help() {
    cat << 'EOF'
Claude Code Project Setup Script

USAGE:
    ./setup-claude-project.sh [OPTIONS] [project-dir] [project-name]

OPTIONS:
    --install-tools    Install Claude Code CLI, VS Code extension, and MCP servers (run once per machine)
    --check            Check if required tools are installed
    --force            Overwrite existing project files (settings, todo.md, CLAUDE.md)
    --help             Show this help message

EXAMPLES:
    # First time setup (install tools globally):
    ./setup-claude-project.sh --install-tools

    # Initialize current directory as a Claude Code project:
    ./setup-claude-project.sh

    # Initialize a specific directory:
    ./setup-claude-project.sh ~/repos/my-project "My Project"

    # Re-initialize and overwrite existing files:
    ./setup-claude-project.sh --force ~/repos/my-project

WHAT --install-tools DOES:
    1. Installs Claude Code CLI (npm install -g @anthropic-ai/claude-code)
    2. Installs Claude Code VS Code extension (anthropic.claude-code)
    3. Installs Playwright Chromium browser
    4. Installs uv/uvx (for Nana Banana MCP)
    5. Configures global MCP servers (Playwright, Nana Banana)
    6. Configures global hooks for auto-allowing MCP tools

WHAT PROJECT SETUP DOES:
    1. Creates .claude/ directory with permission settings
    2. Creates tasks/todo.md for task tracking
    3. Creates CLAUDE.md with development workflow instructions
    4. Updates .gitignore to exclude local settings

    Note: Existing files are NOT overwritten unless --force is specified.

AFTER RUNNING:
    1. Open the project in VS Code: code ~/repos/my-project
    2. Click the Claude icon in the sidebar (or Cmd+Esc / Ctrl+Esc)
    3. Ask Claude: "Please analyze this codebase and update the CLAUDE.md file with the project structure, build commands, and architecture overview."
    4. Review and refine CLAUDE.md as needed

EOF
}

check_tools() {
    print_header "Checking installed tools"
    
    local all_good=true
    
    # Check Node.js
    if command -v node &> /dev/null; then
        print_step "Node.js: $(node --version)"
    else
        print_error "Node.js: NOT INSTALLED"
        echo "       Install from: https://nodejs.org/"
        all_good=false
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        print_step "npm: $(npm --version)"
    else
        print_error "npm: NOT INSTALLED"
        all_good=false
    fi
    
    # Check Claude Code CLI
    if command -v claude &> /dev/null; then
        print_step "Claude Code CLI: $(claude --version 2>/dev/null || echo 'installed')"
    else
        print_warning "Claude Code CLI: NOT INSTALLED"
        echo "       Run: ./setup-claude-project.sh --install-tools"
        all_good=false
    fi
    
    # Check VS Code
    if command -v code &> /dev/null; then
        print_step "VS Code CLI: available"
        # Check if Claude Code extension is installed
        if code --list-extensions 2>/dev/null | grep -q "anthropic.claude-code"; then
            print_step "Claude Code VS Code extension: installed"
        else
            print_warning "Claude Code VS Code extension: NOT INSTALLED"
            echo "       Run: code --install-extension anthropic.claude-code"
        fi
    else
        print_warning "VS Code CLI: NOT IN PATH"
        echo "       In VS Code: Cmd+Shift+P > 'Shell Command: Install code command in PATH'"
    fi
    
    # Check uvx (for nanobanana)
    if command -v uvx &> /dev/null; then
        print_step "uvx: installed (for Nana Banana MCP)"
    else
        print_warning "uvx: NOT INSTALLED (optional, for Nana Banana MCP)"
        echo "       Install uv from: https://docs.astral.sh/uv/getting-started/installation/"
    fi
    
    # Check if Playwright browsers are installed
    if [ -d "$HOME/.cache/ms-playwright" ] || [ -d "$HOME/Library/Caches/ms-playwright" ]; then
        print_step "Playwright browsers: installed"
    else
        print_warning "Playwright browsers: NOT INSTALLED"
        echo "       Run: npx playwright install chromium"
    fi
    
    echo ""
    if [ "$all_good" = true ]; then
        echo -e "${GREEN}All required tools are installed!${NC}"
    else
        echo -e "${YELLOW}Some tools are missing. Run --install-tools to install them.${NC}"
    fi
}

install_tools() {
    print_header "Installing Claude Code and MCP servers"
    
    # Check for Node.js first
    if ! command -v node &> /dev/null; then
        print_error "Node.js is required but not installed."
        echo "Please install Node.js from https://nodejs.org/ first."
        exit 1
    fi
    
    # Install Claude Code CLI (skip if already installed)
    echo ""
    if command -v claude &> /dev/null; then
        print_step "Claude Code CLI already installed, skipping"
    else
        echo "Installing Claude Code CLI..."
        npm install -g @anthropic-ai/claude-code
        
        # Get npm global bin directory and add to PATH for this session
        NPM_GLOBAL_BIN=$(npm config get prefix)/bin
        export PATH="$NPM_GLOBAL_BIN:$PATH"
        
        # Verify claude is now available
        if ! command -v claude &> /dev/null; then
            print_error "Claude Code installed but 'claude' command not found in PATH"
            echo ""
            echo "Add this to your ~/.bashrc or ~/.zshrc:"
            echo "  export PATH=\"$NPM_GLOBAL_BIN:\$PATH\""
            echo ""
            echo "Then restart your terminal and run this script again."
            exit 1
        fi
        print_step "Claude Code CLI installed and verified"
    fi
    
    # Install VS Code extension (skip if already installed)
    echo ""
    if command -v code &> /dev/null; then
        if code --list-extensions 2>/dev/null | grep -q "anthropic.claude-code"; then
            print_step "Claude Code VS Code extension already installed, skipping"
        else
            echo "Installing Claude Code VS Code extension..."
            code --install-extension anthropic.claude-code
            print_step "Claude Code VS Code extension installed"
        fi
    else
        print_warning "VS Code 'code' command not found in PATH"
        echo "         Install the extension manually from VS Code:"
        echo "         1. Open VS Code"
        echo "         2. Go to Extensions (Ctrl+Shift+X)"
        echo "         3. Search for 'Claude Code' by Anthropic"
        echo "         4. Click Install"
        echo ""
        echo "         Or add 'code' to PATH:"
        echo "         - In VS Code: Cmd+Shift+P > 'Shell Command: Install code command in PATH'"
    fi
    
    # Install Playwright browsers (skip if already installed)
    echo ""
    if [ -d "$HOME/.cache/ms-playwright" ] || [ -d "$HOME/Library/Caches/ms-playwright" ]; then
        print_step "Playwright Chromium already installed, skipping"
    else
        echo "Installing Playwright Chromium browser..."
        npx playwright install chromium
        print_step "Playwright Chromium installed"
    fi
    
    # Check for uvx and install uv if needed (for nanobanana)
    echo ""
    if command -v uvx &> /dev/null; then
        print_step "uv already installed, skipping"
    else
        echo "Installing uv (for Nana Banana MCP)..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        # Add to current session PATH
        export PATH="$HOME/.local/bin:$PATH"
        print_step "uv installed"
    fi
    
    # Configure global MCP servers (now that claude is verified)
    echo ""
    echo "Configuring global MCP servers..."
    configure_global_mcp
    
    # Configure global hooks for auto-allowing MCP tools
    echo ""
    echo "Configuring global hooks..."
    configure_global_hooks
    
    echo ""
    print_header "Installation Complete!"
    echo ""
    echo "Next steps:"
    echo "  1. You may need to restart your terminal for PATH changes"
    echo "  2. Run this script again without --install-tools to set up a project"
    echo ""
    echo "To set up a new project:"
    echo "  ./setup-claude-project.sh ~/repos/your-project"
    echo ""
    echo "Then open in VS Code:"
    echo "  code ~/repos/your-project"
    echo ""
    echo "Click the Claude icon in the sidebar to start!"
}

configure_global_mcp() {
    # This adds MCP servers to ~/.claude.json
    # First check if they already exist to avoid unnecessary modifications
    
    CLAUDE_JSON="$HOME/.claude.json"
    
    # Double-check claude is available
    if ! command -v claude &> /dev/null; then
        print_error "Claude CLI not available - cannot configure MCP servers"
        echo "         MCP servers must be configured manually after fixing PATH"
        return 1
    fi
    
    # Check if Playwright MCP already exists in ~/.claude.json
    if [ -f "$CLAUDE_JSON" ] && grep -q '"playwright"' "$CLAUDE_JSON" 2>/dev/null; then
        print_step "Playwright MCP already configured, skipping"
    else
        echo "  Adding Playwright MCP server..."
        if claude mcp add playwright -s user -- /usr/bin/npx @playwright/mcp@latest --browser chromium 2>/dev/null; then
            print_step "Playwright MCP added"
        else
            print_warning "Could not add Playwright MCP"
        fi
    fi
    
    # Check if Nana Banana MCP already exists in ~/.claude.json
    if [ -f "$CLAUDE_JSON" ] && grep -q '"nanobanana"' "$CLAUDE_JSON" 2>/dev/null; then
        print_step "Nana Banana MCP already configured, skipping"
    else
        echo "  Adding Nana Banana MCP server..."
        # User needs to set GEMINI_API_KEY environment variable for initial setup
        if [ -n "$GEMINI_API_KEY" ]; then
            if claude mcp add nanobanana -s user \
                -e GEMINI_API_KEY="$GEMINI_API_KEY" \
                -e NANOBANANA_MODEL=pro \
                -e IMAGE_OUTPUT_DIR="$HOME/Pictures/nanobanana" \
                -- uvx nanobanana-mcp-server@latest 2>/dev/null; then
                print_step "Nana Banana MCP added"
            else
                print_warning "Could not add Nana Banana MCP"
            fi
        else
            print_warning "GEMINI_API_KEY env var not set - skipping Nana Banana MCP"
            echo "         To add manually: claude mcp add nanobanana -s user -e GEMINI_API_KEY=your-key -- uvx nanobanana-mcp-server@latest"
        fi
    fi
    
    print_step "MCP server configuration complete"
}

configure_global_hooks() {
    # Configure hooks in ~/.claude/settings.json for auto-allowing MCP tools
    
    CLAUDE_SETTINGS_DIR="$HOME/.claude"
    CLAUDE_SETTINGS="$CLAUDE_SETTINGS_DIR/settings.json"
    
    mkdir -p "$CLAUDE_SETTINGS_DIR"
    
    # Check if file exists and has content
    if [ -f "$CLAUDE_SETTINGS" ] && [ -s "$CLAUDE_SETTINGS" ]; then
        print_warning "~/.claude/settings.json already exists, skipping hooks configuration"
        echo "         Review and merge manually if needed"
        return
    fi
    
    cat > "$CLAUDE_SETTINGS" << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "mcp__nanobanana__.*",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'allow'"
          }
        ]
      },
      {
        "matcher": "mcp__playwright__.*",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'allow'"
          }
        ]
      }
    ]
  }
}
EOF
    
    print_step "Global hooks configured (auto-allow MCP tools)"
}

setup_project() {
    local FORCE_OVERWRITE="${1:-false}"
    local PROJECT_DIR="${2:-.}"
    local PROJECT_NAME="${3:-$(basename "$(cd "$PROJECT_DIR" 2>/dev/null && pwd || echo "$PROJECT_DIR")")}"
    
    # Convert to absolute path
    if [[ "$PROJECT_DIR" != /* ]]; then
        PROJECT_DIR="$(pwd)/$PROJECT_DIR"
    fi
    
    print_header "Setting up Claude Code project: $PROJECT_NAME"
    echo "Directory: $PROJECT_DIR"
    if [ "$FORCE_OVERWRITE" = "true" ]; then
        echo -e "${YELLOW}Force mode: existing files will be overwritten${NC}"
    fi
    echo ""
    
    # Create directory if it doesn't exist
    mkdir -p "$PROJECT_DIR"
    
    # Create directory structure
    mkdir -p "$PROJECT_DIR/.claude"
    mkdir -p "$PROJECT_DIR/tasks"
    
    # Create .gitignore entries for Claude files
    GITIGNORE="$PROJECT_DIR/.gitignore"
    if [ -f "$GITIGNORE" ]; then
        # Check if entries already exist
        if ! grep -q "settings.local.json" "$GITIGNORE" 2>/dev/null; then
            echo "" >> "$GITIGNORE"
            echo "# Claude Code local settings (machine-specific)" >> "$GITIGNORE"
            echo ".claude/settings.local.json" >> "$GITIGNORE"
            print_step "Updated .gitignore"
        else
            print_step ".gitignore already has Claude entries, skipping"
        fi
    else
        cat > "$GITIGNORE" << 'EOF'
# Claude Code local settings (machine-specific)
.claude/settings.local.json
EOF
        print_step "Created .gitignore"
    fi
    
    # Create shared settings.json (commit to repo)
    if [ -f "$PROJECT_DIR/.claude/settings.json" ] && [ "$FORCE_OVERWRITE" != "true" ]; then
        print_step ".claude/settings.json already exists, skipping (use --force to overwrite)"
    else
        cat > "$PROJECT_DIR/.claude/settings.json" << 'EOF'
{
  "permissions": {
    "allow": []
  }
}
EOF
        print_step "Created .claude/settings.json (team-shared)"
    fi
    
    # Create local settings (gitignored, machine-specific)
    if [ -f "$PROJECT_DIR/.claude/settings.local.json" ] && [ "$FORCE_OVERWRITE" != "true" ]; then
        print_step ".claude/settings.local.json already exists, skipping (use --force to overwrite)"
    else
        cat > "$PROJECT_DIR/.claude/settings.local.json" << 'EOF'
{
  "permissions": {
    "allow": [
      "mcp__nanobanana__*",
      "mcp__playwright__*",
      "Bash(npm run dev:*)",
      "Bash(npm install:*)",
      "Bash(npm run build:*)",
      "Bash(npm run lint:*)",
      "Bash(npm run test:*)",
      "Bash(npx:*)",
      "Bash(git:*)",
      "Bash(ls:*)",
      "Bash(cat:*)",
      "Bash(grep:*)",
      "Bash(find:*)",
      "Bash(mkdir:*)",
      "Bash(curl:*)",
      "Bash(pkill:*)",
      "Bash(lsof:*)"
    ]
  }
}
EOF
        print_step "Created .claude/settings.local.json (your machine)"
    fi
    
    # Create initial todo.md
    if [ -f "$PROJECT_DIR/tasks/todo.md" ] && [ "$FORCE_OVERWRITE" != "true" ]; then
        print_step "tasks/todo.md already exists, skipping (use --force to overwrite)"
    else
        cat > "$PROJECT_DIR/tasks/todo.md" << 'EOF'
# Project Tasks

## Current Sprint

- [ ] Initial project setup
- [ ] Review PROJECT_BRIEF.md
- [ ] Define initial architecture

## Backlog

## Completed

## Review Notes

---
*Updated by Claude Code*
EOF
        print_step "Created tasks/todo.md"
    fi
    
    # Create CLAUDE.md with workflow instructions
    if [ -f "$PROJECT_DIR/CLAUDE.md" ] && [ "$FORCE_OVERWRITE" != "true" ]; then
        print_step "CLAUDE.md already exists, skipping (use --force to overwrite)"
    else
        cat > "$PROJECT_DIR/CLAUDE.md" << 'EOF'
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

<!-- Ask Claude to analyze the codebase and fill in this section -->

## Key References

- `PROJECT_BRIEF.md` - Detailed architecture and requirements
- `README.md` - Repository layout and contribution rules
- `tasks/todo.md` - Current task tracking

## Development Workflow

1. **First think through the problem, read the codebase for relevant files, and write a plan to `tasks/todo.md`.**

2. **The plan should have a list of todo items that you can check off as you complete them.**

3. **Before you begin working, check in with me and I will verify the plan.**

4. **Then, begin working on the todo items, marking them as complete as you go.**

5. **Please every step of the way just give me a high level explanation of what changes you made.**

6. **Make every task and code change as simple as possible.**  
   We want to avoid making any massive or complex changes.  
   Every change should impact as little code as possible.  
   Everything is about *simplicity*.

7. **Finally, add a review section to the `todo.md` file with a summary of the changes you made and any other relevant information.**

8. **DO NOT BE LAZY. NEVER BE LAZY. IF THERE IS A BUG FIND THE ROOT CAUSE AND FIX IT. NO TEMPORARY FIXES. YOU ARE A SENIOR DEVELOPER. NEVER BE LAZY.**

9. **MAKE ALL FIXES AND CODE CHANGES AS SIMPLE AS HUMANLY POSSIBLE.**
   They should only impact necessary code relevant to the task and nothing else.
   It should impact as little code as possible.
   Your goal is to **not introduce any bugs**.
   *It's all about simplicity.*

## Common Commands

```bash
npm run dev          # Start dev server
npm run build        # Production build
npm run lint         # Run linter
npm test             # Run tests
```

## Architecture Notes

<!-- Add project-specific architecture info here -->
EOF
        print_step "Created CLAUDE.md"
    fi
    
    echo ""
    print_header "Setup Complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Open in VS Code: code $PROJECT_DIR"
    echo "  2. Click the Claude icon in the sidebar (or Cmd+Esc / Ctrl+Esc)"
    echo "  3. Ask Claude: \"Please analyze this codebase and update the CLAUDE.md"
    echo "     file with the project structure, build commands, and architecture overview.\""
    echo ""
    echo "Or use terminal: cd $PROJECT_DIR && claude"
    echo ""
    echo "Your global MCP servers (playwright, nanobanana) are already available."
}

# Main script logic
FORCE_OVERWRITE=false
POSITIONAL_ARGS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --help|-h)
            show_help
            exit 0
            ;;
        --check)
            check_tools
            exit 0
            ;;
        --install-tools)
            install_tools
            exit 0
            ;;
        --force|-f)
            FORCE_OVERWRITE=true
            shift
            ;;
        *)
            POSITIONAL_ARGS+=("$1")
            shift
            ;;
    esac
done

# Restore positional arguments
set -- "${POSITIONAL_ARGS[@]}"

# If no special command, run setup_project
# Check if claude is installed first
if ! command -v claude &> /dev/null; then
    print_warning "Claude Code not found!"
    echo ""
    echo "For first-time setup, run:"
    echo "  $0 --install-tools"
    echo ""
    echo "Or install manually:"
    echo "  npm install -g @anthropic-ai/claude-code"
    echo ""
    read -p "Continue with project setup anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

setup_project "$FORCE_OVERWRITE" "$@"
