"""Test OCR functionality and process a few sample PDFs"""
import os
import sys
from pdf_processor_advanced import process_pdf, OCR_AVAILABLE

def test_ocr_setup():
    """Test if OCR is properly configured"""
    print("="*60)
    print("OCR Configuration Test")
    print("="*60)
    
    if OCR_AVAILABLE:
        print("✓ OCR libraries are available")
        try:
            import pytesseract
            version = pytesseract.get_tesseract_version()
            print(f"✓ Tesseract version: {version}")
            
            # Test if poppler is available
            try:
                from pdf2image import convert_from_path
                print("✓ pdf2image library available")
                print("⚠ Note: Poppler is required for pdf2image to work")
                print("  Download from: https://github.com/oschwartz10612/poppler-windows/releases/")
            except Exception as e:
                print(f"⚠ pdf2image issue: {e}")
        except Exception as e:
            print(f"⚠ Tesseract configuration issue: {e}")
    else:
        print("✗ OCR libraries not available")
        print("  Install with: pip install pytesseract pdf2image Pillow opencv-python")
    
    print("="*60)
    print()

def find_sample_pdfs(base_path, max_files=3):
    """Find a few sample PDFs to test"""
    pdfs = []
    
    if not os.path.exists(base_path):
        print(f"⚠ Path not found: {base_path}")
        return pdfs
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('.pdf') and not file.endswith('_extracted.pdf'):
                pdfs.append(os.path.join(root, file))
                if len(pdfs) >= max_files:
                    return pdfs
    
    return pdfs

def test_pdf_extraction(pdf_path):
    """Test extraction on a single PDF"""
    print(f"\nTesting: {os.path.basename(pdf_path)}")
    print("-" * 60)
    
    try:
        data = process_pdf(pdf_path)
        
        # Display extracted data
        print("\nExtracted Data:")
        for key, value in data.items():
            if value:
                print(f"  {key:20s}: {value}")
        
        # Check completeness
        critical_fields = ['Visa No', 'Name', 'Passport No', 'Valid from']
        missing = [f for f in critical_fields if not data.get(f)]
        
        if missing:
            print(f"\n⚠ Missing critical fields: {', '.join(missing)}")
        else:
            print("\n✓ All critical fields extracted successfully")
        
        return data
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("Saudi eVisa OCR Test Suite")
    print("="*60 + "\n")
    
    # Test 1: Check OCR setup
    test_ocr_setup()
    
    # Test 2: Find sample PDFs
    base_path = r"\\COUNTER3\Shared Data\Visa_Slips_Automated"
    print(f"Searching for sample PDFs in: {base_path}")
    
    sample_pdfs = find_sample_pdfs(base_path, max_files=3)
    
    if not sample_pdfs:
        print("⚠ No PDFs found for testing")
        print("\nTo test manually, run:")
        print("  python test_ocr.py <path_to_pdf>")
        return
    
    print(f"✓ Found {len(sample_pdfs)} sample PDF(s)\n")
    
    # Test 3: Process sample PDFs
    results = []
    for pdf_path in sample_pdfs:
        result = test_pdf_extraction(pdf_path)
        if result:
            results.append((pdf_path, result))
        print()
    
    # Summary
    print("="*60)
    print("Test Summary")
    print("="*60)
    print(f"Total PDFs tested: {len(sample_pdfs)}")
    print(f"Successfully extracted: {len(results)}")
    
    if results:
        print("\n✓ OCR system is working!")
        print("\nSample extraction quality:")
        for pdf_path, data in results:
            filled_fields = sum(1 for v in data.values() if v)
            total_fields = len(data)
            percentage = (filled_fields / total_fields * 100) if total_fields > 0 else 0
            print(f"  {os.path.basename(pdf_path)}: {filled_fields}/{total_fields} fields ({percentage:.0f}%)")
    else:
        print("\n⚠ No successful extractions")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific PDF
        pdf_path = sys.argv[1]
        if os.path.exists(pdf_path):
            test_ocr_setup()
            test_pdf_extraction(pdf_path)
        else:
            print(f"Error: File not found: {pdf_path}")
    else:
        # Run full test suite
        main()
