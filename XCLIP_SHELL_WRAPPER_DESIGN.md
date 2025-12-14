# Xclip Shell Wrapper Design

## Overview

This document outlines the design for a shell script wrapper that provides xclip compatibility for Windows clipboard utilities. The wrapper will support both `win32yank.exe` (primary) and `win32yoink.exe` (fallback) with the following features:

1. Process the `-selection` flag that Windows clipboard tools don't support
2. Pass through `-i` and `-o` flags to the appropriate Windows clipboard tool
3. Add additional features needed by pyperclip
4. Handle edge cases and error conditions
5. Provide fallback mechanisms between different Windows clipboard utilities

## Problem Statement

Windows clipboard utilities (`win32yank.exe` and `win32yoink.exe`) provide basic clipboard functionality but lack:

- Support for the `-selection` flag (CLIPBOARD/PRIMARY selection)
- Proper handling of empty clipboard
- Consistent behavior with standard xclip
- Cross-tool compatibility

Pyperclip expects standard xclip behavior, which includes these features. This wrapper provides a unified interface that works with multiple Windows clipboard tools.

## Design Goals

1. **100% xclip compatibility** - Support all xclip command-line options used by pyperclip
2. **Minimal overhead** - Fast execution with minimal shell overhead
3. **Robust error handling** - Clear error messages for debugging
4. **Multi-tool support** - Work with both win32yank (primary) and win32yoink (fallback)
5. **Backward compatibility** - Maintain compatibility with existing installations
6. **Easy deployment** - Simple shell script that can be dropped in place

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Xclip Shell Wrapper                        │
│                                                             │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │  Arg Parser  │───▶│  Selection      │───▶│  Tool       │  │
│  │  (xclip args)│   │  Handler        │   │  Selector   │  │
│  └─────────────┘    └─────────────────┘    └─────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                 Windows Clipboard Tools              │  │
│  │  ┌─────────────┐    ┌─────────────┐                    │  │
│  │  │ win32yank   │    │ win32yoink  │                    │  │
│  │  │ (primary)   │    │ (fallback)  │                    │  │
│  │  └─────────────┘    └─────────────┘                    │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                 Additional Features                  │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌──────────┐  │  │
│  │  │  Empty      │    │  Version    │    │  Help    │  │  │
│  │  │  Clipboard  │    │  Info       │    │  Text    │  │  │
│  │  └─────────────┘    └─────────────┘    └──────────┘  │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. Argument Parser

**Responsibilities:**

- Parse command-line arguments to match xclip interface
- Validate arguments and provide helpful error messages
- Support both positional and named arguments

**Supported xclip options:**

- `-i` / `--in`: Read from stdin and copy to clipboard
- `-o` / `--out`: Read from clipboard and output to stdout
- `-selection c`: Use CLIPBOARD selection (default)
- `-selection p`: Use PRIMARY selection
- `-t TARGET`: Specify target type (e.g., UTF8_STRING, TEXT)
- `-d DISPLAY`: Specify X display (ignored, for compatibility)
- `-version`: Show version information
- `-help`: Show help text
- `-quiet`: Suppress error messages

### 2. Tool Selection Layer

**Responsibilities:**

- Detect available Windows clipboard tools
- Prioritize win32yank.exe as primary tool
- Fallback to win32yoink.exe if win32yank is not available
- Provide consistent interface regardless of underlying tool

**Implementation:**

```bash
# Tool detection and selection
detect_clipboard_tool() {
    # Try win32yank first (primary)
    if command -v win32yank.exe >/dev/null 2>&1; then
        echo "win32yank.exe"
        return 0
    fi
    
    # Fallback to win32yoink
    if command -v win32yoink.exe >/dev/null 2>&1; then
        echo "win32yoink.exe"
        return 0
    fi
    
    return 1
}
```

**Usage in main script:**

```bash
# Detect available clipboard tool
CLIPBOARD_TOOL=$(detect_clipboard_tool)
if [[ $? -ne 0 ]]; then
    echo "Error: No compatible clipboard tool found (win32yank or win32yoink)" >&2
    exit 1
fi
```

### 3. Selection Handler

**Responsibilities:**

- Handle the `-selection` flag that Windows clipboard tools don't support
- Map X11 selections to Windows clipboard
- Provide fallback behavior for PRIMARY selection

**Implementation:**

```bash
# Handle selection
case "$SELECTION" in
    "c")
        # CLIPBOARD selection - use Windows clipboard
        CLIPBOARD_TYPE="clipboard"
        ;;
    "p")
        # PRIMARY selection - map to Windows clipboard
        # Note: Windows doesn't have PRIMARY selection, so we use CLIPBOARD
        if [[ $QUIET == false ]]; then
            echo "Warning: PRIMARY selection not supported on Windows, using CLIPBOARD" >&2
        fi
        CLIPBOARD_TYPE="clipboard"
        ;;
    *)
        echo "Error: Invalid selection type" >&2
        exit 1
        ;;
esac
```

### 4. Multi-Tool Integration Layer

**Responsibilities:**

- Execute the appropriate Windows clipboard tool based on availability
- Handle stdin/stdout redirection consistently across tools
- Process return codes and errors
- Provide fallback mechanisms between tools

**Implementation:**

```bash
# Execute clipboard operation with tool-specific handling
execute_clipboard_operation() {
    local tool="$1"
    local operation="$2"  # "in" or "out"
    
    if [[ "$operation" == "in" ]]; then
        # Copy to clipboard
        if [[ "$tool" == "win32yank.exe" ]]; then
            if ! win32yank.exe -i 2>/dev/null; then
                return 1
            fi
        elif [[ "$tool" == "win32yoink.exe" ]]; then
            if ! win32yoink.exe -i 2>/dev/null; then
                return 1
            fi
        fi
        
    elif [[ "$operation" == "out" ]]; then
        # Read from clipboard
        local output=""
        
        if [[ "$tool" == "win32yank.exe" ]]; then
            output=$(win32yank.exe -o 2>/dev/null || echo "")
        elif [[ "$tool" == "win32yoink.exe" ]]; then
            output=$(win32yoink.exe -o 2>/dev/null || echo "")
        fi
        
        # Check if output is empty or contains tool help text
        if [[ -z "$output" || "$output" == "Usage:"* || "$output" == "win32yank"* || "$output" == "win32yoink"* ]]; then
            # Try fallback tools
            if [[ "$tool" == "win32yank.exe" ]]; then
                # Try win32yoink as fallback
                if command -v win32yoink.exe >/dev/null 2>&1; then
                    output=$(win32yoink.exe -o 2>/dev/null || echo "")
                fi
            fi
        fi
        
        # Remove trailing newlines that some tools add
        output=$(echo "$output" | sed 's/\r$//;s/\n$//')
        
        echo "$output"
    fi
}

# Execute operation
if [[ $INPUT == true ]]; then
    # Copy to clipboard with fallback
    if ! execute_clipboard_operation "$CLIPBOARD_TOOL" "in"; then
        # Try fallback tools
        if [[ "$CLIPBOARD_TOOL" == "win32yank.exe" && command -v win32yoink.exe >/dev/null 2>&1 ]]; then
            if execute_clipboard_operation "win32yoink.exe" "in"; then
                exit 0
            fi
        fi
        
        if [[ $QUIET == false ]]; then
            echo "Error: Failed to copy to clipboard with all available tools" >&2
        fi
        exit 1
    fi
elif [[ $OUTPUT == true ]]; then
    # Read from clipboard with fallback
    execute_clipboard_operation "$CLIPBOARD_TOOL" "out"
fi
```

### 5. Additional Features

#### Empty Clipboard Handling

**Problem:** When the clipboard is empty, Windows clipboard tools may output help text or error messages.

**Solution:** Detect this and return empty string instead.

**Implementation:**

```bash
# Check if clipboard is empty
check_clipboard_empty() {
    local output
    
    # Try primary tool first
    if command -v win32yank.exe >/dev/null 2>&1; then
        output=$(win32yank.exe -o 2>/dev/null || echo "")
    elif command -v win32yoink.exe >/dev/null 2>&1; then
        output=$(win32yoink.exe -o 2>/dev/null || echo "")
    fi

    # Check if output is help text or error message
    if [[ "$output" == "Usage:"* ]] || [[ "$output" == "win32yank"* ]] || [[ "$output" == "win32yoink"* ]]; then
        return 0  # Empty
    fi

    # Check if output is just whitespace
    if [[ -z "$(echo "$output" | tr -d ' \t\r\n')" ]]; then
        return 0  # Empty
    fi

    return 1  # Not empty
}
```

#### Help Text

**Implementation:**

```bash
show_help() {
    cat << 'EOF'
Usage: xclip [OPTIONS]

Options:
  -i, --in              Read from stdin and copy to clipboard
  -o, --out             Read from clipboard and output to stdout
  -selection SEL        Specify selection (c=CLIPBOARD, p=PRIMARY)
  -t, -target TARGET    Specify target type (default: UTF8_STRING)
  -d, -display DISPLAY  Specify X display (ignored)
  -version              Show version information
  -help                 Show this help text
  -quiet                 Suppress error messages

Examples:
  # Copy from stdin to clipboard
  echo "Hello" | xclip -i

  # Paste from clipboard to stdout
  xclip -o

  # Copy with specific selection
  echo "Hello" | xclip -selection c -i

  # Paste with specific selection
  xclip -selection p -o
EOF
}
```

## Complete Implementation

Here's the complete shell script with multi-tool support:

```bash
#!/bin/bash

# Xclip wrapper for Windows clipboard tools
# Provides xclip compatibility on Windows/WSL
# Supports win32yank.exe (primary) and win32yoink.exe (fallback)

# Default values
INPUT=false
OUTPUT=false
SELECTION="c"  # c = CLIPBOARD, p = PRIMARY
TARGET="UTF8_STRING"
QUIET=false

# Tool detection and selection
detect_clipboard_tool() {
    # Try win32yank first (primary)
    if command -v win32yank.exe >/dev/null 2>&1; then
        echo "win32yank.exe"
        return 0
    fi
    
    # Fallback to win32yoink
    if command -v win32yoink.exe >/dev/null 2>&1; then
        echo "win32yoink.exe"
        return 0
    fi
    
    return 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -i|--in)
            INPUT=true
            shift
            ;;
        -o|--out)
            OUTPUT=true
            shift
            ;;
        -selection)
            if [[ "$2" == "c" || "$2" == "p" ]]; then
                SELECTION="$2"
            else
                echo "Error: Invalid selection. Use 'c' for CLIPBOARD or 'p' for PRIMARY" >&2
                exit 1
            fi
            shift 2
            ;;
        -t|-target)
            TARGET="$2"
            shift 2
            ;;
        -d|-display)
            # Ignore display parameter (for compatibility)
            shift 2
            ;;
        -version)
            echo "xclip wrapper v2.0 (win32yank/win32yoink backend)"
            exit 0
            ;;
        -help)
            show_help
            exit 0
            ;;
        -quiet)
            QUIET=true
            shift
            ;;
        *)
            echo "Error: Unknown option $1" >&2
            exit 1
            ;;
    esac
done

# Validate arguments
if [[ $INPUT == false && $OUTPUT == false ]]; then
    echo "Error: Must specify either -i or -o" >&2
    exit 1
fi

if [[ $INPUT == true && $OUTPUT == true ]]; then
    echo "Error: Cannot specify both -i and -o" >&2
    exit 1
fi

# Detect available clipboard tool
CLIPBOARD_TOOL=$(detect_clipboard_tool)
if [[ $? -ne 0 ]]; then
    echo "Error: No compatible clipboard tool found (win32yank or win32yoink)" >&2
    exit 1
fi

# Show help function
show_help() {
    cat << 'EOF'
Usage: xclip [OPTIONS]

Options:
  -i, --in              Read from stdin and copy to clipboard
  -o, --out             Read from clipboard and output to stdout
  -selection SEL        Specify selection (c=CLIPBOARD, p=PRIMARY)
  -t, -target TARGET    Specify target type (default: UTF8_STRING)
  -d, -display DISPLAY  Specify X display (ignored)
  -version              Show version information
  -help                 Show this help text
  -quiet                 Suppress error messages

Examples:
  # Copy from stdin to clipboard
  echo "Hello" | xclip -i

  # Paste from clipboard to stdout
  xclip -o

  # Copy with specific selection
  echo "Hello" | xclip -selection c -i

  # Paste with specific selection
  xclip -selection p -o
EOF
}

# Handle selection
case "$SELECTION" in
    "c")
        # CLIPBOARD selection - use Windows clipboard
        CLIPBOARD_TYPE="clipboard"
        ;;
    "p")
        # PRIMARY selection - map to Windows clipboard
        # Note: Windows doesn't have PRIMARY selection, so we use CLIPBOARD
        if [[ $QUIET == false ]]; then
            echo "Warning: PRIMARY selection not supported on Windows, using CLIPBOARD" >&2
        fi
        CLIPBOARD_TYPE="clipboard"
        ;;
    *)
        echo "Error: Invalid selection type" >&2
        exit 1
        ;;
esac

# Execute clipboard operation with tool-specific handling
execute_clipboard_operation() {
    local tool="$1"
    local operation="$2"  # "in" or "out"
    
    if [[ "$operation" == "in" ]]; then
        # Copy to clipboard
        if [[ "$tool" == "win32yank.exe" ]]; then
            if ! win32yank.exe -i 2>/dev/null; then
                return 1
            fi
        elif [[ "$tool" == "win32yoink.exe" ]]; then
            if ! win32yoink.exe -i 2>/dev/null; then
                return 1
            fi
        fi
        
    elif [[ "$operation" == "out" ]]; then
        # Read from clipboard
        local output=""
        
        if [[ "$tool" == "win32yank.exe" ]]; then
            output=$(win32yank.exe -o 2>/dev/null || echo "")
        elif [[ "$tool" == "win32yoink.exe" ]]; then
            output=$(win32yoink.exe -o 2>/dev/null || echo "")
        fi
        
        # Check if output is empty or contains tool help text
        if [[ -z "$output" || "$output" == "Usage:"* || "$output" == "win32yank"* || "$output" == "win32yoink"* ]]; then
            # Try fallback tools
            if [[ "$tool" == "win32yank.exe" ]]; then
                # Try win32yoink as fallback
                if command -v win32yoink.exe >/dev/null 2>&1; then
                    output=$(win32yoink.exe -o 2>/dev/null || echo "")
                fi
            fi
        fi
        
        # Remove trailing newlines that some tools add
        output=$(echo "$output" | sed 's/\r$//;s/\n$//')
        
        echo "$output"
    fi
}

# Execute operation
if [[ $INPUT == true ]]; then
    # Copy to clipboard with fallback
    if ! execute_clipboard_operation "$CLIPBOARD_TOOL" "in"; then
        # Try fallback tools
        if [[ "$CLIPBOARD_TOOL" == "win32yank.exe" && command -v win32yoink.exe >/dev/null 2>&1 ]]; then
            if execute_clipboard_operation "win32yoink.exe" "in"; then
                exit 0
            fi
        fi
        
        if [[ $QUIET == false ]]; then
            echo "Error: Failed to copy to clipboard with all available tools" >&2
        fi
        exit 1
    fi
elif [[ $OUTPUT == true ]]; then
    # Read from clipboard with fallback
    execute_clipboard_operation "$CLIPBOARD_TOOL" "out"
fi
```

## Deployment

### Installation

1. Save the script as `xclip` (no extension)
2. Make it executable:
   ```bash
   chmod +x xclip
   ```
3. Place it in your PATH (e.g., `/usr/local/bin/`)

## Testing

### Test Cases

1. **Basic copy/paste**

   ```bash
   echo "Hello World" | xclip -i
   xclip -o
   ```

2. **Selection handling**

   ```bash
   echo "Test" | xclip -selection c -i
   xclip -selection p -o
   ```

3. **Empty clipboard**

   ```bash
   xclip -o  # Should return empty string, not help text
   ```

4. **Special characters**

   ```bash
   echo "Special: @#$%^&*()" | xclip -i
   xclip -o
   ```

5. **Unicode**

   ```bash
   echo "Unicode: 你好 🎉" | xclip -i
   xclip -o
   ```

6. **Multi-line text**
   ```bash
   echo -e "Line 1\nLine 2\nLine 3" | xclip -i
   xclip -o
   ```

7. **Tool fallback testing**
   ```bash
   # Test with win32yank available
   echo "Test" | xclip -i
   xclip -o
   
   # Test with only win32yoink available
   # (remove win32yank from PATH temporarily)
   echo "Test2" | xclip -i
   xclip -o
   ```

### Test Script

```bash
#!/bin/bash

echo "Testing xclip wrapper with multi-tool support..."
echo "================================================"

# Test 1: Basic copy/paste
echo -e "\nTest 1: Basic copy/paste"
echo "Hello World" | ./xclip -i
result=$(./xclip -o)
if [[ "$result" == "Hello World" ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Expected 'Hello World', got '$result'"
fi

# Test 2: Selection handling
echo -e "\nTest 2: Selection handling"
echo "Test" | ./xclip -selection c -i
result=$(./xclip -selection p -o)
if [[ "$result" == "Test" ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Expected 'Test', got '$result'"
fi

# Test 3: Empty clipboard
echo -e "\nTest 3: Empty clipboard"
result=$(./xclip -o)
if [[ -z "$result" || "$result" == "Usage:"* ]]; then
    echo "✗ FAIL: Got unexpected output: '$result'"
else
    echo "✓ PASS"
fi

# Test 4: Special characters
echo -e "\nTest 4: Special characters"
special="Special: @#$%^&*()"
echo "$special" | ./xclip -i
result=$(./xclip -o)
if [[ "$result" == "$special" ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Expected '$special', got '$result'"
fi

# Test 5: Unicode
echo -e "\nTest 5: Unicode"
unicode="Unicode: 你好 🎉"
echo "$unicode" | ./xclip -i
result=$(./xclip -o)
if [[ "$result" == "$unicode" ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Expected '$unicode', got '$result'"
fi

# Test 6: Multi-tool fallback (if both tools are available)
echo -e "\nTest 6: Tool detection and fallback"
if command -v win32yank.exe >/dev/null 2>&1; then
    echo "✓ win32yank.exe detected (primary tool)"
else
    echo "- win32yank.exe not found"
fi

if command -v win32yoink.exe >/dev/null 2>&1; then
    echo "✓ win32yoink.exe detected (fallback tool)"
else
    echo "- win32yoink.exe not found"
fi



echo -e "\n================================================"
echo "Testing complete!"
```

## Compatibility with Pyperclip

### How Pyperclip Uses Xclip

Pyperclip calls xclip with the following patterns:

1. **Copy operation:**

   ```python
   subprocess.Popen(['xclip', '-selection', 'c'], stdin=subprocess.PIPE)
   ```

2. **Paste operation:**

   ```python
   subprocess.Popen(['xclip', '-selection', 'c', '-o'],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
   ```

3. **Availability check:**
   ```python
   pyperclip.paste()  # Just tries to paste
   ```

### Testing with Pyperclip

```python
import pyperclip
import subprocess

# Test 1: Set xclip as clipboard mechanism
pyperclip.set_clipboard('xclip')
print(f"Copy function: {pyperclip.copy.__name__}")
print(f"Paste function: {pyperclip.paste.__name__}")

# Test 2: Basic copy/paste
pyperclip.copy("Test from pyperclip")
result = pyperclip.paste()
print(f"Result: {result}")
assert result == "Test from pyperclip", f"Expected 'Test from pyperclip', got '{result}'"

# Test 3: Unicode
pyperclip.copy("Unicode: 你好 🎉")
result = pyperclip.paste()
print(f"Unicode result: {result}")
assert result == "Unicode: 你好 🎉", f"Expected 'Unicode: 你好 🎉', got '{result}'"

print("All pyperclip tests passed!")
```

## Error Handling

### Common Error Scenarios

1. **No compatible clipboard tool found**
   - Check for win32yank.exe and win32yoink.exe
   - Show clear error message with installation instructions

2. **Clipboard permission denied**
   - Show user-friendly error message
   - Suggest running as administrator if needed

3. **Invalid arguments**
   - Show help text with usage examples

4. **Empty clipboard**
   - Return empty string (not help text)

5. **Tool-specific failures**
   - Fallback to alternative tools with clear error reporting

### Error Messages

```bash
# Error: No compatible clipboard tool found
if ! command -v win32yank.exe >/dev/null 2>&1 && ! command -v win32yoink.exe >/dev/null 2>&1; then
    echo "Error: No compatible clipboard tool found" >&2
    echo "Please install win32yank.exe or win32yoink.exe" >&2
    echo "Installation options:" >&2
    echo "  - win32yank: https://github.com/equalsraf/win32yank" >&2
    echo "  - win32yoink: https://github.com/equalsraf/win32yoink" >&2
    exit 1
fi

# Error: Clipboard permission denied
if [[ $? -eq 13 ]]; then
    echo "Error: Permission denied accessing clipboard" >&2
    echo "Try running as administrator or check clipboard permissions" >&2
    exit 1
fi

# Error: All tools failed
if [[ $QUIET == false ]]; then
    echo "Error: Failed to copy to clipboard with all available tools" >&2
    echo "Tried: win32yank.exe, win32yoink.exe" >&2
    exit 1
fi
```
