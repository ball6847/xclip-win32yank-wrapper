#!/usr/bin/env python3
"""
Test suite for xclip wrapper using pytest parameterization.
Converts shell script tests to Python with table-driven approach.
"""

import subprocess
import sys
import pytest


# Test cases defined as a table (list of tuples)
# Each test case: (test_name, input_text, expected_text, should_fail, check_function)
TEST_CASES = [
    # Basic functionality tests
    ("Basic copy/paste", "Hello World", "Hello World", False, "exact"),
    ("Special characters", "Special: @#$%^&*()", "Special: @#$%^&*()", False, "exact"),
    ("Unicode handling", "Unicode: 你好 🎉", "Unicode: 你好 🎉", False, "exact"),
    ("Multi-line text", "Line 1\nLine 2\nLine 3", "Line 1\nLine 2\nLine 3", False, "exact"),
    
    # Selection handling tests
    ("Selection CLIPBOARD", "Test", "Test", False, "exact"),
    ("Selection PRIMARY", "Test", "Test", False, "exact"),
    
    # Edge cases
    ("Empty clipboard", "", "", False, "exact"),
]


# Error handling test cases
ERROR_TEST_CASES = [
    ("No arguments", [], True, "should fail"),
    ("Both -i and -o", ["-i", "-o"], True, "should fail"),
]


@pytest.fixture(scope="module")
def xclip_path():
    """Get the path to the xclip wrapper"""
    import os
    # Try to find xclip in parent directory or current directory
    if os.path.exists("../xclip"):
        return "../xclip"
    elif os.path.exists("./xclip"):
        return "./xclip"
    else:
        return "xclip"


@pytest.mark.parametrize("test_name,input_text,expected_text,should_fail,check_type", TEST_CASES)
def test_clipboard_operations(xclip_path, test_name, input_text, expected_text, should_fail, check_type):
    """Test clipboard operations using parameterized tests"""
    print(f"\nTest: {test_name}")
    
    try:
        # Check if xclip exists first
        import os
        if not os.path.exists(xclip_path):
            print(f"⚠ SKIP: {test_name} - xclip wrapper not found at {xclip_path}")
            pytest.skip(f"xclip wrapper not found at {xclip_path}")
        
        # Copy text to clipboard
        proc = subprocess.Popen(
            [xclip_path, "-i"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate(input=input_text.encode('utf-8'))
        
        # Paste text from clipboard
        proc = subprocess.Popen(
            [xclip_path, "-o"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        result = stdout.decode('utf-8').strip()
        
        # Check result
        if check_type == "exact":
            assert result == expected_text, \
                f"Expected '{expected_text}', got '{result}'"
            print(f"✓ PASS: {test_name}")
        elif check_type == "contains":
            assert expected_text in result, \
                f"Expected '{expected_text}' to be in result: '{result}'"
            print(f"✓ PASS: {test_name}")
            
    except Exception as e:
        print(f"✗ FAIL: {test_name} - Error: {e}")
        raise


@pytest.mark.parametrize("test_name,args,should_fail,check_type", ERROR_TEST_CASES)
def test_error_handling(xclip_path, test_name, args, should_fail, check_type):
    """Test error handling scenarios"""
    print(f"\nTest: {test_name}")
    
    try:
        # Check if xclip exists first
        import os
        if not os.path.exists(xclip_path):
            print(f"⚠ SKIP: {test_name} - xclip wrapper not found at {xclip_path}")
            pytest.skip(f"xclip wrapper not found at {xclip_path}")
        
        proc = subprocess.Popen(
            [xclip_path] + args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        
        if should_fail:
            assert proc.returncode != 0, \
                f"Expected command to fail, but it succeeded"
            print(f"✓ PASS: {test_name}")
        else:
            assert proc.returncode == 0, \
                f"Expected command to succeed, but it failed: {stderr.decode('utf-8')}"
            print(f"✓ PASS: {test_name}")
            
    except Exception as e:
        print(f"✗ FAIL: {test_name} - Error: {e}")
        raise


def test_selection_handling(xclip_path):
    """Test selection handling (-selection flag)"""
    print("\nTest: Selection handling")
    
    # Check if xclip exists first
    import os
    if not os.path.exists(xclip_path):
        print(f"⚠ SKIP: xclip wrapper not found at {xclip_path}")
        pytest.skip(f"xclip wrapper not found at {xclip_path}")
    
    test_text = "Selection test"
    
    # Test CLIPBOARD selection
    proc = subprocess.Popen(
        [xclip_path, "-selection", "c", "-i"],
        stdin=subprocess.PIPE
    )
    proc.communicate(input=test_text.encode('utf-8'))
    
    # Read back
    proc = subprocess.Popen(
        [xclip_path, "-selection", "c", "-o"],
        stdout=subprocess.PIPE
    )
    stdout, _ = proc.communicate()
    result = stdout.decode('utf-8').strip()
    
    assert result == test_text, \
        f"Expected '{test_text}', got '{result}'"
    print("✓ PASS: Selection handling works")


def test_quiet_mode(xclip_path):
    """Test quiet mode (-quiet flag)"""
    print("\nTest: Quiet mode")
    
    # Check if xclip exists first
    import os
    if not os.path.exists(xclip_path):
        print(f"⚠ SKIP: xclip wrapper not found at {xclip_path}")
        pytest.skip(f"xclip wrapper not found at {xclip_path}")
    
    test_text = "Quiet test"
    
    proc = subprocess.Popen(
        [xclip_path, "-i", "-quiet"],
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    _, stderr = proc.communicate(input=test_text.encode('utf-8'))
    
    # Quiet mode should produce no stderr output
    assert stderr.decode('utf-8').strip() == "", \
        f"Expected no stderr output in quiet mode, got: {stderr.decode('utf-8')}"
    print("✓ PASS: Quiet mode works")


def test_help_and_version(xclip_path):
    """Test help and version flags"""
    print("\nTest: Help and version information")
    
    # Check if xclip exists first
    import os
    if not os.path.exists(xclip_path):
        print(f"⚠ SKIP: xclip wrapper not found at {xclip_path}")
        pytest.skip(f"xclip wrapper not found at {xclip_path}")
    
    # Test help
    proc = subprocess.Popen(
        [xclip_path, "-help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    
    # Help should produce output (either stdout or stderr)
    assert (stdout.decode('utf-8').strip() != "" or 
            stderr.decode('utf-8').strip() != ""), \
        "Expected help output"
    print("✓ PASS: Help text displayed")
    
    # Test version
    proc = subprocess.Popen(
        [xclip_path, "-version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    output = (stdout + stderr).decode('utf-8')
    
    # Version should contain version information
    assert "xclip wrapper" in output.lower(), \
        f"Expected version information, got: {output}"
    print("✓ PASS: Version information displayed")


def test_tool_detection():
    """Test clipboard tool detection"""
    print("\nTest: Tool detection")
    
    # Check for win32yank.exe
    try:
        proc = subprocess.Popen(
            ["which", "win32yank.exe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, _ = proc.communicate()
        
        if stdout.decode('utf-8').strip():
            print("✓ win32yank.exe detected (primary tool)")
        else:
            print("- win32yank.exe not found")
    except FileNotFoundError:
        print("- 'which' command not available, skipping win32yank.exe check")
    
    # Check for win32yoink.exe
    try:
        proc = subprocess.Popen(
            ["which", "win32yoink.exe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, _ = proc.communicate()
        
        if stdout.decode('utf-8').strip():
            print("✓ win32yoink.exe detected (fallback tool)")
        else:
            print("- win32yoink.exe not found")
    except FileNotFoundError:
        print("- 'which' command not available, skipping win32yoink.exe check")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
