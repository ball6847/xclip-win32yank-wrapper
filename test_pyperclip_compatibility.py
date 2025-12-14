#!/usr/bin/env python3
"""
Improved pyperclip compatibility test using pytest parameterization.
This makes the test more readable and maintainable with table-driven approach.
"""

import subprocess
import sys
import os
import pytest


# Test cases defined as a table (list of tuples)
TEST_CASES = [
    # (test_name, input_text, expected_text, should_contain_lines)
    ("Basic copy/paste", "Test from pyperclip", "Test from pyperclip", None),
    ("Unicode handling", "Unicode: 你好 🎉", "Unicode: 你好 🎉", None),
    ("Special characters", "Special: @#$%^&*()", "Special: @#$%^&*()", None),
    ("Empty clipboard", "", "", None),
    ("Multi-line text", "Line 1\nLine 2\nLine 3", None, ["Line 1", "Line 2", "Line 3"]),
]


@pytest.fixture(scope="module")
def setup_pyperclip():
    """Setup pyperclip to use xclip"""
    import pyperclip
    pyperclip.set_clipboard('xclip')
    yield


@pytest.mark.parametrize("test_name,input_text,expected_text,should_contain_lines", TEST_CASES)
def test_pyperclip_compatibility(setup_pyperclip, test_name, input_text, expected_text, should_contain_lines):
    """Test xclip wrapper compatibility with pyperclip using parameterized tests"""
    import pyperclip
    
    print(f"\nTest: {test_name}")
    
    try:
        # Copy text
        pyperclip.copy(input_text)
        
        # Paste text
        result = pyperclip.paste()
        
        # Strip trailing newline for comparison (pyperclip adds it)
        result_stripped = result.rstrip('\n')
        
        # Check result
        if should_contain_lines:
            # For multi-line tests, check if all lines are present
            assert all(line in result for line in should_contain_lines), \
                f"Expected all lines to be present in result: {result}"
            print(f"✓ PASS: {test_name}")
        else:
            # For single-line tests, exact match
            assert result_stripped == expected_text, \
                f"Expected '{expected_text}', got '{result}'"
            print(f"✓ PASS: {test_name}")
            
    except Exception as e:
        print(f"✗ FAIL: {test_name} - Error: {e}")
        raise


def test_direct_xclip_calls():
    """Test direct xclip calls (like pyperclip does)"""
    print("\nTest: Direct xclip calls")
    
    try:
        # Test copy with stdin
        proc = subprocess.Popen(['./xclip', '-selection', 'c'], 
                              stdin=subprocess.PIPE)
        proc.communicate(input=b"Direct stdin test")
        
        # Test paste
        proc = subprocess.Popen(['./xclip', '-selection', 'c', '-o'],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        result = stdout.decode('utf-8').strip()
        
        assert result == "Direct stdin test", \
            f"Expected 'Direct stdin test', got '{result}'"
        print("✓ PASS: Direct xclip calls work")
        
    except Exception as e:
        print(f"✗ FAIL: Direct xclip calls - Error: {e}")
        raise


if __name__ == "__main__":
    # Check if pyperclip is installed
    try:
        import pyperclip
    except ImportError:
        print("Error: pyperclip is not installed.")
        print("Please install it with: pip install pyperclip")
        sys.exit(1)
    
    # Run tests with pytest
    pytest.main([__file__, "-v"])
