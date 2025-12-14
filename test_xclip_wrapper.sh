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

# Test 6: Multi-line text
echo -e "\nTest 6: Multi-line text"
echo -e "Line 1\nLine 2\nLine 3" | ./xclip -i
result=$(./xclip -o)
expected="Line 1\nLine 2\nLine 3"
if [[ "$result" == "$expected" ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Expected '$expected', got '$result'"
fi

# Test 7: Tool detection and fallback
echo -e "\nTest 7: Tool detection and fallback"
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

# Test 8: Help text
echo -e "\nTest 8: Help text"
if ./xclip -help >/dev/null 2>&1; then
    echo "✓ Help text displayed"
else
    echo "✗ FAIL: Help text not displayed"
fi

# Test 9: Version information
echo -e "\nTest 9: Version information"
version_output=$(./xclip -version 2>&1)
if [[ "$version_output" == *"xclip wrapper v2.0"* ]]; then
    echo "✓ Version information displayed"
else
    echo "✗ FAIL: Version information not displayed"
fi

# Test 10: Error handling - no arguments
echo -e "\nTest 10: Error handling - no arguments"
if ./xclip 2>/dev/null; then
    echo "✗ FAIL: Should have failed with no arguments"
else
    echo "✓ PASS: Correctly failed with no arguments"
fi

# Test 11: Error handling - both -i and -o
echo -e "\nTest 11: Error handling - both -i and -o"
if echo "test" | ./xclip -i -o 2>/dev/null; then
    echo "✗ FAIL: Should have failed with both -i and -o"
else
    echo "✓ PASS: Correctly failed with both -i and -o"
fi

# Test 12: Quiet mode
echo -e "\nTest 12: Quiet mode"
if echo "test" | ./xclip -i -quiet 2>/dev/null; then
    echo "✓ PASS: Quiet mode works"
else
    echo "✗ FAIL: Quiet mode failed"
fi

echo -e "\n================================================"
echo "Testing complete!"