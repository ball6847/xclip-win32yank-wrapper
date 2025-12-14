#!/usr/bin/env python3
"""
Mock clipboard tools for testing xclip wrapper on non-Windows platforms.
These simulate the behavior of win32yank.exe and win32yoink.exe.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Global clipboard storage for mock
_MOCK_CLIPBOARD = ""
_MOCK_CLIPBOARD_FILE = None


def setup_mock_clipboard():
    """Setup mock clipboard tools"""
    global _MOCK_CLIPBOARD_FILE
    
    # Create a temporary directory for mock tools
    temp_dir = tempfile.mkdtemp()
    
    # Create mock win32yank.exe
    win32yank_script = os.path.join(temp_dir, "win32yank.exe")
    with open(win32yank_script, 'w') as f:
        f.write("""#!/bin/bash
# Mock win32yank.exe

if [[ "$1" == "-i" ]]; then
    # Read from stdin and store in clipboard
    if [ -t 0 ]; then
        # No input on stdin
        exit 0
    fi
    content=$(cat)
    echo "$content" > {clipboard_file}
exit 0
elif [[ "$1" == "-o" ]]; then
    # Output clipboard content
    if [ -f {clipboard_file} ]; then
        cat {clipboard_file}
    fi
exit 0
else
    # Show help
    echo "win32yank: clipboard utility"
    echo "Usage: win32yank [-i|-o]"
    exit 1
fi
""".format(clipboard_file=temp_dir + "/clipboard.txt"))
    
    # Create mock win32yoink.exe
    win32yoink_script = os.path.join(temp_dir, "win32yoink.exe")
    with open(win32yoink_script, 'w') as f:
        f.write("""#!/bin/bash
# Mock win32yoink.exe

if [[ "$1" == "-i" ]]; then
    # Read from stdin and store in clipboard
    if [ -t 0 ]; then
        # No input on stdin
        exit 0
    fi
    content=$(cat)
    echo "$content" > {clipboard_file}
exit 0
elif [[ "$1" == "-o" ]]; then
    # Output clipboard content
    if [ -f {clipboard_file} ]; then
        cat {clipboard_file}
    fi
exit 0
else
    # Show help
    echo "win32yoink: clipboard utility"
    echo "Usage: win32yoink [-i|-o]"
    exit 1
fi
""".format(clipboard_file=temp_dir + "/clipboard.txt"))
    
    # Make scripts executable
    os.chmod(win32yank_script, 0o755)
    os.chmod(win32yoink_script, 0o755)
    
    # Add to PATH
    os.environ["PATH"] = temp_dir + ":" + os.environ["PATH"]
    
    _MOCK_CLIPBOARD_FILE = temp_dir + "/clipboard.txt"
    
    return temp_dir


def clear_mock_clipboard():
    """Clear mock clipboard"""
    global _MOCK_CLIPBOARD
    _MOCK_CLIPBOARD = ""
    if _MOCK_CLIPBOARD_FILE and os.path.exists(_MOCK_CLIPBOARD_FILE):
        os.remove(_MOCK_CLIPBOARD_FILE)


def get_mock_clipboard():
    """Get current clipboard content"""
    if _MOCK_CLIPBOARD_FILE and os.path.exists(_MOCK_CLIPBOARD_FILE):
        with open(_MOCK_CLIPBOARD_FILE, 'r') as f:
            return f.read()
    return ""


def set_mock_clipboard(content):
    """Set clipboard content"""
    global _MOCK_CLIPBOARD
    _MOCK_CLIPBOARD = content
    if _MOCK_CLIPBOARD_FILE:
        with open(_MOCK_CLIPBOARD_FILE, 'w') as f:
            f.write(content)


if __name__ == "__main__":
    # Simple test of mock tools
    setup_mock_clipboard()
    
    # Test win32yank
    result = subprocess.run(["win32yank.exe", "-o"], capture_output=True, text=True)
    print(f"win32yank -o (empty): '{result.stdout}'")
    
    # Copy something
    subprocess.run(["echo", "Test content", "|", "win32yank.exe", "-i"], shell=True)
    result = subprocess.run(["win32yank.exe", "-o"], capture_output=True, text=True)
    print(f"win32yank -o (after copy): '{result.stdout}'")
    
    # Test win32yoink
    result = subprocess.run(["win32yoink.exe", "-o"], capture_output=True, text=True)
    print(f"win32yoink -o (empty): '{result.stdout}'")
    
    clear_mock_clipboard()