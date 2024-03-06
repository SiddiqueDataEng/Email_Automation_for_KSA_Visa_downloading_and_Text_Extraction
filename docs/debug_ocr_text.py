"""Debug OCR - show raw extracted text"""
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'ignore')

from pdf_processor_advanced import AdvancedPDFProcessor

def safe_print(text, max_len=1000):
    """Print text safely, removing problematic characters"""
    if not text:
        print("(empty)")
        return
    
    # Remove Arabic and special characters for display
    import re
    text = re.sub(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]', '[AR]', text)
    text = text[:max_len]
    print(text)

def debug_pdf(pdf_path):
    """Show raw OCR text from PDF"""
    
    if not os.path.exists(pdf_path):
        print(f"[ERROR] File not found: {pdf_path}")
        return
    
    print("\n" + "="*80)
    print(f"DEBUG: {os.path.basename(pdf_path)}")
    print("="*80)
    print()
    
    processor = AdvancedPDFProcessor()
    
    # Extract text using PyPDF2
    print("1. PyPDF2 Text Extraction:")
    print("-"*80)
    text_pypdf = processor._extract_text_pypdf(pdf_path)
    safe_print(text_pypdf, 1000)
    print()
    
    # Extract text using OCR
    if processor.ocr_available:
        print("2. OCR Text Extraction:")
        print("-"*80)
        text_ocr = processor._extract_text_ocr(pdf_path)
        safe_print(text_ocr, 1500)
        print()
    
    # Show extraction results
    print("3. Extracted Fields:")
    print("-"*80)
    data = processor.process_pdf(pdf_path)
    
    for key, value in data.items():
        status = "[OK]" if value else "[--]"
        print(f"{status} {key:20s}: '{value}'")
    
    print("\n" + "="*80)

def main():
    # Find first PDF
    base_path = r"\\COUNTER3\Shared Data\Visa_Slips_Automated"
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        print(f"Searching for PDF in: {base_path}")
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('_extracted.pdf'):
                    pdf_path = os.path.join(root, file)
                    print(f"Found: {file}\n")
                    break
            if 'pdf_path' in locals():
                break
        
        if 'pdf_path' not in locals():
            print("[ERROR] No PDFs found")
            return
    
    debug_pdf(pdf_path)

if __name__ == "__main__":
    main()
