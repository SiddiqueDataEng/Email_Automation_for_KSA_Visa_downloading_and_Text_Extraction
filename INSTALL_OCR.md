# Installing OCR Support for Enhanced Text Extraction

## Why OCR?
OCR (Optical Character Recognition) significantly improves text extraction accuracy from PDF files, especially for:
- Scanned documents
- PDFs with embedded images
- Documents with complex layouts
- Mixed language content (English + Arabic)

## Installation Steps

### 1. Install Python Libraries
```bash
pip install pytesseract pdf2image Pillow opencv-python
```

### 2. Install Tesseract OCR Engine

#### Windows:
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (tesseract-ocr-w64-setup-v5.x.x.exe)
3. During installation, make sure to select:
   - English language data
   - Arabic language data (for better extraction)
4. Add Tesseract to PATH or note the installation path (usually `C:\Program Files\Tesseract-OCR`)

If Tesseract is not in PATH, add this to your code:
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-ara
sudo apt-get install poppler-utils  # For pdf2image
```

#### macOS:
```bash
brew install tesseract tesseract-lang
brew install poppler  # For pdf2image
```

### 3. Verify Installation
```bash
tesseract --version
```

You should see output like:
```
tesseract 5.x.x
```

### 4. Test OCR in Python
```python
import pytesseract
from pdf2image import convert_from_path

# Test Tesseract
print(pytesseract.get_tesseract_version())

# Test PDF conversion
images = convert_from_path('test.pdf', dpi=300)
print(f"Converted {len(images)} pages")
```

## Features with OCR Enabled

✅ **Dual Strategy Extraction**
- First tries fast text extraction
- Falls back to OCR if text extraction fails or is incomplete

✅ **Image Preprocessing**
- Grayscale conversion
- Noise reduction
- Threshold optimization
- Better accuracy for low-quality scans

✅ **Multi-Language Support**
- English text extraction
- Arabic text detection and removal
- Mixed content handling

✅ **Intelligent Field Detection**
- Multiple pattern matching per field
- Fallback patterns for variations
- Smart data merging from multiple sources

✅ **Data Validation**
- Field-specific cleaning rules
- Format normalization
- Duplicate detection

## Performance Impact

- **Without OCR**: ~0.1-0.5 seconds per PDF
- **With OCR**: ~2-5 seconds per PDF (only when needed)
- **Parallel Processing**: Up to 8 PDFs simultaneously

The system automatically uses OCR only when regular text extraction fails, maintaining optimal performance.

## Troubleshooting

### "Tesseract not found"
- Ensure Tesseract is installed
- Add to PATH or set `tesseract_cmd` in code

### "pdf2image error"
- Install poppler-utils (Linux) or download poppler binaries (Windows)
- Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases/

### "Low accuracy"
- Increase DPI (currently 300, can go up to 600)
- Ensure PDF quality is good
- Check if Arabic language data is installed

## Without OCR

The system will still work without OCR libraries, using the basic PDF text extraction. You'll see:
```
⚠ Using basic PDF processor (install OCR libraries for better accuracy)
```

To enable OCR, follow the installation steps above and restart the application.
