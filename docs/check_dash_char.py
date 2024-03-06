"""Check what dash character is in the PDF"""
import os
from pdf_processor_advanced import AdvancedPDFProcessor

base_path = r"\\COUNTER3\Shared Data\Visa_Slips_Automated"

# Find first PDF
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith('_extracted.pdf'):
            pdf_path = os.path.join(root, file)
            break
    if 'pdf_path' in locals():
        break

processor = AdvancedPDFProcessor()
text = processor._extract_text_pypdf(pdf_path)

# Find the dash near "Nationality"
idx = text.find('Nationality')
if idx > 0:
    snippet = text[idx-50:idx+20]
    print("Text around Nationality:")
    print(repr(snippet))
    print()
    
    # Find dash characters
    for i, char in enumerate(snippet):
        if ord(char) > 127 and char not in 'باكستان':  # Non-ASCII, not Arabic
            print(f"Char at position {i}: '{char}' = U+{ord(char):04X}")
