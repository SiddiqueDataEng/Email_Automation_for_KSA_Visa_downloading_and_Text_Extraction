"""Test PDF extraction on a few samples and display results in a table"""
import os
import sys
from pdf_processor_advanced import process_pdf
from tabulate import tabulate
from datetime import datetime

def find_sample_pdfs(base_path, count=5):
    """Find sample PDFs for testing"""
    pdfs = []
    
    if not os.path.exists(base_path):
        print(f"⚠ Path not found: {base_path}")
        return pdfs
    
    print(f"Scanning: {base_path}")
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith('_extracted.pdf'):
                pdfs.append({
                    'path': os.path.join(root, file),
                    'filename': file,
                    'folder': os.path.basename(root)
                })
                if len(pdfs) >= count:
                    return pdfs
    
    return pdfs

def test_pdf_extraction(pdf_info):
    """Extract data from a single PDF"""
    try:
        print(f"  Processing: {pdf_info['filename']}...", end=' ')
        start_time = datetime.now()
        
        data = process_pdf(pdf_info['path'])
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"✓ ({elapsed:.2f}s)")
        
        # Calculate completeness
        total_fields = 14  # Main fields we care about
        filled_fields = sum(1 for k, v in data.items() if v and k in [
            'Visa No', 'Application No', 'Name', 'Passport No', 'Nationality',
            'Valid from', 'Valid until', 'Duration of Stay', 'Visa Type',
            'Ref. No', 'Ref. Date', 'Occupation', 'Employer name', 'Place of issue'
        ])
        
        completeness = (filled_fields / total_fields * 100) if total_fields > 0 else 0
        
        return {
            'filename': pdf_info['filename'][:30],  # Truncate for display
            'folder': pdf_info['folder'],
            'visa_no': data.get('Visa No', '')[:15],
            'name': data.get('Name', '')[:25],
            'passport': data.get('Passport No', '')[:12],
            'nationality': data.get('Nationality', '')[:15],
            'valid_from': data.get('Valid from', '')[:12],
            'valid_until': data.get('Valid until', '')[:12],
            'visa_type': data.get('Visa Type', '')[:15],
            'employer': data.get('Employer name', '')[:30],
            'occupation': data.get('Occupation', '')[:25],
            'ref_no': data.get('Ref. No', '')[:12],
            'completeness': f"{completeness:.0f}%",
            'time': f"{elapsed:.2f}s",
            'full_data': data
        }
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def display_summary_table(results):
    """Display summary table"""
    if not results:
        print("No results to display")
        return
    
    print("\n" + "="*120)
    print("EXTRACTION SUMMARY")
    print("="*120)
    
    summary_data = []
    for r in results:
        summary_data.append([
            r['filename'],
            r['folder'],
            r['visa_no'],
            r['name'],
            r['passport'],
            r['nationality'],
            r['completeness'],
            r['time']
        ])
    
    headers = ['Filename', 'Date', 'Visa No', 'Name', 'Passport', 'Nationality', 'Complete', 'Time']
    print(tabulate(summary_data, headers=headers, tablefmt='grid'))

def display_detailed_table(results):
    """Display detailed extraction table"""
    if not results:
        return
    
    print("\n" + "="*120)
    print("DETAILED EXTRACTION RESULTS")
    print("="*120)
    
    for idx, r in enumerate(results, 1):
        print(f"\n[{idx}] {r['filename']} ({r['folder']})")
        print("-" * 120)
        
        data = r['full_data']
        detail_data = [
            ['Visa No', data.get('Visa No', 'N/A')],
            ['Application No', data.get('Application No', 'N/A')],
            ['Name', data.get('Name', 'N/A')],
            ['Passport No', data.get('Passport No', 'N/A')],
            ['Nationality', data.get('Nationality', 'N/A')],
            ['Valid From', data.get('Valid from', 'N/A')],
            ['Valid Until', data.get('Valid until', 'N/A')],
            ['Duration', data.get('Duration of Stay', 'N/A')],
            ['Visa Type', data.get('Visa Type', 'N/A')],
            ['Ref. No', data.get('Ref. No', 'N/A')],
            ['Ref. Date', data.get('Ref. Date', 'N/A')],
            ['Occupation', data.get('Occupation', 'N/A')],
            ['Employer', data.get('Employer name', 'N/A')],
            ['Place of Issue', data.get('Place of issue', 'N/A')],
        ]
        
        print(tabulate(detail_data, headers=['Field', 'Value'], tablefmt='simple'))

def display_statistics(results):
    """Display extraction statistics"""
    if not results:
        return
    
    print("\n" + "="*120)
    print("STATISTICS")
    print("="*120)
    
    total = len(results)
    avg_time = sum(float(r['time'].replace('s', '')) for r in results) / total
    avg_completeness = sum(float(r['completeness'].replace('%', '')) for r in results) / total
    
    # Field-level statistics
    field_stats = {}
    for r in results:
        for key, value in r['full_data'].items():
            if key not in field_stats:
                field_stats[key] = {'filled': 0, 'empty': 0}
            if value:
                field_stats[key]['filled'] += 1
            else:
                field_stats[key]['empty'] += 1
    
    stats_data = [
        ['Total PDFs Processed', total],
        ['Average Processing Time', f"{avg_time:.2f}s"],
        ['Average Completeness', f"{avg_completeness:.1f}%"],
        ['', ''],
        ['Field Extraction Rates:', ''],
    ]
    
    # Add field-specific stats
    important_fields = ['Visa No', 'Name', 'Passport No', 'Valid from', 'Valid until', 
                       'Nationality', 'Employer name', 'Visa Type']
    
    for field in important_fields:
        if field in field_stats:
            filled = field_stats[field]['filled']
            rate = (filled / total * 100) if total > 0 else 0
            stats_data.append([f"  {field}", f"{filled}/{total} ({rate:.0f}%)"])
    
    print(tabulate(stats_data, tablefmt='simple'))

def main():
    """Main test function"""
    print("\n" + "="*120)
    print("PDF EXTRACTION TEST - SAMPLE ANALYSIS")
    print("="*120)
    print()
    
    # Configuration
    base_path = r"\\COUNTER3\Shared Data\Visa_Slips_Automated"
    sample_count = 5
    
    if len(sys.argv) > 1:
        try:
            sample_count = int(sys.argv[1])
        except:
            pass
    
    print(f"Configuration:")
    print(f"  Base Path: {base_path}")
    print(f"  Sample Count: {sample_count}")
    print()
    
    # Find sample PDFs
    print("Step 1: Finding sample PDFs...")
    sample_pdfs = find_sample_pdfs(base_path, sample_count)
    
    if not sample_pdfs:
        print("✗ No PDFs found for testing")
        return
    
    print(f"✓ Found {len(sample_pdfs)} sample PDF(s)")
    print()
    
    # Process PDFs
    print("Step 2: Processing PDFs with advanced OCR...")
    results = []
    
    for pdf_info in sample_pdfs:
        result = test_pdf_extraction(pdf_info)
        if result:
            results.append(result)
    
    print()
    print(f"✓ Successfully processed {len(results)}/{len(sample_pdfs)} PDFs")
    
    if not results:
        print("✗ No successful extractions")
        return
    
    # Display results
    display_summary_table(results)
    display_detailed_table(results)
    display_statistics(results)
    
    print("\n" + "="*120)
    print("TEST COMPLETE")
    print("="*120)
    print()
    print("Next steps:")
    print("  1. Review the extraction quality above")
    print("  2. If satisfied, use dashboard 'Retry Extraction' to process all PDFs")
    print("  3. Open http://127.0.0.1:5000 to access the dashboard")
    print()

if __name__ == "__main__":
    # Check if tabulate is installed
    try:
        from tabulate import tabulate
    except ImportError:
        print("Installing tabulate for better table display...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tabulate", "--quiet"])
        from tabulate import tabulate
    
    main()
