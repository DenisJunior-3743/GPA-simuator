#!/usr/bin/env python3
"""Test the full save and view flow in the CLI."""

import subprocess
import sys

# Test input: register, save semester with 2 courses, view history, logout
test_input = """1
testuser7
pass123
David Jones
david@test.com
Software
3
7
1
1
2
Linear Algebra
4
1
Discrete Math
3
2
y
6
9
"""

print("Testing save semester and view history flow...\n")

# Run CLI
proc = subprocess.Popen(
    [sys.executable, 'main.py', '--cli'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

output, _ = proc.communicate(input=test_input, timeout=10)

# Show relevant parts of output
lines = output.split('\n')
in_history = False
for i, line in enumerate(lines):
    if 'View Academic History' in line:
        in_history = True
    if in_history:
        print(line)
        if i > 0 and 'Logout' in lines[i-1]:
            break
