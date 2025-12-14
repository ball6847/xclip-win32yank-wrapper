# Testing Guide

This guide explains the testing approach for the xclip-win32yank-wrapper project.

## Test Files

**`test_pyperclip_compatibility.py`**
The test file uses pytest with parameterization for table-driven testing.

**Pros:**
- **Table-driven approach**: All test cases defined in one place
- **More readable**: Test cases clearly listed as data
- **Easier to maintain**: Add new tests by adding to the table
- **Better reporting**: pytest provides excellent test output
- **Fixtures**: Setup/teardown logic centralized

**Cons:**
- Requires pytest installation (`pip install pytest`)
- Slightly more complex setup

## Running Tests

### Using pytest (Recommended)
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

### Using Python directly
```bash
# Run the test file directly (will use pytest internally)
python test_pyperclip_compatibility.py
```

## Test Case Structure

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

## Adding New Tests

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

## Test Coverage

The tests cover:
- Basic copy/paste operations
- Unicode and special character handling
- Multi-line text
- Empty clipboard
- Direct xclip command calls
- Special characters

## Best Practices

1. **Keep tests independent**: Each test should work regardless of order
2. **Use descriptive names**: Test names should clearly indicate what's being tested
3. **Test edge cases**: Empty strings, long text, special characters
4. **Test error conditions**: What happens when clipboard is unavailable?
5. **Keep tests fast**: Tests should run quickly for good developer experience

## Debugging Tests

If a test fails:

1. Run with verbose output: `pytest -vv`
2. Check the exact error message
3. Add debug prints if needed
4. Run individual test: `pytest test_name -v`

## Continuous Integration

For CI/CD pipelines, add this to your workflow:

```yaml
- name: Run tests
  run: |
    pip install pytest pyperclip
    pytest test_pyperclip_compatibility_improved.py -v
```
