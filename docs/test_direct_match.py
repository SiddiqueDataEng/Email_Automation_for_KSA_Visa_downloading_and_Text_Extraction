"""Test pattern matching directly on PDF text"""
import os
import re
from pdf_processor_advanced import AdvancedPDFProcessor

def test_direct():
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
    
    print("Testing patterns on RAW text (no normalization):\n")
    
    # Test Nationality
    pattern = r'([A-Z][a-z]+)\s+[\u2010-\u2015\-]\s+[\u0600-\u06FF\s]+Nationality'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    print(f"Nationality: {match.group(1) if match else 'NO MATCH'}")
    
    # Test Occupation
    pattern = r'([A-Z][A-Za-z\s]+?)\s+[\u0600-\u06FF\s]+[\u2010-\u2015\-]\s+Occupation'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    print(f"Occupation: {match.group(1) if match else 'NO MATCH'}")
    
    # Test Employer
    pattern = r'([\u0600-\u06FF\s]+)\s+Employer\s*name'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        result = match.group(1)[:50]
        print(f"Employer: {repr(result)}")
    else:
        print("Employer: NO MATCH")
    
    # Test Application No
    pattern = r'\b([A-Z]\d{9,10})\b'
    matches = re.findall(pattern, text)
    print(f"Application No candidates: {matches}")

if __name__ == "__main__":
    test_direct()
