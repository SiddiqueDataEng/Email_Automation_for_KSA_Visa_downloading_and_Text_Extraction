"""Test exact pattern with actual text"""
import re

# Exact text from PDF
text = "الجنسية Pakistan ‐  باكستان Nationality"

print("Testing Nationality extraction:")
print(f"Text: {repr(text)}")
print()

# Test pattern
pattern = r'([A-Z][a-z]+)\s+‐\s+[\u0600-\u06FF\s]+Nationality'
match = re.search(pattern, text)

if match:
    print(f"MATCH: '{match.group(1)}'")
else:
    print("NO MATCH")
    
    # Debug: show what characters are in the text
    print("\nCharacter analysis:")
    for i, char in enumerate(text):
        if char in ['‐', '-', '–', '—']:
            print(f"  Position {i}: '{char}' (U+{ord(char):04X}) - dash variant")

# Test with different dash characters
print("\nTrying different dash patterns:")
patterns = [
    r'([A-Z][a-z]+)\s+‐\s+[\u0600-\u06FF\s]+Nationality',  # ‐ (U+2010)
    r'([A-Z][a-z]+)\s+-\s+[\u0600-\u06FF\s]+Nationality',  # - (hyphen)
    r'([A-Z][a-z]+)\s+[\u2010-\u2015-]\s+[\u0600-\u06FF\s]+Nationality',  # Any dash
]

for i, p in enumerate(patterns, 1):
    match = re.search(p, text)
    if match:
        print(f"  Pattern {i}: MATCH = '{match.group(1)}'")
    else:
        print(f"  Pattern {i}: NO MATCH")
