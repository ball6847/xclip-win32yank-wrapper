# Xclip Shell Wrapper - AI Agent Guide

## Project Overview

This project provides a shell script wrapper that enables xclip compatibility for Windows clipboard utilities. The wrapper bridges the gap between Linux xclip expectations and Windows clipboard tools, specifically supporting `win32yank.exe` (primary) and `win32yoink.exe` (fallback).

**Key Problem Solved:** Windows clipboard utilities lack support for the `-selection` flag and other xclip features that pyperclip and other Linux tools expect. This wrapper provides 100% xclip compatibility on Windows/WSL environments.

## Project Structure

```
xclip-win32yank-wrapper/
├── XCLIP_SHELL_WRAPPER_DESIGN.md    # Comprehensive design document (24KB)
├── AGENTS.md                       # This file - AI agent reference
└── .git/                           # Git repository
```

**Current Status:** Design phase completed, implementation pending

## Technology Stack

- **Language:** Bash shell scripting
- **Target Platforms:** Windows, WSL (Windows Subsystem for Linux)
- **Dependencies:** 
  - Primary: `win32yank.exe`
  - Fallback: `win32yoink.exe`
- **Compatibility Layer:** xclip command-line interface

## Architecture

The wrapper consists of five main components:

1. **Argument Parser** - Processes xclip-compatible command-line arguments
2. **Tool Selection Layer** - Detects and prioritizes available clipboard tools
3. **Selection Handler** - Maps X11 selections to Windows clipboard
4. **Multi-Tool Integration** - Provides consistent interface across different tools
5. **Additional Features** - Handles edge cases, empty clipboard, help text

## Development Workflow

### Build Process

This is a shell script project with no compilation required:

```bash
# Make the script executable
chmod +x xclip

# Place in PATH (no sudo required)
mkdir -p ~/.local/bin
cp xclip ~/.local/bin/
```

### Testing Strategy

The project includes comprehensive test cases in the design document.

## Code Style Guidelines

### Shell Script Standards

- Use `#!/bin/bash` shebang
- Follow POSIX-compatible syntax where possible
- Use `[[ ]]` for conditional expressions
- Quote variables: `"$variable"`
- Use `local` for function variables
- Error messages to stderr: `echo "Error" >&2`
- Exit codes: 0 for success, 1 for general errors

### Function Naming

- Use `snake_case` for function names
- Descriptive names: `detect_clipboard_tool()`, `execute_clipboard_operation()`
- Helper functions prefixed with underscore: `_check_clipboard_empty()`

### Error Handling

- Always check command availability before use
- Provide fallback mechanisms
- Clear error messages with installation hints
- Respect the `-quiet` flag for suppressing errors

## Implementation Requirements

### Core Features

1. **xclip Compatibility**
   - Support `-i`, `-o`, `-selection`, `-t`, `-d`, `-version`, `-help`, `-quiet`
   - Handle both short and long options (`-i`/`--in`)
   - Validate argument combinations

2. **Tool Detection**
   - Prioritize: win32yank.exe → win32yoink.exe
   - Graceful fallback between tools
   - Clear error when no tools available

3. **Selection Handling**
   - Map `CLIPBOARD` selection directly
   - Map `PRIMARY` selection with warning (Windows doesn't support it)
   - Default to `CLIPBOARD` selection

4. **Clipboard Operations**
   - Handle stdin/stdout redirection
   - Process empty clipboard correctly
   - Remove trailing newlines and carriage returns
   - Detect and filter help text from tool output

### Edge Cases

- Empty clipboard should return empty string, not help text
- Handle special characters and Unicode (UTF-8)
- Multi-line text support
- Tool-specific error messages filtering
- Permission denied scenarios

## Security Considerations

- No execution of user input as code
- Sanitize clipboard content (remove control characters if needed)
- Handle large clipboard content gracefully
- No credential storage or transmission

## Deployment

### Installation Methods

1. **Manual Installation**
   ```bash
   wget https://raw.githubusercontent.com/ball6847/xclip-win32yank-wrapper/main/xclip
   chmod +x xclip
   mkdir -p ~/.local/bin
   mv xclip ~/.local/bin/
   ```

2. **Package Manager** (future)
   - Consider Chocolatey for Windows
   - Consider AUR for Arch Linux
   - Consider Homebrew for macOS (if WSL support needed)

### Dependencies Installation

```bash
# Install win32yank (primary recommendation)
# Download from: https://github.com/equalsraf/win32yank

# Alternative: Install win32yoink
# Download from: https://github.com/equalsraf/win32yoink
```

## Contributing Guidelines

1. Follow existing code style and patterns
2. Add tests for new features
3. Update documentation for changes
4. Test on multiple Windows versions
5. Verify pyperclip compatibility
6. Consider backward compatibility

## References

- **Design Document:** `XCLIP_SHELL_WRAPPER_DESIGN.md` (comprehensive implementation guide)
- **Pyperclip Integration:** https://github.com/asweigart/pyperclip
- **Win32yank:** https://github.com/equalsraf/win32yank
- **Win32yoink:** https://github.com/equalsraf/win32yoink
