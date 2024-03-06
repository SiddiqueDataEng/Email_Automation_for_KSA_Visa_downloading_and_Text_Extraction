"""Test actual extraction with debug output"""
import os
import re
from pdf_processor_advanced import AdvancedPDFProcessor

def test_with_debug():
    base_path = r"\\COUNTER3\Shared Data\Visa_Slips_Automated"
    
    # Find first PDF
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('_extracted.pdf'):
                pdf_path = os.path.join(root, file)
                break
        if 'pdf_path' in locals():
            break
    
    if 'pdf_path' not in locals():
        print("No PDF found")
        return
    
    print(f"Testing: {os.path.basename(pdf_path)}\n")
    
    processor = AdvancedPDFProcessor()
    
    # Extract text
    text = processor._extract_text_pypdf(pdf_path)
    
    # Show snippet around Nationality
    print("="*80)
    print("TEXT AROUND 'Nationality':")
    print("="*80)
    idx = text.find('Nationality')
    if idx > 0:
        snippet = text[max(0, idx-100):idx+100]
        # Replace Arabic with [AR] for display
        snippet = re.sub(r'[\u0600-\u06FF]', '[AR]', snippet)
        print(snippet)
    print()
    
    # Show snippet around Occupation
    print("="*80)
    print("TEXT AROUND 'Occupation':")
    print("="*80)
    idx = text.find('Occupation')
    if idx > 0:
        snippet = text[max(0, idx-100):idx+100]
        snippet = re.sub(r'[\u0600-\u06FF]', '[AR]', snippet)
        print(snippet)
    print()
    
    # Show snippet around Employer
    print("="*80)
    print("TEXT AROUND 'Employer':")
    print("="*80)
    idx = text.find('Employer')
    if idx > 0:
        snippet = text[max(0, idx-100):idx+100]
        snippet = re.sub(r'[\u0600-\u06FF]', '[AR]', snippet)
        print(snippet)
    print()
    
    # Show snippet around Application
    print("="*80)
    print("TEXT AROUND 'Application':")
    print("="*80)
    idx = text.find('Application')
    if idx > 0:
        snippet = text[max(0, idx-200):idx+100]
        snippet = re.sub(r'[\u0600-\u06FF]', '[AR]', snippet)
        print(snippet)
    else:
        # Search for E followed by digits
        match = re.search(r'([A-Z]\d{9,10})', text)
        if match:
            print(f"Found Application No pattern: {match.group(1)}")
            idx = match.start()
            snippet = text[max(0, idx-50):idx+50]
            snippet = re.sub(r'[\u0600-\u06FF]', '[AR]', snippet)
            print(snippet)
        else:
            print("Not found")
    print()
    
    # Now test extraction
    print("="*80)
    print("EXTRACTION RESULTS:")
    print("="*80)
    data = processor.process_pdf(pdf_path)
    
    print(f"Nationality: '{data.get('Nationality', '')}'")
    print(f"Occupation: '{data.get('Occupation', '')}'")
    print(f"Employer: '{data.get('Employer name', '')}'")
    print(f"Application No: '{data.get('Application No', '')}'")

if __name__ == "__main__":
    test_with_debug()
