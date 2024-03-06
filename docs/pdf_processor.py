import PyPDF2
import re

def process_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    
    return extract_visa_data(text)

def extract_visa_data(text):
    # Clean text first
    text = text.replace('\n', ' ')
    
    data = {
        'Visa No': extract_field(text, r'Visa\s*No\.?\s*(\d+)'),
        'Application No': extract_field(text, r'Application\s*No\.?\s*(\d+)'),
        'Valid from': extract_field(text, r'Valid\s*from\s*(\d{2}/\d{2}/\d{4})'),
        'Valid until': extract_field(text, r'Valid\s*until\s*(\d{2}/\d{2}/\d{4})'),
        'Duration of Stay': extract_field(text, r'Duration\s*of\s*Stay\s*(\d+\s*Days?|Days?\s*\d+)'),
        'Place of issue': extract_field(text, r'Place\s*of\s*issue\s*([^\u0600-\u06FF]+?)(?=\s*Visa\s*Type|Saudi Mission)', multiline=True),
        'Visa Type': extract_field(text, r'Visa\s*Type\s*([^\u0600-\u06FF]+?)(?=\s*Name|Work|Business|Visit)', multiline=True),
        'Name': extract_field(text, r'Name\s*([A-Z][A-Z\s]+?)(?=\s*Nationality|\s*[\u0600-\u06FF])', multiline=True),
        'Nationality': extract_field(text, r'Nationality\s*([A-Za-z\s]+?)(?=\s*Passport|\s*[\u0600-\u06FF])', multiline=True),
        'Passport No': extract_field(text, r'Passport\s*No\.?\s*([A-Z0-9]+)'),
        'Ref. No': extract_field(text, r'Ref\.?\s*No\.?\s*(\d+)'),
        'Ref. Date': extract_field(text, r'Ref\.?\s*Date\s*(\d{2}/\d{2}/\d{4})'),
        'Occupation': extract_field(text, r'Occupation\s*([^\u0600-\u06FF]+?)(?=\s*Employer|Offices\s*and\s*facilities)', multiline=True),
        'Employer name': extract_field(text, r'(?:Employer\s*name|name\s*Employer)\s*([^\u0600-\u06FF]+?)(?=\s*Visa\s*Fees|[\u0600-\u06FF])', multiline=True),
        'Visa Fees': extract_field(text, r'Visa\s*Fees\s*([^\u0600-\u06FF\n]+)', multiline=True)
    }
    
    # Clean up extracted data
    for key in data:
        if data[key]:
            data[key] = data[key].strip()
            # Remove Arabic text
            data[key] = re.sub(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+', '', data[key]).strip()
            # Remove extra whitespace
            data[key] = re.sub(r'\s+', ' ', data[key]).strip()
            # Remove common artifacts
            data[key] = re.sub(r'[‐\-]+', '-', data[key])
            
            # Clean up specific fields
            if key == 'Duration of Stay':
                # Normalize to "X Days" format
                match = re.search(r'(\d+)', data[key])
                if match:
                    data[key] = f"{match.group(1)} Days"
            
            if key == 'Visa Type':
                # Clean visa type
                data[key] = re.sub(r'(Work|Business|Visit|Tourist).*', r'\1', data[key], flags=re.IGNORECASE)
            
            if key == 'Name':
                # Clean name - keep only uppercase letters and spaces
                data[key] = re.sub(r'[^A-Z\s]', '', data[key].upper()).strip()
            
            if key == 'Nationality':
                # Clean nationality
                data[key] = re.sub(r'[^A-Za-z\s]', '', data[key]).strip().title()
    
    return data

def extract_field(text, pattern, multiline=False):
    flags = re.IGNORECASE | re.DOTALL if multiline else re.IGNORECASE
    match = re.search(pattern, text, flags)
    return match.group(1).strip() if match else ''
