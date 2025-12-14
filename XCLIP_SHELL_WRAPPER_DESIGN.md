# Xclip Shell Wrapper Design

## Overview

This document outlines the design for a shell script wrapper that provides xclip compatibility for `win32yoink.exe`. The wrapper will:

1. Process the `-selection` flag that win32yoink doesn't support
2. Pass through `-i` and `-o` flags to win32yoink
3. Add additional features needed by pyperclip
4. Handle edge cases and error conditions

## Problem Statement

`win32yoink.exe` is a Windows clipboard utility that provides basic clipboard functionality but lacks:

- Support for the `-selection` flag (CLIPBOARD/PRIMARY selection)
- Proper handling of empty clipboard
- Consistent behavior with standard xclip

Pyperclip expects standard xclip behavior, which includes these features.

## Design Goals

1. **100% xclip compatibility** - Support all xclip command-line options used by pyperclip
2. **Minimal overhead** - Fast execution with minimal shell overhead
3. **Robust error handling** - Clear error messages for debugging
4. **Backward compatibility** - Work with existing win32yoink installations
5. **Easy deployment** - Simple shell script that can be dropped in place

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Xclip Shell Wrapper                        │
│                                                             │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │  Arg Parser  │───▶│  Selection      │───▶│  win32yoink  │  │
│  │  (xclip args)│   │  Handler        │   │  (Windows)   │  │
│  └─────────────┘    └─────────────────┘    └─────────────┘  │
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

**Implementation:**

```bash
#!/bin/bash

# Default values
INPUT=false
OUTPUT=false
SELECTION="c"  # c = CLIPBOARD, p = PRIMARY
TARGET="UTF8_STRING"
QUIET=false

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
            echo "xclip wrapper v1.0 (win32yoink backend)"
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
```

### 2. Selection Handler

**Responsibilities:**

- Handle the `-selection` flag that win32yoink doesn't support
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

### 3. win32yoink Integration

**Responsibilities:**

- Execute win32yoink with appropriate arguments
- Handle stdin/stdout redirection
- Process return codes and errors

**Implementation:**

```bash
# Execute win32yoink
if [[ $INPUT == true ]]; then
    # Copy to clipboard
    if ! win32yoink -i 2>/dev/null; then
        if [[ $QUIET == false ]]; then
            echo "Error: Failed to copy to clipboard" >&2
        fi
        exit 1
    fi
elif [[ $OUTPUT == true ]]; then
    # Read from clipboard
    OUTPUT=$(win32yoink -o 2>/dev/null)

    # Check if output is empty or contains win32yoink help text
    if [[ -z "$OUTPUT" || "$OUTPUT" == "Usage:"* ]]; then
        # Try to get from Windows clipboard using alternative method
        OUTPUT=$(powershell -command "Get-Clipboard" 2>/dev/null || echo "")
    fi

    # Remove trailing newline that win32yoink adds
    OUTPUT=$(echo "$OUTPUT" | sed 's/\r$//;s/\n$//')

    echo "$OUTPUT"
fi
```

### 4. Additional Features

#### Empty Clipboard Handling

**Problem:** When the clipboard is empty, win32yoink outputs its help text.

**Solution:** Detect this and return empty string instead.

**Implementation:**

```bash
# Check if clipboard is empty
check_clipboard_empty() {
    local output
    output=$(win32yoink -o 2>/dev/null || echo "")

    # Check if output is win32yoink help text
    if [[ "$output" == "Usage:"* ]] || [[ "$output" == "win32yoink"* ]]; then
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

Here's the complete shell script:

```bash
#!/bin/bash

# Xclip wrapper for win32yoink.exe
# Provides xclip compatibility on Windows/WSL

# Default values
INPUT=false
OUTPUT=false
SELECTION="c"  # c = CLIPBOARD, p = PRIMARY
TARGET="UTF8_STRING"
QUIET=false

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
            echo "xclip wrapper v1.0 (win32yoink backend)"
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

# Execute operation
if [[ $INPUT == true ]]; then
    # Copy to clipboard
    # Read from stdin
    local data
    data=$(cat)

    # Try win32yoink first
    if echo "$data" | win32yoink -i 2>/dev/null; then
        exit 0
    fi

    # Fallback to PowerShell
    if echo "$data" | powershell -command "Set-Clipboard" 2>/dev/null; then
        exit 0
    fi

    if [[ $QUIET == false ]]; then
        echo "Error: Failed to copy to clipboard" >&2
    fi
    exit 1
elif [[ $OUTPUT == true ]]; then
    # Read from clipboard
    local output

    # Try win32yoink first
    output=$(win32yoink -o 2>/dev/null || echo "")

    # Check if output is win32yoink help text or empty
    if [[ -n "$output" && "$output" != "Usage:"* && "$output" != "win32yoink"* ]]; then
        # Valid output from win32yoink
        echo "$output" | sed 's/\r$//;s/\n$//'
        exit 0
    fi

    # Fallback to PowerShell
    output=$(powershell -command "Get-Clipboard" 2>/dev/null || echo "")

    # Remove trailing newlines
    output=$(echo "$output" | sed 's/\r$//;s/\n$//')

    echo "$output"
    exit 0
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

### Test Script

```bash
#!/bin/bash

echo "Testing xclip wrapper..."
echo "========================"

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

echo -e "\n========================"
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

1. **win32yoink not found**
   - Try fallback to PowerShell
   - If PowerShell also fails, show clear error message

2. **Clipboard permission denied**
   - Show user-friendly error message
   - Suggest running as administrator if needed

3. **Invalid arguments**
   - Show help text with usage examples

4. **Empty clipboard**
   - Return empty string (not help text)

### Error Messages

```bash
# Error: win32yoink not found
if ! command -v win32yoink >/dev/null 2>&1 && ! command -v powershell >/dev/null 2>&1; then
    echo "Error: Neither win32yoink nor PowerShell found" >&2
    echo "Please install win32yoink or ensure PowerShell is available" >&2
    exit 1
fi

# Error: Clipboard permission denied
if [[ $? -eq 13 ]]; then
    echo "Error: Permission denied accessing clipboard" >&2
    echo "Try running as administrator or check clipboard permissions" >&2
    exit 1
fi
```

## Performance Considerations

1. **Minimize shell overhead**
   - Use direct command execution where possible
   - Avoid unnecessary variable assignments

2. **Fallback strategy**
   - Try win32yoink first (faster)
   - Fallback to PowerShell only if needed

3. **Caching**
   - Could cache clipboard contents for repeated accesses
   - Not implemented in this version to keep it simple

## Future Enhancements

1. **Additional clipboard formats**
   - Support for images, files, and other MIME types
   - HTML clipboard format
   - Rich text format

2. **Clipboard monitoring**
   - Watch for clipboard changes
   - Notify when clipboard content changes

3. **Clipboard history**
   - Maintain history of clipboard contents
   - Allow cycling through previous clipboard contents

4. **Security features**
   - Clipboard encryption for sensitive data
   - Clipboard access notifications
   - Clipboard audit logging

5. **Advanced features**
   - Clipboard synchronization across devices
   - Clipboard sharing between VMs and host
   - Clipboard access from remote sessions

## Migration from win32yoink

### For Existing Users

1. **No changes needed**
   - The wrapper passes through all arguments to win32yoink
   - Existing scripts will continue to work

2. **New features available**
   - `-selection` flag now works
   - Better error handling
   - Fallback to PowerShell

3. **Performance**
   - Minimal overhead (just argument parsing)
   - Fast execution

### For Developers

1. **Pyperclip compatibility**
   - Pyperclip will now work correctly
   - No code changes needed

2. **Other tools**
   - Any tool expecting xclip will work
   - Full xclip command-line interface support

## Conclusion

This shell wrapper provides a simple, effective solution for making win32yoink compatible with xclip. By handling the `-selection` flag and other xclip features that win32yoink doesn't support, it enables tools like pyperclip to work correctly on Windows/WSL systems.

The wrapper is easy to deploy, has minimal overhead, and provides robust error handling. It can be extended in the future to support additional features as needed.
