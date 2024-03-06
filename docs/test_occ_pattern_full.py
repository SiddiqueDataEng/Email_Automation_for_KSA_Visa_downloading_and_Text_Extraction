"""Test occupation pattern to capture full text"""
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

# Find the occupation section
idx = normalized.find('Occupation')
if idx > 0:
    snippet = normalized[idx-50:idx+20]
    print("Text around Occupation:")
    print(repr(snippet))
    print()
    
    # Test pattern to capture full text including Arabic
    pattern = r'([A-Z][a-z]+[\s\xa0]+[\u0600-\u06FF\uFE00-\uFEFF\s\xa0]*)\s*[\u2010-\u2015\-]?\s*Occupation'
    match = re.search(pattern, snippet, re.IGNORECASE)
    
    if match:
        print(f"MATCH: {repr(match.group(1))}")
    else:
        print("NO MATCH")
        
        # Try simpler
        pattern2 = r'([A-Z][a-z]+[^\n]*?)\s*Occupation'
        match2 = re.search(pattern2, snippet, re.IGNORECASE)
        if match2:
            print(f"Simple MATCH: {repr(match2.group(1))}")
