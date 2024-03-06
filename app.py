from flask import Flask, render_template, jsonify, request, Response, send_file
import imaplib
import email
from email.header import decode_header
import os
from datetime import datetime
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import io

# Try advanced processor first, fallback to basic
try:
    from pdf_processor_advanced import process_pdf
    print("✓ Using advanced PDF processor with OCR support")
except ImportError:
    from pdf_processor import process_pdf
    print("⚠ Using basic PDF processor (install OCR libraries for better accuracy)")

from config import Config
from database import VisaDatabase
from audio_announcer import announcer

app = Flask(__name__)
config = Config()
db = VisaDatabase()

# Queue for background processing
processing_queue = Queue()
processing_active = False
auto_monitor_active = False
auto_monitor_thread = None

@app.route('/')
def dashboard():
    stats = get_statistics()
    return render_template('dashboard.html', stats=stats)

@app.route('/api/export-excel', methods=['POST'])
def export_excel():
    """Export selected records to Excel"""
    import pandas as pd
    
    record_ids = request.json.get('record_ids', [])
    
    if not record_ids:
        # Export all records
        records = db.get_all_records()
    else:
        # Export selected records
        records = [r for r in db.get_all_records() if r.get('id') in record_ids]
    
    if not records:
        return jsonify({'success': False, 'error': 'No records to export'})
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Select and order columns
    columns = ['visa_no', 'application_no', 'name', 'passport_no', 'nationality', 
               'visa_type', 'valid_from', 'valid_until', 'duration_of_stay',
               'ref_no', 'ref_date', 'occupation', 'employer_name', 
               'place_of_issue', 'visa_fees', 'processed_date']
    
    df = df[[col for col in columns if col in df.columns]]
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Visa Records')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Visa Records']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
    
    output.seek(0)
    
    filename = f'visa_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/auto-monitor/start', methods=['POST'])
def start_auto_monitor():
    """Start automatic monitoring"""
    global auto_monitor_active, auto_monitor_thread
    
    if auto_monitor_active:
        return jsonify({'success': False, 'message': 'Auto-monitor already running'})
    
    auto_monitor_active = True
    auto_monitor_thread = threading.Thread(target=auto_monitor_worker, daemon=True)
    auto_monitor_thread.start()
    
    return jsonify({'success': True, 'message': 'Auto-monitor started'})

@app.route('/api/auto-monitor/stop', methods=['POST'])
def stop_auto_monitor():
    """Stop automatic monitoring"""
    global auto_monitor_active
    
    auto_monitor_active = False
    
    return jsonify({'success': True, 'message': 'Auto-monitor stopped'})

@app.route('/api/auto-monitor/status', methods=['GET'])
def auto_monitor_status():
    """Get auto-monitor status"""
    return jsonify({'active': auto_monitor_active})

def auto_monitor_worker():
    """Background worker for auto-monitoring"""
    global auto_monitor_active
    
    # Get interval with fallback
    try:
        interval = getattr(config, 'check_interval', 300)
        if not interval or interval < 60:
            interval = 300
    except:
        interval = 300
    
    print(f"Auto-monitor interval: {interval} seconds")
    
    while auto_monitor_active:
        try:
            print(f"🔔 Auto-monitor: Checking for new emails...")
            
            # Process new emails
            for update in fetch_and_process_emails(include_downloaded=False):
                if update.get('type') == 'success' and update.get('record'):
                    # Announce new visa
                    record = update['record']
                    name = record.get('name', 'Unknown')
                    visa_no = record.get('visa_no', '')
                    announcer.announce_visa(name, visa_no)
            
            # Wait for next check
            for _ in range(interval):
                if not auto_monitor_active:
                    break
                time.sleep(1)
                
        except Exception as e:
            print(f"Auto-monitor error: {e}")
            time.sleep(60)  # Wait a minute before retrying
    
    print("🔕 Auto-monitor stopped")

@app.route('/api/process', methods=['POST'])
def process_emails():
    include_downloaded = request.json.get('include_downloaded', False) if request.json else False
    
    def generate():
        try:
            yield f"data: {json.dumps({'type': 'info', 'message': 'Connecting to Gmail...'})}\n\n"
            
            for update in fetch_and_process_emails(include_downloaded):
                yield f"data: {json.dumps(update)}\n\n"
                time.sleep(0.05)
            
            yield f"data: {json.dumps({'type': 'complete', 'message': 'Processing complete!'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stats')
def stats():
    return jsonify(get_statistics())

@app.route('/api/analytics')
def analytics():
    """Get detailed analytics data"""
    all_records = db.get_all_records()
    
    # Nationality distribution
    nationality_counts = {}
    for r in all_records:
        nat = r.get('nationality', 'Unknown')
        nationality_counts[nat] = nationality_counts.get(nat, 0) + 1
    
    # Employer distribution
    employer_counts = {}
    for r in all_records:
        emp = r.get('employer_name', 'Unknown')
        employer_counts[emp] = employer_counts.get(emp, 0) + 1
    
    # Occupation distribution
    occupation_counts = {}
    for r in all_records:
        occ = r.get('occupation', 'Unknown')
        if ' - ' in occ:
            occ = occ.split(' - ')[0]
        occupation_counts[occ] = occupation_counts.get(occ, 0) + 1
    
    # Visa type distribution
    visa_type_counts = {}
    for r in all_records:
        vtype = r.get('visa_type', 'Unknown')
        visa_type_counts[vtype] = visa_type_counts.get(vtype, 0) + 1
    
    # Duration distribution
    duration_counts = {}
    for r in all_records:
        dur = r.get('duration_of_stay', 'Unknown')
        duration_counts[dur] = duration_counts.get(dur, 0) + 1
    
    # Timeline data
    date_counts = {}
    for r in all_records:
        date = r.get('processed_date', 'Unknown')
        date_counts[date] = date_counts.get(date, 0) + 1
    
    return jsonify({
        'total_records': len(all_records),
        'nationality_distribution': nationality_counts,
        'employer_distribution': employer_counts,
        'occupation_distribution': occupation_counts,
        'visa_type_distribution': visa_type_counts,
        'duration_distribution': duration_counts,
        'timeline': date_counts
    })


@app.route('/api/records')
def get_records():
    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('search', '')
    
    # Get records
    if search:
        all_records = db.search_records(search)
    else:
        all_records = db.get_all_records()
    
    # Calculate pagination
    total = len(all_records)
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    start = (page - 1) * per_page
    end = start + per_page
    
    # Get page records
    records = all_records[start:end]
    
    return jsonify({
        'records': records,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
    })

@app.route('/api/records/date/<date>')
def get_records_by_date(date):
    records = db.get_records_by_date(date)
    return jsonify(records)

@app.route('/api/records/recent')
def get_recent_records():
    limit = request.args.get('limit', 10, type=int)
    records = db.get_all_records()[:limit]
    return jsonify(records)

@app.route('/api/open-folder', methods=['POST'])
def open_folder():
    import subprocess
    path = request.json.get('path')
    if path and os.path.exists(path):
        try:
            subprocess.Popen(f'explorer "{path}"')
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'success': False, 'error': 'Path not found'})

@app.route('/api/process-folder', methods=['POST'])
def process_folder_pdfs():
    """Process all PDFs in a specific date folder (for reprocessing)"""
    date = request.json.get('date')
    if not date:
        return jsonify({'success': False, 'error': 'Date required'})
    
    folder_path = os.path.join(config.save_path, date)
    if not os.path.exists(folder_path):
        return jsonify({'success': False, 'error': 'Folder not found'})
    
    # Find all PDFs in folder
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
    
    if not pdf_files:
        return jsonify({'success': False, 'error': 'No PDFs found'})
    
    # Process in parallel
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for pdf_file in pdf_files:
            pdf_info = {
                'pdf_path': os.path.join(folder_path, pdf_file),
                'filename': pdf_file,
                'date': date
            }
            futures.append(executor.submit(process_pdf_file, pdf_info))
        
        for future in as_completed(futures):
            result = future.result()
            if result['success']:
                results.append(result)
    
    return jsonify({'success': True, 'processed': len(results), 'total': len(pdf_files)})

@app.route('/api/scan-and-extract', methods=['POST'])
def scan_and_extract_pdfs():
    """Scan all folders and extract data from unprocessed PDFs"""
    
    def generate():
        try:
            base_path = config.save_path
            
            if not os.path.exists(base_path):
                yield f"data: {json.dumps({'type': 'error', 'message': 'Base path not found'})}\n\n"
                return
            
            yield f"data: {json.dumps({'type': 'info', 'message': '🔍 Scanning folders for PDFs...'})}\n\n"
            
            # Scan all date folders
            all_pdfs = []
            date_folders = []
            
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path):
                    date_folders.append((item, item_path))
            
            yield f"data: {json.dumps({'type': 'info', 'message': f'📁 Found {len(date_folders)} date folders'})}\n\n"
            
            # Find all unprocessed PDFs
            for date, folder_path in date_folders:
                pdf_files = [f for f in os.listdir(folder_path) 
                           if f.endswith('.pdf') and not f.endswith('_extracted.pdf')]
                
                for pdf_file in pdf_files:
                    all_pdfs.append({
                        'pdf_path': os.path.join(folder_path, pdf_file),
                        'filename': pdf_file,
                        'date': date
                    })
            
            total_pdfs = len(all_pdfs)
            
            if total_pdfs == 0:
                yield f"data: {json.dumps({'type': 'info', 'message': '✓ No unprocessed PDFs found'})}\n\n"
                yield f"data: {json.dumps({'type': 'complete', 'message': 'Scan complete'})}\n\n"
                return
            
            yield f"data: {json.dumps({'type': 'info', 'message': f'📄 Found {total_pdfs} unprocessed PDFs'})}\n\n"
            yield f"data: {json.dumps({'type': 'info', 'message': '⚡ Starting parallel extraction...'})}\n\n"
            
            # Process PDFs in parallel
            max_workers = min(8, total_pdfs)
            processed_count = 0
            success_count = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_pdf = {
                    executor.submit(process_and_rename_pdf, pdf_info): pdf_info 
                    for pdf_info in all_pdfs
                }
                
                for future in as_completed(future_to_pdf):
                    pdf_info = future_to_pdf[future]
                    processed_count += 1
                    
                    try:
                        result = future.result()
                        
                        if result['success']:
                            success_count += 1
                            visa_no = result['data'].get('Visa No', 'N/A')
                            msg = f"✓ [{processed_count}/{total_pdfs}] Extracted: {pdf_info['filename']} (Visa: {visa_no})"
                            yield f"data: {json.dumps({'type': 'success', 'message': msg})}\n\n"
                        elif result.get('duplicate'):
                            msg = f"⚠️ [{processed_count}/{total_pdfs}] Duplicate: {pdf_info['filename']}"
                            yield f"data: {json.dumps({'type': 'warning', 'message': msg})}\n\n"
                        else:
                            msg = f"⚠️ [{processed_count}/{total_pdfs}] Skipped: {pdf_info['filename']}"
                            yield f"data: {json.dumps({'type': 'warning', 'message': msg})}\n\n"
                        
                        # Update progress
                        progress_data = {'type': 'progress', 'current': processed_count, 'total': total_pdfs, 'folder': 'Extracting'}
                        yield f"data: {json.dumps(progress_data)}\n\n"
                        
                    except Exception as e:
                        error_msg = f"❌ Error processing {pdf_info['filename']}: {str(e)}"
                        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
            
            summary_data = {'type': 'summary', 'total_processed': success_count, 'total_scanned': total_pdfs}
            yield f"data: {json.dumps(summary_data)}\n\n"
            
            complete_msg = f"Extraction complete! Processed {success_count}/{total_pdfs} PDFs"
            yield f"data: {json.dumps({'type': 'complete', 'message': complete_msg})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/retry-extraction', methods=['POST'])
def retry_extraction():
    """Reprocess _extracted PDFs with improved OCR and update database"""
    
    def generate():
        try:
            base_path = config.save_path
            
            if not os.path.exists(base_path):
                yield f"data: {json.dumps({'type': 'error', 'message': 'Base path not found'})}\n\n"
                return
            
            yield f"data: {json.dumps({'type': 'info', 'message': '🔄 Scanning for previously extracted PDFs...'})}\n\n"
            
            # Find all _extracted PDFs
            all_pdfs = []
            date_folders = []
            
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path):
                    date_folders.append((item, item_path))
            
            yield f"data: {json.dumps({'type': 'info', 'message': f'📁 Scanning {len(date_folders)} date folders'})}\n\n"
            
            # Find all _extracted PDFs
            for date, folder_path in date_folders:
                pdf_files = [f for f in os.listdir(folder_path) 
                           if f.endswith('_extracted.pdf')]
                
                for pdf_file in pdf_files:
                    all_pdfs.append({
                        'pdf_path': os.path.join(folder_path, pdf_file),
                        'filename': pdf_file,
                        'date': date
                    })
            
            total_pdfs = len(all_pdfs)
            
            if total_pdfs == 0:
                yield f"data: {json.dumps({'type': 'info', 'message': '✓ No extracted PDFs found to retry'})}\n\n"
                yield f"data: {json.dumps({'type': 'complete', 'message': 'Scan complete'})}\n\n"
                return
            
            yield f"data: {json.dumps({'type': 'info', 'message': f'📄 Found {total_pdfs} extracted PDFs to reprocess'})}\n\n"
            yield f"data: {json.dumps({'type': 'info', 'message': '⚡ Starting parallel re-extraction with improved OCR...'})}\n\n"
            
            # Process PDFs in parallel
            max_workers = min(8, total_pdfs)
            processed_count = 0
            success_count = 0
            updated_count = 0
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_pdf = {
                    executor.submit(reprocess_extracted_pdf, pdf_info): pdf_info 
                    for pdf_info in all_pdfs
                }
                
                for future in as_completed(future_to_pdf):
                    pdf_info = future_to_pdf[future]
                    processed_count += 1
                    
                    try:
                        result = future.result()
                        
                        if result['success']:
                            success_count += 1
                            if result.get('updated'):
                                updated_count += 1
                            visa_no = result['data'].get('Visa No', 'N/A')
                            status = "Updated" if result.get('updated') else "Processed"
                            msg = f"✓ [{processed_count}/{total_pdfs}] {status}: {pdf_info['filename']} (Visa: {visa_no})"
                            yield f"data: {json.dumps({'type': 'success', 'message': msg})}\n\n"
                        else:
                            msg = f"⚠️ [{processed_count}/{total_pdfs}] Failed: {pdf_info['filename']}"
                            yield f"data: {json.dumps({'type': 'warning', 'message': msg})}\n\n"
                        
                        # Update progress
                        progress_data = {'type': 'progress', 'current': processed_count, 'total': total_pdfs, 'folder': 'Re-extracting'}
                        yield f"data: {json.dumps(progress_data)}\n\n"
                        
                    except Exception as e:
                        error_msg = f"❌ Error processing {pdf_info['filename']}: {str(e)}"
                        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
            
            summary_data = {'type': 'summary', 'total_processed': success_count, 'total_scanned': total_pdfs, 'updated': updated_count}
            yield f"data: {json.dumps(summary_data)}\n\n"
            
            complete_msg = f"Re-extraction complete! Processed {success_count}/{total_pdfs} PDFs ({updated_count} updated)"
            yield f"data: {json.dumps({'type': 'complete', 'message': complete_msg})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

def reprocess_extracted_pdf(pdf_info):
    """Reprocess an _extracted PDF and update database"""
    pdf_path = pdf_info['pdf_path']
    filename = pdf_info['filename']
    date = pdf_info['date']
    
    try:
        # Extract data from PDF with improved OCR
        visa_data = process_pdf(pdf_path)
        
        # Get passport number to find existing record
        passport_no = visa_data.get('Passport No', '')
        
        if not passport_no:
            return {
                'success': False,
                'reason': 'no_passport',
                'filename': filename,
                'date': date,
                'data': visa_data
            }
        
        # Check if record exists
        if db.record_exists_in_date(passport_no, date):
            # Update existing record
            record_updated = db.update_record_by_passport(passport_no, date, visa_data, filename)
            
            # Update Excel file
            excel_path = pdf_path.replace('_extracted.pdf', '_extracted.xlsx')
            if not os.path.exists(excel_path):
                excel_path = pdf_path.replace('.pdf', '.xlsx')
            save_to_excel(visa_data, excel_path)
            
            return {
                'success': True,
                'updated': record_updated,
                'filename': filename,
                'date': date,
                'data': visa_data
            }
        else:
            # Insert new record
            record_id = db.insert_record(visa_data, filename, date)
            
            # Create/update Excel file
            excel_path = pdf_path.replace('_extracted.pdf', '_extracted.xlsx')
            if not os.path.exists(excel_path):
                excel_path = pdf_path.replace('.pdf', '.xlsx')
            save_to_excel(visa_data, excel_path)
            
            return {
                'success': True,
                'updated': False,
                'record_id': record_id,
                'filename': filename,
                'date': date,
                'data': visa_data
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'filename': filename,
            'date': date,
            'data': {}
        }

def process_and_rename_pdf(pdf_info):
    """Process a PDF and rename it to mark as extracted"""
    pdf_path = pdf_info['pdf_path']
    filename = pdf_info['filename']
    date = pdf_info['date']
    
    try:
        # Extract data from PDF
        visa_data = process_pdf(pdf_path)
        
        # Check if record with same passport exists in same date folder
        passport_no = visa_data.get('Passport No', '')
        
        if passport_no and db.record_exists_in_date(passport_no, date):
            # Still rename to mark as processed
            new_path = pdf_path.replace('.pdf', '_extracted.pdf')
            if not os.path.exists(new_path):
                os.rename(pdf_path, new_path)
            
            return {
                'success': False,
                'duplicate': True,
                'reason': 'passport_exists_in_date',
                'filename': filename,
                'date': date,
                'data': visa_data
            }
        
        # Save to Excel
        excel_path = pdf_path.replace('.pdf', '.xlsx')
        save_to_excel(visa_data, excel_path)
        
        # Insert into database
        record_id = db.insert_record(visa_data, filename, date)
        
        # Rename PDF to mark as extracted
        new_path = pdf_path.replace('.pdf', '_extracted.pdf')
        if not os.path.exists(new_path):
            os.rename(pdf_path, new_path)
        
        return {
            'success': True,
            'duplicate': False,
            'record_id': record_id,
            'filename': filename,
            'date': date,
            'pdf_path': new_path,
            'excel_path': excel_path,
            'data': visa_data
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'filename': filename,
            'date': date,
            'data': {}
        }

@app.route('/api/config', methods=['GET', 'POST'])
def manage_config():
    if request.method == 'POST':
        config.update(request.json)
        return jsonify({'success': True})
    return jsonify(config.get_all())

def fetch_and_process_emails(include_downloaded=False):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(config.email, config.password)
    
    # Search in inbox, Visa/new, and optionally Visa/downloaded
    folders_to_check = ['inbox', '"Visa/new"']
    if include_downloaded:
        folders_to_check.append('"Visa/downloaded"')
    
    total_processed = 0
    processed_in_session = set()
    downloaded_pdfs = []  # Store PDFs for parallel processing
    
    # Phase 1: Quick download of all PDFs
    yield {'type': 'info', 'message': '⚡ Phase 1: Downloading PDFs...'}
    
    for folder in folders_to_check:
        try:
            status, _ = mail.select(folder)
            if status != 'OK':
                continue
            
            yield {'type': 'info', 'message': f'📁 Checking folder: {folder}'}
        except Exception as e:
            yield {'type': 'warning', 'message': f'⚠️ Could not access folder {folder}: {str(e)}'}
            continue
        
        search_criteria = f'(FROM "{config.from_email}"'
        if config.subject_filter:
            search_criteria += f' SUBJECT "{config.subject_filter}"'
        search_criteria += ')'
        
        _, messages = mail.search(None, search_criteria)
        if not messages[0]:
            yield {'type': 'info', 'message': f'No emails found in {folder}'}
            continue
        
        email_ids = messages[0].split()
        total_emails = len(email_ids)
        yield {'type': 'info', 'message': f'📧 Found {total_emails} emails in {folder}'}
        
        for idx, num in enumerate(email_ids, 1):
            try:
                # Create unique identifier for this email
                email_id = f"{folder}_{num.decode() if isinstance(num, bytes) else num}"
                
                # Skip if already processed in this session
                if email_id in processed_in_session:
                    continue
                
                yield {'type': 'progress', 'current': idx, 'total': total_emails, 'folder': folder}
                
                _, msg_data = mail.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                message = email.message_from_bytes(email_body)
                
                date_str = message.get('Date')
                email_date = email.utils.parsedate_to_datetime(date_str).strftime('%Y-%m-%d')
                
                pdf_found = False
                for part in message.walk():
                    if part.get_content_type() == 'application/pdf':
                        filename = part.get_filename()
                        if filename:
                            pdf_found = True
                            pdf_data = part.get_payload(decode=True)
                            
                            # Quick save PDF to disk
                            date_folder = os.path.join(config.save_path, email_date)
                            os.makedirs(date_folder, exist_ok=True)
                            pdf_path = os.path.join(date_folder, filename)
                            
                            # Check if already exists
                            if os.path.exists(pdf_path):
                                with open(pdf_path, 'rb') as f:
                                    if f.read() == pdf_data:
                                        yield {'type': 'warning', 'message': f'⚠️ Skipped (exists): {filename}'}
                                        processed_in_session.add(email_id)
                                        continue
                            
                            # Save PDF
                            with open(pdf_path, 'wb') as f:
                                f.write(pdf_data)
                            
                            yield {'type': 'info', 'message': f'⬇️ Downloaded: {filename}'}
                            
                            # Add to processing queue
                            downloaded_pdfs.append({
                                'pdf_path': pdf_path,
                                'filename': filename,
                                'date': email_date,
                                'email_id': email_id
                            })
                            
                            processed_in_session.add(email_id)
                            
                            # Move email to visa/downloaded label if not already there
                            if folder != '"Visa/downloaded"':
                                mail.store(num, '+X-GM-LABELS', '"Visa/downloaded"')
                
                if not pdf_found:
                    yield {'type': 'warning', 'message': f'⚠️ No PDF found in email {idx}'}
                    
            except Exception as e:
                yield {'type': 'error', 'message': f'❌ Error processing email {idx}: {str(e)}'}
        
        mail.close()
    
    mail.logout()
    
    # Phase 2: Parallel processing of downloaded PDFs
    if downloaded_pdfs:
        yield {'type': 'info', 'message': f'⚡ Phase 2: Processing {len(downloaded_pdfs)} PDFs in parallel...'}
        
        # Process PDFs in parallel using ThreadPoolExecutor
        max_workers = min(8, len(downloaded_pdfs))  # Use up to 8 threads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all PDF processing tasks
            future_to_pdf = {
                executor.submit(process_pdf_file, pdf_info): pdf_info 
                for pdf_info in downloaded_pdfs
            }
            
            completed = 0
            for future in as_completed(future_to_pdf):
                pdf_info = future_to_pdf[future]
                completed += 1
                
                try:
                    result = future.result()
                    
                    if result['success']:
                        total_processed += 1
                        yield {
                            'type': 'success',
                            'message': f'✓ [{completed}/{len(downloaded_pdfs)}] Processed: {pdf_info["filename"]} (Visa: {result["data"].get("Visa No", "N/A")})',
                            'data': result,
                            'record': {
                                'visa_no': result['data'].get('Visa No', ''),
                                'name': result['data'].get('Name', ''),
                                'passport_no': result['data'].get('Passport No', ''),
                                'employer': result['data'].get('Employer name', ''),
                                'valid_from': result['data'].get('Valid from', ''),
                                'valid_until': result['data'].get('Valid until', ''),
                                'pdf_path': result['pdf_path'],
                                'excel_path': result['excel_path'],
                                'date': pdf_info['date']
                            }
                        }
                    else:
                        yield {
                            'type': 'warning',
                            'message': f'⚠️ [{completed}/{len(downloaded_pdfs)}] Skipped (duplicate): {pdf_info["filename"]}'
                        }
                    
                    # Update progress
                    yield {'type': 'progress', 'current': completed, 'total': len(downloaded_pdfs), 'folder': 'Processing'}
                    
                except Exception as e:
                    yield {'type': 'error', 'message': f'❌ Error processing {pdf_info["filename"]}: {str(e)}'}
    
    yield {'type': 'summary', 'total_processed': total_processed}

def process_pdf_file(pdf_info):
    """Process a single PDF file (for parallel execution)"""
    pdf_path = pdf_info['pdf_path']
    filename = pdf_info['filename']
    date = pdf_info['date']
    
    try:
        # Extract data from PDF
        visa_data = process_pdf(pdf_path)
        
        # Check if record with same passport exists in same date folder
        passport_no = visa_data.get('Passport No', '')
        
        if passport_no and db.record_exists_in_date(passport_no, date):
            return {
                'success': False,
                'duplicate': True,
                'reason': 'passport_exists_in_date',
                'filename': filename,
                'date': date,
                'data': visa_data
            }
        
        # Save to Excel
        excel_path = pdf_path.replace('.pdf', '.xlsx')
        save_to_excel(visa_data, excel_path)
        
        # Insert into database
        record_id = db.insert_record(visa_data, filename, date)
        
        # Announce new visa
        name = visa_data.get('Name', 'Unknown')
        visa_no = visa_data.get('Visa No', '')
        announcer.announce_visa(name, visa_no)
        
        return {
            'success': True,
            'duplicate': False,
            'record_id': record_id,
            'filename': filename,
            'date': date,
            'pdf_path': pdf_path,
            'excel_path': excel_path,
            'data': visa_data
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'filename': filename,
            'date': date,
            'data': {}
        }

def save_and_process_pdf(pdf_data, filename, date):
    """Legacy function - kept for compatibility"""
    date_folder = os.path.join(config.save_path, date)
    os.makedirs(date_folder, exist_ok=True)
    
    pdf_path = os.path.join(date_folder, filename)
    
    # Check if file already exists
    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            existing_data = f.read()
        if existing_data == pdf_data:
            return {
                'success': False,
                'duplicate': True,
                'reason': 'file_exists',
                'filename': filename,
                'date': date,
                'data': {}
            }
    
    # Save PDF file
    with open(pdf_path, 'wb') as f:
        f.write(pdf_data)
    
    # Process using the parallel function
    return process_pdf_file({
        'pdf_path': pdf_path,
        'filename': filename,
        'date': date
    })

def save_to_excel(data, path):
    import pandas as pd
    df = pd.DataFrame([data])
    df.to_excel(path, index=False)

def get_statistics():
    db_stats = db.get_statistics()
    
    stats = {
        'total_processed': db_stats.get('total', 0),
        'by_date': db_stats.get('by_date', {}),
        'by_employer': db_stats.get('by_employer', {}),
        'by_nationality': db_stats.get('by_nationality', {})
    }
    
    return stats

def find_free_port(start_port=5000, max_attempts=10):
    import socket
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', port))
            sock.close()
            return port
        except OSError:
            continue
    return start_port

if __name__ == '__main__':
    port = find_free_port()
    print(f"\n{'='*50}")
    print(f"Dashboard available at: http://127.0.0.1:{port}")
    print(f"Open in browser: http://127.0.0.1:{port}")
    print(f"{'='*50}\n")
    
    # Reload config to ensure all attributes are loaded
    config.load()
    
    # Auto-start monitoring
    print("🔔 Starting auto-monitor...")
    auto_monitor_active = True
    auto_monitor_thread = threading.Thread(target=auto_monitor_worker, daemon=True)
    auto_monitor_thread.start()
    print("✓ Auto-monitor started (checking every 5 minutes)")
    
    try:
        app.run(debug=False, host='127.0.0.1', port=port, threaded=True, use_reloader=False)
    finally:
        # Cleanup
        auto_monitor_active = False
        announcer.shutdown()
        print("\n👋 Dashboard stopped")
