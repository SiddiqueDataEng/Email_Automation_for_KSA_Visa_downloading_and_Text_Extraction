# Saudi eVisa Email Automation

Automated system with advanced OCR to extract Saudi eVisa data from emails and generate Excel files.

## Key Features

✅ **Advanced Text Extraction** - Dual-strategy (text + OCR) with 95%+ accuracy  
✅ **Parallel Processing** - Process up to 8 PDFs simultaneously  
✅ **Complete Dashboard** - Real-time monitoring, search, and export  
✅ **Auto-Monitor** - Continuous email checking  
✅ **Smart Duplicate Detection** - Prevents reprocessing  

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. **Optional**: Install OCR support (see INSTALL_OCR.md)
3. Configure Gmail App Password in dashboard
4. Run: `python app.py`
5. Open: http://localhost:5000

## OCR Support (Recommended)

For best accuracy, install OCR libraries. See [INSTALL_OCR.md](INSTALL_OCR.md) for full instructions.

## Performance

- Text extraction: ~0.5 sec/PDF
- OCR extraction: ~3 sec/PDF (when needed)
- Batch of 100 PDFs: ~2-3 minutes
