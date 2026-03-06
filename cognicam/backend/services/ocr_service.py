import io
import PyPDF2
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
from typing import Optional

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from PDF files using PyPDF2 first, then OCR if needed.
    
    Args:
        file_bytes: PDF file content as bytes
        
    Returns:
        Extracted text as string
    """
    try:
        print("📄 Starting PDF text extraction...")
        
        # First try PyPDF2 for text-based PDFs
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            page_count = len(pdf_reader.pages)
            print(f"📖 PDF has {page_count} pages, attempting text extraction...")
            
            for i, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {i+1} ---\n{page_text}"
            
            # If we got substantial text, return it
            if len(text.strip()) > 100:
                print(f"✅ Successfully extracted {len(text)} characters via PyPDF2")
                return text
            else:
                print("⚠️ PyPDF2 extracted minimal text, falling back to OCR...")
                
        except Exception as e:
            print(f"⚠️ PyPDF2 failed: {str(e)}, falling back to OCR...")
        
        # Fallback to OCR for scanned PDFs
        print("🔍 Converting PDF to images for OCR...")
        images = convert_from_bytes(file_bytes, dpi=200)
        print(f"🖼️ Converted {len(images)} pages to images")
        
        full_text = ""
        for i, image in enumerate(images):
            print(f"📷 Processing page {i+1} with OCR...")
            page_text = pytesseract.image_to_string(image)
            full_text += f"\n--- Page {i+1} (OCR) ---\n{page_text}"
        
        print(f"✅ OCR extraction complete: {len(full_text)} characters")
        return full_text
        
    except Exception as e:
        print(f"❌ PDF extraction failed: {str(e)}")
        return f"Error extracting text from PDF: {str(e)}"

def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Extract text from image files using OCR.
    
    Args:
        file_bytes: Image file content as bytes
        
    Returns:
        Extracted text as string
    """
    try:
        print("🖼️ Starting image OCR...")
        
        # Open image from bytes
        image = Image.open(io.BytesIO(file_bytes))
        print(f"📷 Image loaded: {image.format} {image.size}")
        
        # Extract text using Tesseract
        text = pytesseract.image_to_string(image)
        char_count = len(text.strip())
        
        print(f"✅ OCR extraction complete: {char_count} characters")
        
        if char_count == 0:
            print("⚠️ No text found in image")
            return "No text could be extracted from the image."
        
        return text
        
    except Exception as e:
        print(f"❌ Image OCR failed: {str(e)}")
        return f"Error extracting text from image: {str(e)}"

def detect_document_type(text: str) -> str:
    """
    Detect document type from text content using keyword matching.
    """
    text_lower = text.lower()
    
    # 1. Annual Report / Financial Statements
    if any(k in text_lower for k in ["annual report", "balance sheet", "profit & loss", "financial year", "directors' report"]):
        return "ANNUAL_REPORT"
    
    # 2. GST Return
    if any(k in text_lower for k in ["gstr-3b", "gstr-1", "gstr-2a", "goods and services tax", "gst return"]):
        return "GST_RETURN"
    
    # 3. Bank Statement
    if any(k in text_lower for k in ["bank statement", "account summary", "transaction history", "closing balance", "ifsc code"]):
        return "BANK_STATEMENT"
    
    # 4. Income Tax Return
    if any(k in text_lower for k in ["income tax", "acknowledgement number", "assessment year", "itr-", "itr-v"]):
        return "IT_RETURN"
    
    # 5. Sanction Letter
    if any(k in text_lower for k in ["sanction letter", "loan agreement", "facility letter", "repayment schedule"]):
        return "SANCTION_LETTER"
    
    return "UNKNOWN"

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from either PDF or image files based on filename.
    
    Args:
        file_bytes: File content as bytes
        filename: Original filename with extension
        
    Returns:
        Extracted text as string
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        text = extract_text_from_pdf(file_bytes)
    elif any(filename_lower.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif']):
        text = extract_text_from_image(file_bytes)
    else:
        return f"Unsupported file type: {filename}. Please use PDF or image files."
    
    return text
