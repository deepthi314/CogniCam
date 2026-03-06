from fastapi import APIRouter
from models.schemas import ExplainRequest
from services.explainability import generate_shap_explanation, format_shap_for_display, compute_model_metrics

router = APIRouter()

@router.post("/explain", response_model=dict)
async def explain_credit_decision(request: ExplainRequest):
    """
    Generate SHAP-based explainability for credit decision.
    """
    print("🔍 Starting SHAP explainability analysis...")
    
    try:
        print(f"📊 Input scores: {request.scores}")
        
        # Generate SHAP explanation
        shap_result = generate_shap_explanation(request.scores)
        
        # Compute performance metrics for the model
        model_metrics = compute_model_metrics(request.scores)
        
        # Format for frontend display
        formatted_result = format_shap_for_display(shap_result)
        
        # Prepare response
        response = {
            "status": "success",
            "shap_values": shap_result["shap_values"],
            "top_positive_factor": shap_result["top_positive_factor"],
            "top_positive_label": shap_result["top_positive_label"],
            "top_positive_value": shap_result["top_positive_value"],
            "top_negative_factor": shap_result["top_negative_factor"],
            "top_negative_label": shap_result["top_negative_label"],
            "top_negative_value": shap_result["top_negative_value"],
            "approval_probability": shap_result["approval_probability"],
            "explanation_text": shap_result["explanation_text"],
            "base_value": shap_result["base_value"],
            "model_metrics": model_metrics,
            "formatted": formatted_result
        }
        
        print(f"✅ SHAP analysis complete: {shap_result['top_positive_label']} (+{shap_result['top_positive_value']}) vs {shap_result['top_negative_label']} ({shap_result['top_negative_value']})")
        return response
        
    except Exception as e:
        print(f"❌ SHAP analysis failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "shap_values": {},
            "top_positive_factor": "",
            "top_positive_label": "",
            "top_positive_value": 0,
            "top_negative_factor": "",
            "top_negative_label": "",
            "top_negative_value": 0,
            "approval_probability": 0.0,
            "explanation_text": "Explainability analysis failed due to processing error",
            "base_value": 0.0,
            "formatted": {
                "values": {},
                "normalized": {},
                "impacts": {},
                "top_positive": {"factor": "", "label": "", "value": 0},
                "top_negative": {"factor": "", "label": "", "value": 0},
                "approval_probability": 0.0,
                "explanation_text": ""
            }
        }
