"""Test pattern with newline"""
import re

# Exact text from PDF with newline
text = "الجنسية Pakistan\xa0‐\xa0 باكستان Nationality\n"

print("Text:", repr(text))
print()

# Test patterns
patterns = [
    r'([A-Z][a-z]+)[\s\xa0]+[\u2010-\u2015\-][\s\xa0]+[\u0600-\u06FF\s\xa0]+Nationality',
    r'([A-Z][a-z]+)[\s\xa0]+[\u2010-\u2015\-][\s\xa0]+[\u0600-\u06FF\s\xa0\n]+Nationality',  # Add \n
]

for i, pattern in enumerate(patterns, 1):
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    print(f"Pattern {i}: {match.group(1) if match else 'NO MATCH'}")
