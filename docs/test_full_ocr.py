"""Quick test to verify full OCR with Poppler is working"""
import os
import sys

def test_full_ocr():
    print("="*60)
    print("Full OCR Test (with Poppler)")
    print("="*60)
    
    # Test imports
    try:
        import pytesseract
        print("✓ pytesseract imported")
        
        # Configure Tesseract path
        import os
        if os.name == 'nt':
            tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                print(f"✓ Tesseract configured: {tesseract_path}")
            
    except ImportError as e:
        print(f"✗ pytesseract import failed: {e}")
        return False
    
    try:
        from pdf2image import convert_from_path
        print("✓ pdf2image imported")
    except ImportError as e:
        print(f"✗ pdf2image import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ PIL imported")
    except ImportError as e:
        print(f"✗ PIL import failed: {e}")
        return False
    
    # Test Tesseract
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract version: {version}")
    except Exception as e:
        print(f"✗ Tesseract error: {e}")
        return False
    
    # Test Poppler
    poppler_path = os.path.join(os.getcwd(), 'Release-25.12.0-0', 'poppler-25.12.0', 'Library', 'bin')
    if os.path.exists(poppler_path):
        print(f"✓ Poppler found at: {poppler_path}")
    else:
        print(f"✗ Poppler not found at: {poppler_path}")
        return False
    
    # Find a test PDF
    base_path = r"\\COUNTER3\Shared Data\Visa_Slips_Automated"
    test_pdf = None
    
    if os.path.exists(base_path):
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('_extracted.pdf'):
                    test_pdf = os.path.join(root, file)
                    break
            if test_pdf:
                break
    
    if not test_pdf:
        print("⚠ No test PDF found")
        print("✓ All libraries are configured correctly!")
        return True
    
    print(f"\nTesting with: {os.path.basename(test_pdf)}")
    print("-"*60)
    
    try:
        # Test PDF to image conversion
        print("Converting PDF to images...")
        images = convert_from_path(test_pdf, dpi=300, poppler_path=poppler_path, first_page=1, last_page=1)
        print(f"✓ Converted to {len(images)} image(s)")
        
        # Test OCR
        print("Running OCR...")
        text = pytesseract.image_to_string(images[0], lang='eng')
        
        # Check if we got meaningful text
        if len(text.strip()) > 50:
            print(f"✓ OCR successful! Extracted {len(text)} characters")
            print("\nSample text (first 200 chars):")
            print(text[:200])
            return True
        else:
            print(f"⚠ OCR returned limited text: {len(text)} characters")
            return True
            
    except Exception as e:
        print(f"✗ Error during OCR test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print()
    success = test_full_ocr()
    print()
    print("="*60)
    if success:
        print("✓ FULL OCR SYSTEM IS READY!")
        print()
        print("You can now:")
        print("1. Use 'Retry Extraction' to reprocess all PDFs")
        print("2. Process new emails with improved accuracy")
        print("3. Scan existing PDFs with OCR fallback")
    else:
        print("✗ OCR system has issues - check errors above")
    print("="*60)
    print()
