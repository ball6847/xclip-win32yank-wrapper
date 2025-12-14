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

## Testing Framework

### Test Files

**`test_pyperclip_compatibility.py`**
- **Approach**: Table-driven testing with pytest parameterization
- **Dependencies**: pytest, pyperclip
- **Use Case**: Professional development, CI/CD, contributions
- **Status**: Active, recommended for all use
- **Features**:
  - All test cases defined in `TEST_CASES` list
  - Better organization and readability
  - Easier to add new tests
  - Better error reporting
  - Fixtures for setup/teardown

**Pros:**
- **Table-driven approach**: All test cases defined in one place
- **More readable**: Test cases clearly listed as data
- **Easier to maintain**: Add new tests by adding to the table
- **Better reporting**: pytest provides excellent test output
- **Fixtures**: Setup/teardown logic centralized

**Cons:**
- Requires pytest installation (`pip install pytest`)
- Slightly more complex setup

### Testing Approach Comparison

| Feature | Original Test | Improved Test |
|---------|--------------|---------------|
| Approach | Procedural | Table-driven |
| Dependencies | pyperclip | pytest, pyperclip |
| Readability | Good | Excellent |
| Maintainability | Moderate | High |
| Test Addition | Copy-paste code | Add to table |
| Reporting | Basic | Excellent |
| Fixtures | No | Yes |
| Selective Testing | No | Yes |
| CI/CD Integration | Basic | Excellent |

### Test Case Structure

The improved test uses a table-driven approach where test cases are defined as:

```python
TEST_CASES = [
    # (test_name, input_text, expected_text, should_contain_lines)
    ("Basic copy/paste", "Test from pyperclip", "Test from pyperclip", None),
    ("Unicode handling", "Unicode: 你好 🎉", "Unicode: 你好 🎉", None),
    ("Multi-line text", "Line 1\nLine 2\nLine 3", None, ["Line 1", "Line 2", "Line 3"]),
]
```

**Parameters:**
- `test_name`: Descriptive name of the test
- `input_text`: Text to copy to clipboard
- `expected_text`: Expected text when pasting (for exact match tests)
- `should_contain_lines`: List of lines to check for (for multi-line tests)

### Adding New Tests

To add a new test case:

1. Add it to the `TEST_CASES` list
2. Choose the appropriate verification method:
   - For exact match: use `expected_text` parameter
   - For multi-line: use `should_contain_lines` parameter

Example:
```python
TEST_CASES = [
    # ... existing tests ...
    ("Long text", "A" * 1000, "A" * 1000, None),  # Test long text
    ("Emoji only", "🎉🎊🎈", "🎉🎊🎈", None),  # Test emoji
]
```

### Running Tests

#### Using pytest (Recommended)
```bash
# Install pytest if needed
pip install pytest

# Run all tests
pytest test_pyperclip_compatibility.py -v

# Run specific test
pytest test_pyperclip_compatibility.py::test_direct_xclip_calls -v

# Run with verbose output
pytest test_pyperclip_compatibility.py -v

# Run with detailed output
pytest test_pyperclip_compatibility.py -vv
```

#### Using Python directly
```bash
# Run the test file directly (will use pytest internally)
python test_pyperclip_compatibility.py
```

### Test Coverage

The tests cover:
- Basic copy/paste operations
- Unicode and special character handling
- Multi-line text
- Empty clipboard
- Direct xclip command calls
- Special characters

### Best Practices

1. **For New Development**: Use `test_pyperclip_compatibility.py`
2. **For CI/CD Pipelines**: Use pytest with verbose output
3. **For Adding Tests**: Add to `TEST_CASES` list in improved test file
4. **For Debugging**: Use `pytest -vv` for detailed output
5. **For Selective Testing**: Use `pytest test_name -v`
6. **Keep tests independent**: Each test should work regardless of order
7. **Use descriptive names**: Test names should clearly indicate what's being tested
8. **Test edge cases**: Empty strings, long text, special characters
9. **Test error conditions**: What happens when clipboard is unavailable?
10. **Keep tests fast**: Tests should run quickly for good developer experience

### Debugging Tests

If a test fails:

1. Run with verbose output: `pytest -vv`
2. Check the exact error message
3. Add debug prints if needed
4. Run individual test: `pytest test_name -v`

### Continuous Integration

For CI/CD pipelines, add this to your workflow:

```yaml
- name: Run tests
  run: |
    pip install pytest pyperclip
    pytest test_pyperclip_compatibility.py -v
```

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

#### All Tests (Python-based)

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

### Build Process
```bash
# Make executable
chmod +x xclip

# Install to PATH
mkdir -p ~/.local/bin
cp xclip ~/.local/bin/
```
