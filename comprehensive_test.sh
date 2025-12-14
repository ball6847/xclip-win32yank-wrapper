#!/bin/bash

echo "Comprehensive xclip wrapper testing..."
echo "======================================"

# Test 1: Basic functionality
echo -e "\nTest 1: Basic copy/paste"
echo "Hello World" | xclip -i
result=$(xclip -o)
if [[ "$result" == "Hello World" ]]; then
    echo "PASS"
else
    echo "FAIL: Expected 'Hello World', got '$result'"
fi

# Test 2: Selection flags
echo -e "\nTest 2: Selection flags"
echo "Test" | xclip -selection c -i
result=$(xclip -selection p -o)
if [[ "$result" == "Test" ]]; then
    echo "PASS"
else
    echo "FAIL: Expected 'Test', got '$result'"
fi

# Test 3: Empty clipboard
echo -e "\nTest 3: Empty clipboard"
result=$(xclip -o)
if [[ -z "$result" ]]; then
    echo "PASS"
else
    echo "FAIL: Expected empty string, got '$result'"
fi

# Test 4: Special characters
echo -e "\nTest 4: Special characters"
special="!@#$%^&*()_+-=[]{}|;:',.<>?/~`"
echo "$special" | xclip -i
result=$(xclip -o)
if [[ "$result" == "$special" ]]; then
    echo "PASS"
else
    echo "FAIL: Expected '$special', got '$result'"
fi

# Test 5: Unicode
echo -e "\nTest 5: Unicode"
unicode="Hello 世界 🎉 😀"
echo "$unicode" | xclip -i
result=$(xclip -o)
if [[ "$result" == "$unicode" ]]; then
    echo "PASS"
else
    echo "FAIL: Expected '$unicode', got '$result'"
fi

# Test 6: Multi-line text
echo -e "\nTest 6: Multi-line text"
echo -e "Line 1\nLine 2\nLine 3" | xclip -i
result=$(xclip -o)
if [[ "$result" == "Line 1" ]] && [[ "$result" == *"Line 2"* ]] && [[ "$result" == *"Line 3"* ]]; then
    echo "PASS"
else
    echo "FAIL: Expected multiline text, got '$result'"
fi

# Test 7: Long text
echo -e "\nTest 7: Long text"
long_text=$(python -c "print('A' * 10000)")
echo "$long_text" | xclip -i
result=$(xclip -o)
if [[ "${#result}" -eq 10000 ]]; then
    echo "PASS"
else
    echo "FAIL: Expected 10000 chars, got ${#result}"
fi

# Test 8: Whitespace handling
echo -e "\nTest 8: Whitespace handling"
whitespace="  spaces  \t  tabs  \n  newlines  "
echo -e "$whitespace" | xclip -i
result=$(xclip -o)
if [[ "$result" == "$whitespace" ]]; then
    echo "PASS"
else
    echo "FAIL: Expected '$whitespace', got '$result'"
fi

# Test 9: Version flag
echo -e "\nTest 9: Version flag"
version=$(xclip -version 2>&1)
if [[ "$version" == *"xclip wrapper v2.0"* ]]; then
    echo "PASS"
else
    echo "FAIL: Expected version info, got '$version'"
fi

# Test 10: Help flag
echo -e "\nTest 10: Help flag"
if xclip -help >/dev/null 2>&1; then
    echo "PASS"
else
    echo "FAIL: Help flag failed"
fi

# Test 11: Quiet mode
echo -e "\nTest 11: Quiet mode"
if echo "test" | xclip -i -quiet 2>/dev/null; then
    echo "PASS"
else
    echo "FAIL: Quiet mode failed"
fi

# Test 12: Error handling - invalid selection
echo -e "\nTest 12: Error handling - invalid selection"
if echo "test" | xclip -selection x 2>/dev/null; then
    echo "FAIL: Should have failed with invalid selection"
else
    echo "PASS"
fi

# Test 13: Error handling - both -i and -o
echo -e "\nTest 13: Error handling - both -i and -o"
if echo "test" | xclip -i -o 2>/dev/null; then
    echo "FAIL: Should have failed with both -i and -o"
else
    echo "PASS"
fi

# Test 14: Error handling - unknown option
echo -e "\nTest 14: Error handling - unknown option"
if xclip -unknown 2>/dev/null; then
    echo "FAIL: Should have failed with unknown option"
else
    echo "PASS"
fi

# Test 15: Tool detection
echo -e "\nTest 15: Tool detection"
if command -v win32yank.exe >/dev/null 2>&1; then
    echo "win32yank.exe detected"
else
    echo "win32yank.exe not found"
fi

if command -v win32yoink.exe >/dev/null 2>&1; then
    echo "win32yoink.exe detected"
else
    echo "win32yoink.exe not found"
fi

echo -e "\n======================================"
echo "Comprehensive testing complete!"
