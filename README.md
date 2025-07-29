# 🧾 PDF Outline Extractor

This project extracts the *document title* and *heading hierarchy (H1, H2, H3)* from PDF files using a combination of font-size analysis and OCR (Tesseract), and outputs the result as a structured JSON file.

## 📦 Features

- Automatically detects the title from the first page.
- Classifies headings using font size and numbering (e.g., 1, 1.1, 1.1.1).
- Uses OCR if the first page is image-based.
- Outputs a JSON file with structured outline (title, headings, and page numbers).

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.6+
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) installed:
  > Default path: C:\Program Files\Tesseract-OCR\tesseract.exe
  >

### 📥 Installation

Run these commands to set up:

```bash
pip install pytesseract
pip install pymupdf
pip install pillow

echo pytesseract > requirements.txt
echo pymupdf >> requirements.txt
echo pillow >> requirements.txt

pip install -r requirements.txt

mkdir input
mkdir output
```
