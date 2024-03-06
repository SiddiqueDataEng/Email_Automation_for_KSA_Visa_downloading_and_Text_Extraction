"""Test single PDF extraction with detailed debugging"""
import os
import sys
from pdf_processor_advanced import process_pdf

def test_single_pdf(pdf_path):
    """Test extraction on a single PDF with detailed output"""
    
    if not os.path.exists(pdf_path):
        print(f"✗ File not found: {pdf_path}")
        return
    
    print("\n" + "="*80)
    print(f"TESTING: {os.path.basename(pdf_path)}")
    print("="*80)
    print()
    
    try:
        print("Processing PDF...")
        data = process_pdf(pdf_path)
        
        print("\n" + "-"*80)
        print("EXTRACTION RESULTS")
        print("-"*80)
        
        # Display all fields
        fields = [
            'Visa No',
            'Application No',
            'Name',
            'Passport No',
            'Nationality',
            'Valid from',
            'Valid until',
            'Duration of Stay',
            'Visa Type',
            'Ref. No',
            'Ref. Date',
            'Occupation',
            'Employer name',
            'Place of issue',
        ]
        
        for field in fields:
            value = data.get(field, 'N/A')
            status = "✓" if value else "✗"
            print(f"{status} {field:20s}: {value}")
        
        # Calculate completeness
        filled = sum(1 for f in fields if data.get(f))
        completeness = (filled / len(fields) * 100) if fields else 0
        
        print()
        print(f"Completeness: {filled}/{len(fields)} fields ({completeness:.0f}%)")
        
        # Highlight critical fields
        print()
        print("Critical Fields Check:")
        critical = ['Visa No', 'Passport No', 'Name', 'Valid from']
        for field in critical:
            value = data.get(field, '')
            status = "✓ OK" if value else "✗ MISSING"
            print(f"  {status:10s} {field}: {value}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    
    # Check if PDF path provided
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        # Find first PDF in the default location
        base_path = r"\\COUNTER3\Shared Data\Visa_Slips_Automated"
        
        print(f"Searching for PDFs in: {base_path}")
        
        for root, dirs, files in os.walk(base_path):
            for file in files:
                if file.endswith('_extracted.pdf'):
                    pdf_path = os.path.join(root, file)
                    print(f"Found: {file}")
                    break
            if 'pdf_path' in locals():
                break
        
        if 'pdf_path' not in locals():
            print("✗ No PDFs found")
            print("\nUsage: python test_single_pdf.py <path_to_pdf>")
            return
    
    test_single_pdf(pdf_path)

if __name__ == "__main__":
    main()
