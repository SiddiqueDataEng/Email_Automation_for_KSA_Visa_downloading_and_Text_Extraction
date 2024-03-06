"""Analyze exact text structure for missing fields"""
import os
import re
from pdf_processor_advanced import AdvancedPDFProcessor

def analyze_pdf():
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
    
    print("="*80)
    print("ANALYZING TEXT STRUCTURE")
    print("="*80)
    print()
    
    # 1. Nationality
    print("1. NATIONALITY SECTION:")
    print("-"*80)
    idx = text.find('Nationality')
    if idx > 0:
        snippet = text[idx-60:idx+20]
        print("Raw text:", repr(snippet))
        print()
        
        # Test pattern
        pattern = r'([A-Z][a-z]+)[\s\xa0]+[\u2010-\u2015\-][\s\xa0]+[\u0600-\u06FF\s\xa0]+Nationality'
        match = re.search(pattern, snippet, re.IGNORECASE | re.DOTALL)
        print(f"Pattern match: {match.group(1) if match else 'NO MATCH'}")
        
        # Try simpler pattern
        pattern2 = r'([A-Z][a-z]+)[\s\xa0\u2010-\u2015\-\u0600-\u06FF]+Nationality'
        match2 = re.search(pattern2, snippet, re.IGNORECASE | re.DOTALL)
        print(f"Simple pattern: {match2.group(1) if match2 else 'NO MATCH'}")
    print()
    
    # 2. Occupation
    print("2. OCCUPATION SECTION:")
    print("-"*80)
    idx = text.find('Occupation')
    if idx > 0:
        snippet = text[idx-60:idx+20]
        print("Raw text:", repr(snippet))
        print()
        
        # Test pattern
        pattern = r'([A-Z][A-Za-z\s]+?)[\s\xa0]+[\u0600-\u06FF\s\xa0]+[\u2010-\u2015\-][\s\xa0]+Occupation'
        match = re.search(pattern, snippet, re.IGNORECASE | re.DOTALL)
        print(f"Pattern match: {match.group(1) if match else 'NO MATCH'}")
        
        # Try simpler pattern
        pattern2 = r'([A-Z][a-z]+)[\s\xa0\u0600-\u06FF\u2010-\u2015\-]+Occupation'
        match2 = re.search(pattern2, snippet, re.IGNORECASE | re.DOTALL)
        print(f"Simple pattern: {match2.group(1) if match2 else 'NO MATCH'}")
    print()
    
    # 3. Employer
    print("3. EMPLOYER SECTION:")
    print("-"*80)
    idx = text.find('Employer')
    if idx > 0:
        snippet = text[idx-100:idx+30]
        print("Raw text:", repr(snippet))
        print()
        
        # The employer name is in Arabic before "Employer name"
        # We need to extract it and transliterate or keep as is
        pattern = r'([\u0600-\u06FF\s\xa0]+)[\s\xa0]+Employer[\s\xa0]+name'
        match = re.search(pattern, snippet, re.IGNORECASE | re.DOTALL)
        if match:
            arabic_text = match.group(1).strip()
            print(f"Arabic employer: {repr(arabic_text[:50])}")
            print("Note: Employer names are in Arabic in the PDF")
        else:
            print("Pattern match: NO MATCH")
    print()
    
    print("="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print("1. Nationality & Occupation: Use simpler patterns that match any characters")
    print("2. Employer: Keep Arabic text (no English equivalent in PDF)")
    print("3. Consider OCR as fallback if PyPDF2 text has encoding issues")
    print()

if __name__ == "__main__":
    analyze_pdf()
