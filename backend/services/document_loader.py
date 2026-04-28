import fitz # PyMuPDF
import docx
import os

def load_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext == ".txt":
        return extract_text_from_txt(file_path)
    elif ext in [".py", ".js", ".java", ".cpp", ".c", ".html", ".css", ".go", ".rs", ".php"]:
        return extract_text_from_code(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
        return extract_text_from_image(file_path)
    else:
        # Default to reading as text for unknown files
        return extract_text_from_txt(file_path)

def extract_text_from_pdf(file_path):
    try:
        import pymupdf4llm
        import re
        import fitz
        
        # 1. Extract markdown text
        text = pymupdf4llm.to_markdown(file_path)
        
        # 2. Advanced: Extract images and formulas as visual blocks
        # We create a media directory for this specific document
        doc_id = os.path.splitext(os.path.basename(file_path))[0]
        media_dir = os.path.join("data", "media", doc_id)
        os.makedirs(media_dir, exist_ok=True)
        
        pdf = fitz.open(file_path)
        img_refs = []
        
        for pno, page in enumerate(pdf):
            # Find image objects (often used for complex equations in academic PDFs)
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                img_name = f"eq_p{pno}_{img_index}.{image_ext}"
                img_path = os.path.join(media_dir, img_name)
                
                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                
                # Insert the image reference into the markdown at the end of the page content
                img_refs.append(f"![Equation]({img_path})")

        # --- SCIENTIFIC ARTIFACT CLEANING ---
        text = re.sub(r'(\s*/\s*){2,}', ' ', text)
        text = re.sub(r'/\s+/\s+/', ' ', text)
        text = re.sub(r'<br\s*/?>', ' ', text, flags=re.IGNORECASE)
        
        # Append visual references if found
        if img_refs:
            text += "\n\n### 📐 Captured Equations & Graphics\n" + "\n".join(img_refs[:10]) # Limit to 10 key visuals
            
        return text.strip()
    except Exception as e:
        print(f"Extraction error: {e}")
        return ""
        print(f"pymupdf4llm error: {e}, falling back to fitz...")
        import fitz
        text = ""
        pdf = fitz.open(file_path)
        for page in pdf:
            text += page.get_text()
        return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return "\n".join(text)

def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_text_from_code(file_path):
    ext = os.path.splitext(file_path)[1]
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()
        return f"### SOURCE CODE FILE: {ext.upper()}\n\n```python\n{code}\n```"

def extract_text_from_image(file_path):
    """
    Extracts text from images using high-fidelity AI vision (OpenAI/Gemini).
    """
    from backend.utils.llm_client import get_chat_response
    import base64
    
    def encode_image(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    try:
        base64_image = encode_image(file_path)
        # We can pass the image to Gemini or OpenAI via our client if updated, 
        # but for now let's use a simpler vision prompt if supported.
        # Since our current get_chat_response doesn't handle images yet, 
        # let's add a placeholder or simple OCR if available.
        return f"[IMAGE UPLOADED: {os.path.basename(file_path)}] - Vision processing requires active API key with vision capabilities."
    except Exception as e:
        return f"[Image Read Error: {str(e)}]"
