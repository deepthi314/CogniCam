from fastapi import APIRouter, HTTPException
from models.schemas import ReportRequest
from services.cam_generator import generate_cam_report
import base64
import os

router = APIRouter()

@router.post("/generate-report")
async def generate_cam_report_endpoint(request: ReportRequest):
    """
    Generate Credit Appraisal Memorandum (CAM) Word document.
    Returns Base64 encoded JSON to avoid CORS/file protocol issues.
    """
    print("📄 Starting CAM report generation...")
    
    try:
        # Build report data from request
        report_data = {
            "company_name": request.company_name,
            "financial_data": request.financial_data,
            "scores": request.scores,
            "rationales": request.scores.get("rationales", {}),
            "recommendation": request.recommendation,
            "mca_data": request.mca_data,
            "litigation_cases": request.litigation_cases,
            "news_articles": request.news_articles,
            "gstr_flags": request.gstr_flags,
            "shap_explanation": request.shap_explanation,
            "field_note": request.field_note
        }
        
        print(f"📊 Report data: {request.company_name} - {request.recommendation.get('decision', 'UNKNOWN')}")
        
        # Generate CAM report
        doc_bytes = generate_cam_report(report_data)
        
        # Encode as Base64 for safe transit
        base64_content = base64.b64encode(doc_bytes).decode('utf-8')
        
        # Create safe filename
        safe_company_name = "".join(c for c in request.company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"CAM_{safe_company_name}.docx"
        
        print(f"✅ CAM report generated & encoded: {len(base64_content)} chars")
        
        return {
            "status": "success",
            "filename": filename,
            "content": base64_content,
            "media_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
        
    except Exception as e:
        print(f"❌ Report generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
    
    finally:
        # Cleanup temporary file (this will be handled by FastAPI after response)
        pass
