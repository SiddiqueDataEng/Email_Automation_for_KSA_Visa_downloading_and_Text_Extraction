"""Find where occupation actually is in the text"""
import os
import re
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

# Normalize
normalized = re.sub(r'[ \t\xa0]+', ' ', text)

print("Looking for 'Builder' in text...")
idx = normalized.find('Builder')
if idx > 0:
    print(f"\nFound at position {idx}")
    print("Context:")
    print(normalized[idx-100:idx+100])
    print()
    
    # What's before and after?
    before = normalized[max(0, idx-200):idx]
    after = normalized[idx:idx+200]
    
    print("Labels before Builder:")
    labels = re.findall(r'(Ref\.|Date|Passport|No\.|Occupation|Employer)', before)
    print(labels[-5:] if len(labels) > 5 else labels)
    
    print("\nLabels after Builder:")
    labels = re.findall(r'(Ref\.|Date|Passport|No\.|Occupation|Employer)', after)
    print(labels[:5])
