"""Check exact characters around Builder"""
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

idx = normalized.find('Builder')
if idx > 0:
    snippet = normalized[idx:idx+30]
    print("Characters after 'Builder':")
    for i, char in enumerate(snippet):
        print(f"  {i}: '{char}' = U+{ord(char):04X} ({repr(char)})")
        if i > 15:
            break
