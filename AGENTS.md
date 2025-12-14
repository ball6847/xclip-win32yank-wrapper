# Xclip Shell Wrapper - Technical Reference

## Technical Constraints

### Platform Requirements
- **Primary Platform:** Windows (WSL - Windows Subsystem for Linux)
- **Shell Environment:** Bash shell scripting
- **Python Version:** Python 3.x (for testing and compatibility layer)

### Dependency Constraints
- **Primary Clipboard Tool:** `win32yank.exe` (required for full functionality)
- **Fallback Clipboard Tool:** `win32yoink.exe` (optional, used if win32yank.exe not available)
- **Python Dependency:** `pyperclip==1.11.0` (for compatibility testing)

### Implementation Constraints
- **Shell Scripting Standards:**
  - Must use `#!/bin/bash` shebang
  - Must follow POSIX-compatible syntax where possible
  - Must use `[[ ]]` for conditional expressions
  - Must quote variables: `"$variable"`
  - Must use `local` for function variables
  - Error messages must go to stderr: `echo "Error" >&2`
  - Exit codes: 0 for success, 1 for general errors

- **Function Naming:**
  - Must use `snake_case` for function names
  - Helper functions must be prefixed with underscore: `_check_clipboard_empty()`

- **Error Handling:**
  - Must check command availability before use
  - Must provide fallback mechanisms
  - Must provide clear error messages with installation hints
  - Must respect the `-quiet` flag for suppressing errors

### Security Constraints
- Must not execute user input as code
- Must sanitize clipboard content (remove control characters if needed)
- Must handle large clipboard content gracefully
- Must not store or transmit credentials

## Technical Implementation Details

### Core Features
- **xclip Compatibility:**
  - Must support `-i`, `-o`, `-selection`, `-t`, `-d`, `-version`, `-help`, `-quiet`
  - Must handle both short and long options (`-i`/`--in`)
  - Must validate argument combinations

- **Tool Detection:**
  - Must prioritize: win32yank.exe → win32yoink.exe
  - Must provide graceful fallback between tools
  - Must provide clear error when no tools available

- **Selection Handling:**
  - Must map `CLIPBOARD` selection directly
  - Must map `PRIMARY` selection with warning (Windows doesn't support it)
  - Must default to `CLIPBOARD` selection

- **Clipboard Operations:**
  - Must handle stdin/stdout redirection
  - Must process empty clipboard correctly
  - Must remove trailing newlines and carriage returns
  - Must detect and filter help text from tool output

### Edge Cases
- Empty clipboard must return empty string, not help text
- Must handle special characters and Unicode (UTF-8)
- Must support multi-line text
- Must filter tool-specific error messages
- Must handle permission denied scenarios

## Development Setup

### Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Testing
```bash
# Shell wrapper tests
chmod +x test_xclip_wrapper.sh
./test_xclip_wrapper.sh

# Pyperclip compatibility tests
source venv/bin/activate
python test_pyperclip_compatibility.py
```

### Build Process
```bash
# Make executable
chmod +x xclip

# Install to PATH
mkdir -p ~/.local/bin
cp xclip ~/.local/bin/
```
