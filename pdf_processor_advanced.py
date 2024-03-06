import PyPDF2
import re
import os
from typing import Dict, Optional

# Try to import OCR libraries
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    import cv2
    import numpy as np
    
    # Configure Tesseract path for Windows
    import os
    if os.name == 'nt':  # Windows
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        ]
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"[OK] Tesseract configured: {path}")
                break
    
    # Verify Tesseract is accessible
    try:
        version = pytesseract.get_tesseract_version()
        OCR_AVAILABLE = True
        print(f"[OK] OCR enabled with Tesseract: {version}")
    except Exception as e:
        OCR_AVAILABLE = False
        Image = None
        print(f"[WARN] Tesseract not accessible: {e}")
        print("  Make sure Tesseract is installed at: C:\\Program Files\\Tesseract-OCR\\")
        
except ImportError as e:
    OCR_AVAILABLE = False
    Image = None  # Define placeholder
    print(f"[WARN] OCR libraries not available: {e}")
except Exception as e:
    OCR_AVAILABLE = False
    Image = None
    print(f"[WARN] OCR configuration error: {e}")

class AdvancedPDFProcessor:
    """Advanced PDF processor with OCR fallback and intelligent extraction"""
    
    def __init__(self):
        self.ocr_available = OCR_AVAILABLE
        # Field patterns based on actual PDF text structure
        self.patterns = {
            'Visa No': [
                r'(?:رقم\s*التأشيرة|Visa\s*No\.?)\s+(\d{10})',  # After label
                r'(\d{10})\s+Visa\s*No',  # Before label (Arabic layout)
            ],
            'Application No': [
                r'Application\s*No\.?\s+([A-Z]\d{9,10})',
                r'([A-Z]\d{9,10})\s+Application',
                r'\b([A-Z]\d{9,10})\b',  # Standalone at bottom of PDF
            ],
            'Valid from': [
                r'(?:صالحة\s*اعتبارا\s*من|Valid\s*From)\s+(\d{2}/\d{2}/\d{4})',
                r'(\d{2}/\d{2}/\d{4})\s+Valid\s*From',
            ],
            'Valid until': [
                r'(?:صالحة\s*لغاية|Valid\s*Until)\s+(\d{2}/\d{2}/\d{4})',
                r'(\d{2}/\d{2}/\d{4})\s+Valid\s*Until',
            ],
            'Duration of Stay': [
                r'(?:مدة\s*الإقامة|Duration\s*of\s*Stay)\s+Days?(\d+)',
                r'Days(\d+)',
            ],
            'Visa Type': [
                r'(?:نوع\s*التأشيرة|Visa\s*Type)\s+([A-Za-z]+)',
                r'(Work|Business|Visit|Tourist|Umrah|Hajj)\s*[\u2010-\u2015\-]',  # Flexible dash
            ],
            'Name': [
                r'([A-Z][A-Z\s]+?)\s+(?:Name|Nationality)',  # Stop at Name or Nationality label
                r'Name\s+([A-Z][A-Z\s]+?)\s+(?:Pakistan|India|Bangladesh)',
            ],
            'Nationality': [
                r'([A-Z][a-z]+)[\s\xa0]+[\u2010-\u2015\-][\s\xa0]+[\u0600-\u06FF\uFE00-\uFEFF\s\xa0]+Nationality',  # Include presentation forms
                r'([A-Z][a-z]+)[\s\xa0\u2010-\u2015\-\u0600-\u06FF\uFE00-\uFEFF]+Nationality',  # Simpler
                r'Nationality[\s\xa0]+([A-Za-z]+)[\s\xa0]+[\u2010-\u2015\-]',
            ],
            'Passport No': [
                r'(?:رقم\s*الجواز|Passport\s*No\.?)\s+([A-Z]{2}\d{7,8})',
                r'([A-Z]{2}\d{7,8})\s+Passport',
            ],
            'Ref. No': [
                r'(?:رقم\s*المستند|Ref\.\s*No\.?)\s+(\d{10})',
                r'(\d{10})\s+Ref\.\s*No',
            ],
            'Ref. Date': [
                r'(?:التاريخ|Ref\.\s*Date)\s+(\d{2}/\d{2}/\d{4})',
                r'(\d{2}/\d{2}/\d{4})\s+Ref\.\s*Date',
            ],
            'Occupation': [
                # Patterns disabled - using special handling below to capture full text with Arabic
            ],
            'Employer name': [
                r'([\u0600-\u06FF\uFE00-\uFEFF\s\xa0]+)[\s\xa0]+Employer[\s\xa0]*name',  # Include presentation forms
                r'Employer[\s\xa0]*name[\s\xa0]+([A-Za-z\s]+)',
                r'[\u0600-\u06FF\uFE00-\uFEFF\s\xa0]+([\u0600-\u06FF\uFE00-\uFEFF\s\xa0]+)[\s\xa0]+Employer',
            ],
            'Place of issue': [
                r'(?:مكان\s*الإصدار|Place\s*of\s*issue)[^\n]*?Saudi\s+Mission\s+In\s+([A-Za-z]+)',
                r'Saudi\s+Mission\s+In\s+([A-Za-z]+)',
            ],
        }
    
    def process_pdf(self, pdf_path: str) -> Dict[str, str]:
        """Main processing function with fallback strategies"""
        # Strategy 1: Try text extraction first
        text = self._extract_text_pypdf(pdf_path)
        data = self._extract_fields(text)
        
        # Strategy 2: If critical fields missing, try OCR
        if self._is_extraction_incomplete(data) and self.ocr_available:
            print(f"Text extraction incomplete, trying OCR for {os.path.basename(pdf_path)}")
            ocr_text = self._extract_text_ocr(pdf_path)
            if ocr_text:
                ocr_data = self._extract_fields(ocr_text)
                # Merge data, preferring OCR for missing fields
                data = self._merge_data(data, ocr_data)
        
        # Strategy 3: Clean and validate data
        data = self._clean_and_validate(data)
        
        return data
    
    def _extract_text_pypdf(self, pdf_path: str) -> str:
        """Extract text using PyPDF2"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text() + '\n'
                return text
        except Exception as e:
            print(f"PyPDF2 extraction error: {e}")
            return ''
    
    def _extract_text_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR (Tesseract)"""
        if not self.ocr_available:
            return ''
        
        try:
            # Configure poppler path for Windows
            poppler_path = None
            if os.name == 'nt':  # Windows
                # Check common locations
                possible_paths = [
                    os.path.join(os.getcwd(), 'Release-25.12.0-0', 'poppler-25.12.0', 'Library', 'bin'),
                    r'C:\Program Files\poppler\bin',
                    r'C:\Program Files (x86)\poppler\bin',
                ]
                for path in possible_paths:
                    if os.path.exists(os.path.join(path, 'pdftoppm.exe')):
                        poppler_path = path
                        break
            
            # Convert PDF to images
            if poppler_path:
                images = convert_from_path(pdf_path, dpi=300, poppler_path=poppler_path)
            else:
                images = convert_from_path(pdf_path, dpi=300)
            
            full_text = ''
            for i, image in enumerate(images):
                # Preprocess image for better OCR
                processed_image = self._preprocess_image(image)
                
                # Perform OCR with English and Arabic
                text = pytesseract.image_to_string(processed_image, lang='eng+ara')
                full_text += text + '\n'
            
            return full_text
        except Exception as e:
            error_msg = str(e)
            if 'poppler' in error_msg.lower() or 'pdftoppm' in error_msg.lower():
                print(f"[WARN] Poppler error: {e}")
                print(f"   Poppler should be in: Release-25.12.0-0\\poppler-25.12.0\\Library\\bin")
            else:
                print(f"OCR extraction error: {e}")
            return ''
    
    def _preprocess_image(self, image):
        """Preprocess image for better OCR accuracy"""
        if not self.ocr_available:
            return image
        
        try:
            # Convert PIL Image to OpenCV format
            img_array = np.array(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(thresh)
            
            # Convert back to PIL Image
            from PIL import Image as PILImage
            return PILImage.fromarray(denoised)
        except:
            return image
    
    def _extract_fields(self, text: str) -> Dict[str, str]:
        """Extract fields using multiple pattern matching"""
        data = {}
        
        # Keep original text with line breaks for better matching
        original_text = text
        
        # Create a normalized version (collapse multiple spaces but keep structure)
        normalized_text = re.sub(r'[ \t\xa0]+', ' ', text)  # Collapse spaces/tabs/nbsp but keep newlines
        normalized_text = re.sub(r'\n+', '\n', normalized_text)  # Collapse multiple newlines
        
        for field, patterns in self.patterns.items():
            value = None
            for pattern in patterns:
                # Try on original text first (preserves all spacing)
                match = re.search(pattern, original_text, re.IGNORECASE | re.DOTALL)
                if match:
                    value = match.group(1).strip()
                    break
                
                # If not found, try on normalized text
                if not value:
                    match = re.search(pattern, normalized_text, re.IGNORECASE | re.DOTALL)
                    if match:
                        value = match.group(1).strip()
                        break
            
            data[field] = value if value else ''
        
        # Special handling for fields that are hard to extract with regex
        if not data.get('Nationality'):
            # Nationality is between Name and Passport, look for country name
            nat = self._extract_between_labels(normalized_text, 'Name', 'Passport', r'\b(Pakistan|India|Bangladesh|Philippines|Egypt|Nepal|Sri Lanka|Indonesia)\b')
            data['Nationality'] = nat
        
        if not data.get('Occupation'):
            # Occupation comes BEFORE the "Occupation" label
            # May have newline before it: "\nﺍﻟﻤﻬﻨﺔ Builder ﺑﻨﺎﺀ ‐ Occupation"
            # Capture full text including Arabic
            match = re.search(r'[\n\s]*[\u0600-\u06FF\uFE00-\uFEFF\s\xa0]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?[\s\xa0]+[\u0600-\u06FF\uFE00-\uFEFF\s\xa0]*)\s*[\u2010-\u2015\-]?\s*Occupation', normalized_text, re.IGNORECASE)
            if match:
                occ = match.group(1).strip()
                # Remove common non-occupation words
                if not any(word in occ for word in ['Ref', 'Date', 'Employer', 'Name', 'Visa', 'Fees', 'No', 'Passport']):
                    data['Occupation'] = occ
        
        return data
    
    def _extract_between_labels(self, text: str, start_label: str, end_label: str, value_pattern: str) -> str:
        """Extract value between two labels"""
        try:
            # Find text between labels
            pattern = f'{start_label}.*?{end_label}'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                section = match.group(0)
                # Extract value using pattern
                value_match = re.search(value_pattern, section)
                if value_match:
                    return value_match.group(1).strip()
        except:
            pass
        return ''
    
    def _is_extraction_incomplete(self, data: Dict[str, str]) -> bool:
        """Check if critical fields are missing"""
        critical_fields = ['Visa No', 'Name', 'Passport No', 'Valid from']
        missing = sum(1 for field in critical_fields if not data.get(field))
        return missing >= 2  # If 2 or more critical fields missing
    
    def _merge_data(self, data1: Dict[str, str], data2: Dict[str, str]) -> Dict[str, str]:
        """Merge two data dictionaries, preferring non-empty values"""
        merged = data1.copy()
        for key, value in data2.items():
            if value and not merged.get(key):
                merged[key] = value
        return merged
    
    def _clean_and_validate(self, data: Dict[str, str]) -> Dict[str, str]:
        """Clean and validate extracted data"""
        cleaned = {}
        
        for key, value in data.items():
            if not value:
                cleaned[key] = ''
                continue
            
            # Remove Arabic text and common column titles (but keep for Occupation and Employer)
            if key not in ['Occupation', 'Employer name']:
                value = re.sub(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFE00-\uFEFF]+', '', value)
            value = re.sub(r'(الاسم|الجنسية|رقم\s*الجواز|الرسوم|رقم\s*التأشيرة)', '', value)
            
            # Remove extra whitespace
            value = re.sub(r'\s+', ' ', value).strip()
            
            # Remove common artifacts
            value = re.sub(r'[‐\-—]+', '-', value)
            value = re.sub(r'["""]', '', value)
            
            # Field-specific cleaning
            if key == 'Duration of Stay':
                match = re.search(r'(\d+)', value)
                if match:
                    value = f"{match.group(1)} Days"
            
            elif key == 'Visa Type':
                # Extract main visa type (before Arabic text)
                value = value.split('-')[0].strip() if '-' in value else value
                for vtype in ['Work', 'Business', 'Visit', 'Tourist', 'Umrah', 'Hajj']:
                    if vtype.lower() in value.lower():
                        value = vtype
                        break
            
            elif key == 'Name':
                # Keep only uppercase letters and spaces
                value = re.sub(r'[^A-Z\s]', '', value.upper()).strip()
                # Remove common words that shouldn't be in name
                words = [w for w in value.split() if len(w) > 1 and w not in ['NATIONALITY', 'PASSPORT', 'NO', 'NAME']]
                value = ' '.join(words)
                # Limit to reasonable name length (max 4-5 words)
                words = value.split()
                if len(words) > 5:
                    value = ' '.join(words[:5])
            
            elif key == 'Nationality':
                # Clean nationality - extract first word before dash
                value = value.split('-')[0].strip() if '-' in value else value
                value = value.split('‐')[0].strip() if '‐' in value else value
                value = re.sub(r'[^A-Za-z\s]', '', value).strip().title()
                # Take first word only
                value = value.split()[0] if value.split() else value
            
            elif key == 'Passport No':
                # CRITICAL: Keep only alphanumeric (2 letters + 7-8 digits)
                value = re.sub(r'[^A-Z0-9]', '', value.upper())
                # Validate format: 2 letters followed by 7-8 digits
                match = re.match(r'^([A-Z]{2}\d{7,8})$', value)
                if match:
                    value = match.group(1)
                else:
                    # Try to find pattern within the string
                    match = re.search(r'([A-Z]{2}\d{7,8})', value)
                    value = match.group(1) if match else value
            
            elif key == 'Application No':
                # Keep alphanumeric (1 letter + 9-10 digits)
                value = re.sub(r'[^A-Z0-9]', '', value.upper())
                # Validate format
                match = re.search(r'([A-Z]\d{9,10})', value)
                value = match.group(1) if match else value
            
            elif key in ['Visa No', 'Ref. No']:
                # Keep only digits (10 digits)
                value = re.sub(r'[^\d]', '', value)
                # Take first 10 digits if longer
                if len(value) > 10:
                    value = value[:10]
            
            elif key in ['Valid from', 'Valid until', 'Ref. Date']:
                # Normalize date format to DD/MM/YYYY
                value = re.sub(r'[-]', '/', value)
            
            elif key == 'Occupation':
                # Keep both English and Arabic: "Builder - بناء"
                # Extract English part
                english = re.sub(r'[\u0600-\u06FF\uFE00-\uFEFF\u2010-\u2015\-]', '', value)
                english = re.sub(r'[^A-Za-z\s]', '', english).strip().title()
                
                # Extract Arabic part
                arabic = re.sub(r'[A-Za-z\s\u2010-\u2015\-]', '', value).strip()
                
                # Combine both
                if english and arabic:
                    value = f"{english} - {arabic}"
                elif english:
                    value = english
                else:
                    value = arabic if arabic else ''
            
            elif key == 'Employer name':
                # Employer names are in Arabic in PDFs - keep them
                # Remove label text
                value = re.sub(r'اسم\s*صاحب\s*العمل', '', value)
                value = re.sub(r'Employer.*', '', value, flags=re.IGNORECASE)
                value = re.sub(r'Visa\s*Fees.*', '', value, flags=re.IGNORECASE)
                value = re.sub(r'الرسوم.*', '', value)
                value = value.strip()
                
                # Keep if it has content (Arabic company name)
                if len(value) < 3 or not any(c.isalnum() or ord(c) > 127 for c in value):
                    value = ''
                # Limit length
                if len(value) > 100:
                    value = value[:100] + '...'
            
            elif key == 'Place of issue':
                # Extract city name from "Saudi Mission In Islamabad"
                match = re.search(r'Saudi\s+Mission\s+[Ii]n\s+([A-Za-z]+)', value)
                if match:
                    value = match.group(1)
                else:
                    # Clean up
                    value = re.sub(r'Place\s*of\s*issue', '', value, flags=re.IGNORECASE)
                    value = re.sub(r'place', '', value, flags=re.IGNORECASE)
                    value = re.sub(r'[^A-Za-z\s]', '', value).strip().title()
                    # Take first word
                    value = value.split()[0] if value.split() else value
            
            cleaned[key] = value
        
        return cleaned

# Create global instance
processor = AdvancedPDFProcessor()

def process_pdf(pdf_path: str) -> Dict[str, str]:
    """Main entry point for PDF processing"""
    return processor.process_pdf(pdf_path)
