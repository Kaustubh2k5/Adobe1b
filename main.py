import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
import fitz  # PyMuPDF
import os
import json
import re
from PIL import Image
import pytesseract
import io

# Set path to Tesseract if not in system PATH
# For Windows:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_title_from_image(img):
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    lines = {}
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if not text:
            continue
        height = data['height'][i]
        line_no = data['line_num'][i]
        if line_no not in lines:
            lines[line_no] = {'words': [], 'height': height}
        lines[line_no]['words'].append(text)

    top_lines = sorted(lines.values(), key=lambda x: -x['height'])[:3]
    title = " ".join(" ".join(line['words']) for line in top_lines).strip()
    return title

def extract_headings(pdf_path):
    doc = fitz.open(pdf_path)
    elements = []
    title_text = ""

    first_page = doc[0]
    blocks = first_page.get_text("dict")["blocks"]
    title_lines = []

    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            line_text = ""
            sizes = []
            for span in line["spans"]:
                text = span["text"].strip()
                if text:
                    sizes.append(span["size"])
                    line_text += text + " "
            if line_text.strip():
                title_lines.append({"text": line_text.strip(), "size": max(sizes)})

    # Fallback to OCR if too few text lines found
    if not title_lines or len(title_lines) <= 2:
        print("📷 First page looks like an image — using OCR to extract title...")
        pix = first_page.get_pixmap(dpi=300)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        title_text = extract_title_from_image(img)
    else:
        # Use largest font lines as title
        max_size = max(line["size"] for line in title_lines)
        filtered = [
            line["text"] for line in title_lines
            if abs(line["size"] - max_size) < 1.0
            and not re.fullmatch(r"(grade\s*\d+|class\s*\d+|\d+)", line["text"], re.IGNORECASE)
        ]
        title_text = " ".join(filtered).strip()

    # Extract all elements for headings
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text = ""
                font_sizes = []
                for span in line["spans"]:
                    text += span["text"].strip() + " "
                    font_sizes.append(span["size"])
                if text.strip():
                    elements.append({
                        "text": text.strip(),
                        "size": max(font_sizes),
                        "page": page_num
                    })

    return elements, title_text

def classify_headings(elements, title_text):
    outline = []

    pattern_h1 = re.compile(r"^\d+\s")
    pattern_h2 = re.compile(r"^\d+\.\d+\s")
    pattern_h3 = re.compile(r"^\d+\.\d+\.\d+\s")

    if title_text:
        outline.append({
            "level": "H1",
            "text": title_text,
            "page": 1
        })

    for element in elements:
        text = element["text"]
        if "table of contents" in text.lower():
            continue
        if text == title_text:
            continue
        if text.lower() == "introduction":
            outline.append({
                "level": "H1",
                "text": text,
                "page": element["page"]
            })
            continue

        level = None
        if pattern_h3.match(text):
            level = "H3"
        elif pattern_h2.match(text):
            level = "H2"
        elif pattern_h1.match(text):
            level = "H1"

        if level:
            outline.append({
                "level": level,
                "text": text,
                "page": element["page"]
            })

    return {
        "title": title_text,
        "outline": outline
    }

def process_pdf(input_path, output_path):
    elements, title_text = extract_headings(input_path)
    structured = classify_headings(elements, title_text)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structured, f, indent=2, ensure_ascii=False)
    print(f"✅ Processed: {os.path.basename(input_path)}")

if __name__ == "__main__":
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.lower().endswith(".pdf"):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, file.replace(".pdf", ".json"))
            process_pdf(input_path, output_path)
