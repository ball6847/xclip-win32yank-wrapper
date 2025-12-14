#!/bin/bash

echo "Simple xclip wrapper tests..."
echo "============================"

# Clear clipboard first
echo "" | xclip -i

# Test 1: Basic copy/paste
echo -e "\nTest 1: Basic copy/paste"
echo "Hello World" | xclip -i
result=$(xclip -o)
if [[ "$result" == "Hello World" ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Expected 'Hello World', got '$result'"
fi

# Test 2: Unicode
echo -e "\nTest 2: Unicode"
unicode="Hello 世界 🎉"
echo "$unicode" | xclip -i
result=$(xclip -o)
if [[ "$result" == "$unicode" ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Expected '$unicode', got '$result'"
fi

# Test 3: Empty clipboard
echo -e "\nTest 3: Empty clipboard"
echo "" | xclip -i
result=$(xclip -o)
if [[ -z "$result" ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Expected empty string, got '$result'"
fi

# Test 4: Special characters
echo -e "\nTest 4: Special characters"
special="!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
echo "$special" | xclip -i
result=$(xclip -o)
if [[ "$result" == "$special" ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Expected '$special', got '$result'"
fi

# Test 5: Version
echo -e "\nTest 5: Version"
version=$(xclip -version 2>&1)
if [[ "$version" == *"xclip wrapper v2.0"* ]]; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Expected version info, got '$version'"
fi

# Test 6: Help
echo -e "\nTest 6: Help"
if xclip -help >/dev/null 2>&1; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Help failed"
fi

# Test 7: Quiet mode
echo -e "\nTest 7: Quiet mode"
if echo "test" | xclip -i -quiet 2>/dev/null; then
    echo "✓ PASS"
else
    echo "✗ FAIL: Quiet mode failed"
fi

# Test 8: Error handling - invalid selection
echo -e "\nTest 8: Error handling - invalid selection"
if echo "test" | xclip -selection x 2>/dev/null; then
    echo "✗ FAIL: Should have failed"
else
    echo "✓ PASS"
fi

# Test 9: Error handling - both -i and -o
echo -e "\nTest 9: Error handling - both -i and -o"
if echo "test" | xclip -i -o 2>/dev/null; then
    echo "✗ FAIL: Should have failed"
else
    echo "✓ PASS"
fi

# Test 10: Tool detection
echo -e "\nTest 10: Tool detection"
if command -v win32yank.exe >/dev/null 2>&1; then
    echo "✓ win32yank.exe detected"
else
    echo "- win32yank.exe not found"
fi

if command -v win32yoink.exe >/dev/null 2>&1; then
    echo "✓ win32yoink.exe detected"
else
    echo "- win32yoink.exe not found"
fi

echo -e "\n============================"
echo "All tests complete!"
