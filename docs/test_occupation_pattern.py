"""Test occupation pattern"""
import os
import re
from pdf_processor_advanced import AdvancedPDFProcessor

base_path = r"\\COUNTER3\Shared Data\Visa_Slips_Automated"

for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith('_extracted.pdf'):
            pdf_path = os.path.join(root, file)
            break
    if 'pdf_path' in locals():
        break

processor = AdvancedPDFProcessor()
text = processor._extract_text_pypdf(pdf_path)
normalized = re.sub(r'[ \t\xa0]+', ' ', text)

print("Testing occupation pattern:")
print()

# Check if Builder is in normalized text
if 'Builder' in normalized:
    print("✓ 'Builder' found in normalized text")
else:
    print("✗ 'Builder' NOT in normalized text")
    print(f"Normalized text length: {len(normalized)}")

# Test pattern - no space between Builder and Arabic
pattern = r'([A-Z][a-z]+)[\s\xa0]*[\u0600-\u06FF]+.*?Occupation'
match = re.search(pattern, normalized, re.IGNORECASE | re.DOTALL)

if match:
    print(f"MATCH: '{match.group(1)}'")
else:
    print("NO MATCH")
    
    # Try simpler
    pattern2 = r'([A-Z][a-z]+)\s+[\u0600-\u06FF]+.*?Occupation'
    match2 = re.search(pattern2, normalized, re.IGNORECASE | re.DOTALL)
    if match2:
        print(f"Simple pattern MATCH: '{match2.group(1)}'")
    else:
        print("Simple pattern NO MATCH")
        
        # Show what's actually there
        idx = normalized.find('Occupation')
        if idx > 0:
            snippet = normalized[idx-50:idx+20]
            print(f"\nActual text: {repr(snippet)}")
