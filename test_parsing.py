#!/usr/bin/env python3

# Test git status parsing
line = " M app.py"
print("Full line:", repr(line))
print("Length:", len(line))
print("Status:", repr(line[:2]))
print("Filename:", repr(line[3:]))
print("Status[0]:", repr(line[0]))
print("Status[1]:", repr(line[1]))

# Test the parsing logic
status = line[:2]
filename = line[3:]

print("\nParsing results:")
print(f"Status code: {repr(status)}")
print(f"Extracted filename: {repr(filename)}")

# Test the condition checks
print(f"\nCondition checks:")
print(f"status[0] == ' ': {status[0] == ' '}")
print(f"status[1] == 'M': {status[1] == 'M'}")
print(f"status[0] in ['M', 'A', 'D', 'R', 'C']: {status[0] in ['M', 'A', 'D', 'R', 'C']}")
print(f"status[1] in ['M', 'D']: {status[1] in ['M', 'D']}")
