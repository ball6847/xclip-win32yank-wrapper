#!/usr/bin/env python3
"""
Comprehensive test suite for xclip wrapper using pytest parameterization.
Converts comprehensive_test.sh to Python with table-driven approach.
"""

import subprocess
import sys
import pytest


# Comprehensive test cases defined as a table
COMPREHENSIVE_TEST_CASES = [
    # (test_name, input_text, expected_text, check_type, should_fail)
    ("Basic copy/paste", "Hello World", "Hello World", "exact", False),
    ("Selection flags", "Test", "Test", "exact", False),
    ("Empty clipboard", "", "", "exact", False),
    ("Special characters", "!@#$%^&*()_+-=[]{}|;:',.<>?/~`", "!@#$%^&*()_+-=[]{}|;:',.<>?/~`", "exact", False),
    ("Unicode", "Hello 世界 🎉 😀", "Hello 世界 🎉 😀", "exact", False),
    ("Multi-line text", "Line 1\nLine 2\nLine 3", "Line 1\nLine 2\nLine 3", "exact", False),
    ("Long text", "A" * 10000, "A" * 10000, "exact", False),
    ("Whitespace handling", "  spaces  \t  tabs  \n  newlines  ", "  spaces  \t  tabs  \n  newlines  ", "contains", False),
]


# Error handling test cases
ERROR_TEST_CASES = [
    ("Invalid selection", ["-selection", "x"], True),
    ("Both -i and -o", ["-i", "-o"], True),
    ("Unknown option", ["-unknown"], True),
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


@pytest.mark.parametrize("test_name,input_text,expected_text,check_type,should_fail", COMPREHENSIVE_TEST_CASES)
def test_comprehensive_operations(xclip_path, test_name, input_text, expected_text, check_type, should_fail):
    """Test comprehensive clipboard operations"""
    print(f"\nTest: {test_name}")
    
    # Check if xclip exists first
    import os
    if not os.path.exists(xclip_path):
        print(f"⚠ SKIP: xclip wrapper not found at {xclip_path}")
        pytest.skip(f"xclip wrapper not found at {xclip_path}")
    
    try:
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


@pytest.mark.parametrize("test_name,args,should_fail", ERROR_TEST_CASES)
def test_comprehensive_error_handling(xclip_path, test_name, args, should_fail):
    """Test comprehensive error handling scenarios"""
    print(f"\nTest: {test_name}")
    
    # Check if xclip exists first
    import os
    if not os.path.exists(xclip_path):
        print(f"⚠ SKIP: xclip wrapper not found at {xclip_path}")
        pytest.skip(f"xclip wrapper not found at {xclip_path}")
    
    try:
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


def test_version_and_help(xclip_path):
    """Test version and help flags"""
    print("\nTest: Version and help flags")
    
    # Check if xclip exists first
    import os
    if not os.path.exists(xclip_path):
        print(f"⚠ SKIP: xclip wrapper not found at {xclip_path}")
        pytest.skip(f"xclip wrapper not found at {xclip_path}")
    
    # Test version
    proc = subprocess.Popen(
        [xclip_path, "-version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    version_output = (stdout + stderr).decode('utf-8')
    
    assert "xclip wrapper" in version_output.lower(), \
        f"Expected version information, got: {version_output}"
    print("✓ PASS: Version flag")
    
    # Test help
    proc = subprocess.Popen(
        [xclip_path, "-help"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = proc.communicate()
    
    assert (stdout.decode('utf-8').strip() != "" or 
            stderr.decode('utf-8').strip() != ""), \
        "Expected help output"
    print("✓ PASS: Help flag")


def test_quiet_mode(xclip_path):
    """Test quiet mode"""
    print("\nTest: Quiet mode")
    
    # Check if xclip exists first
    import os
    if not os.path.exists(xclip_path):
        print(f"⚠ SKIP: xclip wrapper not found at {xclip_path}")
        pytest.skip(f"xclip wrapper not found at {xclip_path}")
    
    test_text = "test"
    
    proc = subprocess.Popen(
        [xclip_path, "-i", "-quiet"],
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    _, stderr = proc.communicate(input=test_text.encode('utf-8'))
    
    assert stderr.decode('utf-8').strip() == "", \
        f"Expected no stderr output in quiet mode, got: {stderr.decode('utf-8')}"
    print("✓ PASS: Quiet mode")


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
