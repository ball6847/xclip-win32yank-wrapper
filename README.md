# Xclip Shell Wrapper for Windows

A shell script wrapper that provides 100% xclip compatibility for Windows clipboard utilities, specifically supporting `win32yank.exe` (primary) and `win32yoink.exe` (fallback).

## Overview

This project solves the problem of Windows clipboard utilities lacking support for the `-selection` flag and other xclip features that pyperclip and other Linux tools expect. The wrapper provides a unified interface that works with multiple Windows clipboard tools.

## Features

✅ **100% xclip compatibility** - Supports all xclip command-line options
✅ **Multi-tool support** - Works with win32yank.exe and win32yoink.exe
✅ **Selection handling** - Maps X11 selections (CLIPBOARD/PRIMARY) to Windows clipboard
✅ **Robust error handling** - Clear error messages with installation instructions
✅ **Pyperclip compatible** - Works seamlessly with the pyperclip library
✅ **Unicode support** - Proper handling of UTF-8 characters and emojis
✅ **Multi-line text** - Correct processing of newlines
✅ **Empty clipboard handling** - Returns empty string instead of help text
✅ **Fallback mechanisms** - Graceful degradation when tools fail

## Installation

### Quick Install

```bash
# Download the script
wget https://raw.githubusercontent.com/ball6847/xclip-win32yank-wrapper/main/xclip

# Make it executable
chmod +x xclip

# Place in PATH
mkdir -p ~/.local/bin
cp xclip ~/.local/bin/
```

### Manual Install

1. Clone or download this repository
2. Make the script executable: `chmod +x xclip`
3. Copy to your PATH: `cp xclip ~/.local/bin/`

## Dependencies

You need at least one of these Windows clipboard tools:

- **Primary**: [win32yank.exe](https://github.com/equalsraf/win32yank) (recommended)
- **Fallback**: [win32yoink.exe](https://github.com/equalsraf/win32yoink)

### Installing win32yank (recommended)

```bash
# Download from GitHub releases
wget https://github.com/equalsraf/win32yank/releases/download/v0.0.4/win32yank.exe
chmod +x win32yank.exe
cp win32yank.exe ~/.local/bin/
```

## Usage

### Basic Copy/Paste

```bash
# Copy to clipboard
echo "Hello World" | xclip -i

# Paste from clipboard
xclip -o
```

### Selection Handling

```bash
# Copy with CLIPBOARD selection (default)
echo "Test" | xclip -selection c -i

# Paste with PRIMARY selection (mapped to CLIPBOARD on Windows)
xclip -selection p -o
```

### Unicode and Special Characters

```bash
# Unicode text
echo "Unicode: 你好 🎉" | xclip -i
xclip -o

# Special characters
echo "Special: @#$%^&*()" | xclip -i
xclip -o
```

### Multi-line Text

```bash
# Multi-line text
echo -e "Line 1\nLine 2\nLine 3" | xclip -i
xclip -o
```

### Pyperclip Integration

```python
import pyperclip

# Set xclip as the clipboard mechanism
pyperclip.set_clipboard('xclip')

# Copy and paste
pyperclip.copy("Test from pyperclip")
print(pyperclip.paste())
```

### Help and Version

```bash
# Show help
xclip -help

# Show version
xclip -version
```

## Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `-i`, `--in` | Read from stdin and copy to clipboard | `echo "text" \| xclip -i` |
| `-o`, `--out` | Read from clipboard and output to stdout | `xclip -o` |
| `-selection SEL` | Specify selection (c=CLIPBOARD, p=PRIMARY) | `xclip -selection c -i` |
| `-t`, `-target TARGET` | Specify target type (default: UTF8_STRING) | `xclip -t UTF8_STRING -i` |
| `-d`, `-display DISPLAY` | Specify X display (ignored for compatibility) | `xclip -d :0 -i` |
| `-version` | Show version information | `xclip -version` |
| `-help` | Show help text | `xclip -help` |
| `-quiet` | Suppress error messages | `xclip -quiet -i` |

## Testing

### Continuous Integration

Tests are automatically run on every push and pull request to the main branch using GitHub Actions. The workflow tests against multiple Python versions (3.8-3.12) to ensure compatibility.

### Test Files

**`tests/test_pyperclip_compatibility.py`**
- Table-driven testing with pytest parameterization
- Tests pyperclip integration
- All test cases defined in a single table

**`tests/test_xclip_wrapper.py`**
- Table-driven testing with pytest parameterization
- Tests direct xclip wrapper functionality
- All test cases defined in tables
- Comprehensive error handling tests

### Run All Tests

```bash
# Install dependencies
pip install pytest pyperclip

# Run all tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_pyperclip_compatibility.py -v

# Run specific test function
pytest tests/test_xclip_wrapper.py::test_clipboard_operations -v

# Run with detailed output
pytest -vv
```

## Error Handling

The wrapper provides clear, actionable error messages:

```
Error: No compatible clipboard tool found (win32yank or win32yoink)
Please install win32yank.exe or win32yoink.exe
Installation options:
  - win32yank: https://github.com/equalsraf/win32yank
  - win32yoink: https://github.com/equalsraf/win32yoink
```

## Compatibility

- **Platforms**: Windows, WSL (Windows Subsystem for Linux)
- **Shell**: Bash (tested with bash 5.1+)
- **Python**: Compatible with pyperclip library
- **Unicode**: Full UTF-8 support

## Implementation Details

See [XCLIP_SHELL_WRAPPER_DESIGN.md](XCLIP_SHELL_WRAPPER_DESIGN.md) for comprehensive design documentation.

## Development Setup

### Using Makefile (Recommended)

The project includes a Makefile to simplify common tasks:

```bash
# Show help
make help

# Setup virtual environment and install dependencies
make setup

# Run all tests
make test

# Run quick validation tests only
make test-quick

# Run comprehensive tests
make test-comprehensive

# Run pyperclip compatibility tests
make test-pyperclip

# Run xclip wrapper tests
make test-wrapper

# Clean up test cache
make clean
```

### Manual Setup

If you prefer not to use the Makefile, you can set up manually:

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Testing

#### Test Files (in `tests/` directory)

**`tests/test_pyperclip_compatibility.py`**
- Table-driven testing with pytest parameterization
- Tests pyperclip integration
- All test cases defined in a single table

**`tests/test_xclip_wrapper.py`**
- Table-driven testing with pytest parameterization
- Tests direct xclip wrapper functionality
- All test cases defined in tables
- Comprehensive error handling tests

**`tests/test_comprehensive.py`**
- Comprehensive test suite (converted from comprehensive_test.sh)
- 8 parameterized clipboard operation tests
- 3 parameterized error handling tests
- Tests for long text, whitespace, and edge cases

**`tests/test_simple.py`**
- Simple test suite (converted from simple_test.sh)
- 4 basic clipboard operation tests
- 2 error handling tests
- Quick validation of core functionality

#### Run All Tests

```bash
# Activate virtual environment first!
source venv/bin/activate

# Run all tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_pyperclip_compatibility.py -v

# Run specific test function
pytest tests/test_xclip_wrapper.py::test_clipboard_operations -v

# Run with detailed output
pytest -vv
```

## Contributing

1. Follow existing code style and patterns
2. Add tests for new features
3. Update documentation for changes
4. Test on multiple Windows versions
5. Verify pyperclip compatibility
6. Consider backward compatibility

## License

This project is open source and available for use.

## Support

For issues and questions, please refer to the [AGENTS.md](AGENTS.md) file for AI agent guidance.

## Files

- `xclip` - Main shell script wrapper
- `Makefile` - Build automation and testing commands
- `tests/` - Directory containing all test files
  - `test_xclip_wrapper.py` - Comprehensive test suite (pytest)
  - `test_pyperclip_compatibility.py` - Pyperclip compatibility tests (pytest)
  - `test_comprehensive.py` - Comprehensive test suite (pytest)
  - `test_simple.py` - Simple test suite (pytest)
- `requirements.txt` - Python dependencies
- `XCLIP_SHELL_WRAPPER_DESIGN.md` - Detailed design documentation
- `PLAN.md` - Implementation plan and task tracking
- `AGENTS.md` - AI agent guide
- `IMPLEMENTATION_SUMMARY.md` - Implementation summary

## Success Criteria

✅ 100% xclip compatibility  
✅ Support for win32yank.exe and win32yoink.exe  
✅ Clear error messages with installation hints  
✅ Comprehensive testing framework  
✅ Pyperclip compatibility  
✅ Easy installation and usage  
✅ Multi-tool fallback mechanisms  
✅ Empty clipboard handling  
✅ Unicode and special character support  
✅ Multi-line text support  
✅ Selection flag handling  

All implementation tasks have been completed successfully!