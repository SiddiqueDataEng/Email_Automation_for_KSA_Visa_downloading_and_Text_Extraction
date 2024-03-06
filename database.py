import sqlite3
import os
from datetime import datetime

class VisaDatabase:
    def __init__(self, db_path='visa_records.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visa_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                visa_no TEXT,
                application_no TEXT,
                valid_from TEXT,
                valid_until TEXT,
                duration_of_stay TEXT,
                place_of_issue TEXT,
                visa_type TEXT,
                name TEXT,
                nationality TEXT,
                passport_no TEXT,
                ref_no TEXT,
                ref_date TEXT,
                occupation TEXT,
                employer_name TEXT,
                visa_fees TEXT,
                pdf_filename TEXT,
                pdf_path TEXT,
                processed_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add pdf_path column if it doesn't exist (migration)
        try:
            cursor.execute('ALTER TABLE visa_records ADD COLUMN pdf_path TEXT')
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        # Create indexes for faster searching
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_visa_no ON visa_records(visa_no)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_passport_no ON visa_records(passport_no)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_employer ON visa_records(employer_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_valid_from ON visa_records(valid_from)')
        
        conn.commit()
        conn.close()
    
    def insert_record(self, data, pdf_filename, processed_date, pdf_path=''):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO visa_records (
                visa_no, application_no, valid_from, valid_until, duration_of_stay,
                place_of_issue, visa_type, name, nationality, passport_no,
                ref_no, ref_date, occupation, employer_name, visa_fees,
                pdf_filename, pdf_path, processed_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('Visa No', ''),
            data.get('Application No', ''),
            data.get('Valid from', ''),
            data.get('Valid until', ''),
            data.get('Duration of Stay', ''),
            data.get('Place of issue', ''),
            data.get('Visa Type', ''),
            data.get('Name', ''),
            data.get('Nationality', ''),
            data.get('Passport No', ''),
            data.get('Ref. No', ''),
            data.get('Ref. Date', ''),
            data.get('Occupation', ''),
            data.get('Employer name', ''),
            data.get('Visa Fees', ''),
            pdf_filename,
            pdf_path,
            processed_date
        ))
        
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id
    
    def get_all_records(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM visa_records ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        records = [dict(row) for row in rows]
        conn.close()
        return records
    
    def get_records_by_date(self, date):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM visa_records WHERE processed_date = ? ORDER BY created_at DESC', (date,))
        rows = cursor.fetchall()
        
        records = [dict(row) for row in rows]
        conn.close()
        return records
    
    def get_records_by_employer(self, employer):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM visa_records WHERE employer_name = ? ORDER BY created_at DESC', (employer,))
        rows = cursor.fetchall()
        
        records = [dict(row) for row in rows]
        conn.close()
        return records
    
    def search_records(self, query):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_pattern = f'%{query}%'
        cursor.execute('''
            SELECT * FROM visa_records 
            WHERE visa_no LIKE ? OR name LIKE ? OR passport_no LIKE ? 
            OR employer_name LIKE ? OR nationality LIKE ?
            ORDER BY created_at DESC
        ''', (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        records = [dict(row) for row in rows]
        conn.close()
        return records
    
    def get_statistics(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total records
        cursor.execute('SELECT COUNT(*) FROM visa_records')
        stats['total'] = cursor.fetchone()[0]
        
        # By date
        cursor.execute('SELECT processed_date, COUNT(*) as count FROM visa_records GROUP BY processed_date ORDER BY processed_date DESC')
        stats['by_date'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By employer
        cursor.execute('SELECT employer_name, COUNT(*) as count FROM visa_records GROUP BY employer_name ORDER BY count DESC LIMIT 10')
        stats['by_employer'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        # By nationality
        cursor.execute('SELECT nationality, COUNT(*) as count FROM visa_records GROUP BY nationality ORDER BY count DESC')
        stats['by_nationality'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return stats
    
    def record_exists(self, visa_no, passport_no):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM visa_records WHERE visa_no = ? AND passport_no = ?', (visa_no, passport_no))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def record_exists_in_date(self, passport_no, date):
        """Check if a record with the same passport exists in the same date"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM visa_records WHERE passport_no = ? AND processed_date = ?', (passport_no, date))
        exists = cursor.fetchone() is not None
        
        conn.close()
        return exists
    
    def update_record_by_passport(self, passport_no, date, data, pdf_filename, pdf_path=''):
        """Update existing record with new extracted data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE visa_records SET
                visa_no = ?,
                application_no = ?,
                valid_from = ?,
                valid_until = ?,
                duration_of_stay = ?,
                place_of_issue = ?,
                visa_type = ?,
                name = ?,
                nationality = ?,
                ref_no = ?,
                ref_date = ?,
                occupation = ?,
                employer_name = ?,
                visa_fees = ?,
                pdf_filename = ?,
                pdf_path = ?
            WHERE passport_no = ? AND processed_date = ?
        ''', (
            data.get('Visa No', ''),
            data.get('Application No', ''),
            data.get('Valid from', ''),
            data.get('Valid until', ''),
            data.get('Duration of Stay', ''),
            data.get('Place of issue', ''),
            data.get('Visa Type', ''),
            data.get('Name', ''),
            data.get('Nationality', ''),
            data.get('Ref. No', ''),
            data.get('Ref. Date', ''),
            data.get('Occupation', ''),
            data.get('Employer name', ''),
            data.get('Visa Fees', ''),
            pdf_filename,
            pdf_path,
            passport_no,
            date
        ))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
