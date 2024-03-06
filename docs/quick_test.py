"""Quick test - process 2 PDFs and show results"""
import os
from pdf_processor_advanced import process_pdf

def test_quick():
    base_path = r"\\COUNTER3\Shared Data\Visa_Slips_Automated"
    
    # Find 2 PDFs
    pdfs = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('_extracted.pdf'):
                pdfs.append(os.path.join(root, file))
                if len(pdfs) >= 2:
                    break
        if len(pdfs) >= 2:
            break
    
    if not pdfs:
        print("No PDFs found")
        return
    
    print("="*80)
    print("QUICK EXTRACTION TEST")
    print("="*80)
    
    for idx, pdf_path in enumerate(pdfs, 1):
        filename = os.path.basename(pdf_path)
        print(f"\n[{idx}] Processing: {filename}")
        print("-"*80)
        
        try:
            data = process_pdf(pdf_path)
            
            # Display key fields
            print(f"Visa No:        {data.get('Visa No', 'NOT FOUND')}")
            print(f"Name:           {data.get('Name', 'NOT FOUND')}")
            print(f"Passport:       {data.get('Passport No', 'NOT FOUND')}")
            print(f"Nationality:    {data.get('Nationality', 'NOT FOUND')}")
            print(f"Valid From:     {data.get('Valid from', 'NOT FOUND')}")
            print(f"Valid Until:    {data.get('Valid until', 'NOT FOUND')}")
            print(f"Duration:       {data.get('Duration of Stay', 'NOT FOUND')}")
            print(f"Visa Type:      {data.get('Visa Type', 'NOT FOUND')}")
            print(f"Employer:       {data.get('Employer name', 'NOT FOUND')}")
            print(f"Occupation:     {data.get('Occupation', 'NOT FOUND')}")
            print(f"Ref. No:        {data.get('Ref. No', 'NOT FOUND')}")
            print(f"Ref. Date:      {data.get('Ref. Date', 'NOT FOUND')}")
            
            # Count filled fields
            filled = sum(1 for v in data.values() if v)
            total = len(data)
            print(f"\nCompleteness:   {filled}/{total} fields ({filled/total*100:.0f}%)")
            
        except Exception as e:
            print(f"ERROR: {e}")
    
    print("\n" + "="*80)
    print("✓ Test complete!")
    print("="*80)

if __name__ == "__main__":
    test_quick()
