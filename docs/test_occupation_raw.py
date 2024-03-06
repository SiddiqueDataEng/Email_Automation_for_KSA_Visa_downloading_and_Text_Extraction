"""Test what occupation value is before cleaning"""
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

# Get raw text
text = processor._extract_text_pypdf(pdf_path)
normalized = re.sub(r'[ \t\xa0]+', ' ', text)

# Extract fields WITHOUT cleaning
data_raw = processor._extract_fields(normalized)

print("Raw extracted Occupation:", repr(data_raw.get('Occupation', '')))
print("Raw extracted Employer:", repr(data_raw.get('Employer name', ''))[:100])

# Now with full processing
data_clean = processor.process_pdf(pdf_path)

print("\nCleaned Occupation:", repr(data_clean.get('Occupation', '')))
print("Cleaned Employer:", repr(data_clean.get('Employer name', ''))[:100])
