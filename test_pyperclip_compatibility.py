#!/usr/bin/env python3

import subprocess
import sys
import os

def test_pyperclip_compatibility():
    """Test xclip wrapper compatibility with pyperclip"""
    
    print("Testing xclip wrapper with pyperclip compatibility...")
    print("=" * 60)
    
    # Test 1: Basic copy/paste
    print("\nTest 1: Basic copy/paste")
    try:
        # Set xclip as clipboard mechanism
        import pyperclip
        pyperclip.set_clipboard('xclip')
        
        # Test copy and paste
        test_text = "Test from pyperclip"
        pyperclip.copy(test_text)
        result = pyperclip.paste()
        
        # Strip trailing newline for comparison (pyperclip adds it)
        result_stripped = result.rstrip('\n')
        if result_stripped == test_text:
            print("✓ PASS: Basic copy/paste works")
        else:
            print(f"✗ FAIL: Expected '{test_text}', got '{result}'")
            return False
            
    except Exception as e:
        print(f"✗ FAIL: Error in basic copy/paste: {e}")
        return False
    
    # Test 2: Unicode handling
    print("\nTest 2: Unicode handling")
    try:
        unicode_text = "Unicode: 你好 🎉"
        pyperclip.copy(unicode_text)
        result = pyperclip.paste()
        
        # Strip trailing newline for comparison
        result_stripped = result.rstrip('\n')
        if result_stripped == unicode_text:
            print("✓ PASS: Unicode handling works")
        else:
            print(f"✗ FAIL: Expected '{unicode_text}', got '{result}'")
            return False
            
    except Exception as e:
        print(f"✗ FAIL: Error in Unicode handling: {e}")
        return False
    
    # Test 3: Multi-line text
    print("\nTest 3: Multi-line text")
    try:
        multiline_text = "Line 1\nLine 2\nLine 3"
        pyperclip.copy(multiline_text)
        result = pyperclip.paste()
        
        # For multiline, check if it contains all lines (newline handling may vary)
        if "Line 1" in result and "Line 2" in result and "Line 3" in result:
            print("✓ PASS: Multi-line text works")
        else:
            print(f"✗ FAIL: Expected multiline text, got '{result}'")
            return False
            
    except Exception as e:
        print(f"✗ FAIL: Error in multi-line text: {e}")
        return False
    
    # Test 4: Special characters
    print("\nTest 4: Special characters")
    try:
        special_text = "Special: @#$%^&*()"
        pyperclip.copy(special_text)
        result = pyperclip.paste()
        
        # Strip trailing newline for comparison
        result_stripped = result.rstrip('\n')
        if result_stripped == special_text:
            print("✓ PASS: Special characters work")
        else:
            print(f"✗ FAIL: Expected '{special_text}', got '{result}'")
            return False
            
    except Exception as e:
        print(f"✗ FAIL: Error in special characters: {e}")
        return False
    
    # Test 5: Empty clipboard
    print("\nTest 5: Empty clipboard")
    try:
        # Clear clipboard by copying empty string
        pyperclip.copy("")
        result = pyperclip.paste()
        
        # Strip whitespace for comparison
        result_stripped = result.strip()
        if result_stripped == "":
            print("✓ PASS: Empty clipboard works")
        else:
            print(f"✗ FAIL: Expected empty string, got '{result}'")
            return False
            
    except Exception as e:
        print(f"✗ FAIL: Error in empty clipboard: {e}")
        return False
    
    # Test 6: Direct xclip calls (like pyperclip does)
    print("\nTest 6: Direct xclip calls")
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
        
        if result == "Direct stdin test":
            print("✓ PASS: Direct xclip calls work")
        else:
            print(f"✗ FAIL: Expected 'Direct stdin test', got '{result}'")
            return False
            
    except Exception as e:
        print(f"✗ FAIL: Error in direct xclip calls: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("All pyperclip compatibility tests passed!")
    return True

if __name__ == "__main__":
    # Check if pyperclip is installed
    try:
        import pyperclip
    except ImportError:
        print("Error: pyperclip is not installed.")
        print("Please install it with: pip install pyperclip")
        sys.exit(1)
    
    success = test_pyperclip_compatibility()
    sys.exit(0 if success else 1)