from fastapi import APIRouter
from models.schemas import ScoringRequest
from services.scoring_engine import FiveCsEngine
from services.llm_service import adjust_score_from_field_note

router = APIRouter()

# Initialize scoring engine at module level
scoring_engine = FiveCsEngine()

@router.post("/score", response_model=dict)
async def calculate_credit_score(request: ScoringRequest):
    """
    Calculate Five Cs credit score and generate credit recommendation.
    """
    print("🧮 Starting credit scoring calculation...")
    
    try:
        # Prepare data for scoring engine
        data = {
            "financial_data": request.financial_data,
            "litigation_cases": request.litigation_cases,
            "news_sentiments": request.news_sentiments,
            "gstr_flags": request.gstr_flags,
            "field_note": request.field_note,
            "sector": request.sector,
            "company_info": request.company_info
        }
        
        print(f"📊 Input data: {len(request.litigation_cases)} cases, {len(request.news_sentiments)} articles")
        
        # Calculate base scores
        print("🎯 Computing Five Cs scores...")
        scoring_result = scoring_engine.calculate_scores(data)
        
        # Apply field note adjustments if provided
        scores_after_field_note = None
        field_note_rationale = None
        
        if request.field_note and request.field_note.strip():
            print("🧠 Applying field officer adjustments...")
            adjustment_result = adjust_score_from_field_note(
                request.field_note, 
                scoring_result["scores"]
            )
            scores_after_field_note = adjustment_result.get("adjusted_scores", {})
            field_note_rationale = adjustment_result.get("rationale", {})
            
            print(f"✅ Field adjustments applied")
        else:
            print("ℹ️ No field note provided - using base scores")
        
        # Prepare response
        response = {
            "status": "success",
            "scores": scoring_result["scores"],
            "rationales": scoring_result["rationales"],
            "final_score": scoring_result["final_score"],
            "recommendation": scoring_result["recommendation"],
            "weights": scoring_result["weights"],
            "scores_after_field_note": scores_after_field_note,
            "field_note_rationale": field_note_rationale
        }
        
        decision = scoring_result["recommendation"]["decision"]
        final_score = scoring_result["final_score"]
        print(f"✅ Scoring complete: {decision} - {final_score:.1f}/100")
        
        return response
        
    except Exception as e:
        print(f"❌ Scoring failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "scores": {},
            "rationales": {},
            "final_score": 0.0,
            "recommendation": {
                "decision": "ERROR",
                "credit_limit": 0,
                "credit_limit_cr": 0,
                "interest_rate": 0,
                "risk_grade": "N/A",
                "tenor": "N/A",
                "confidence": 0.0,
                "final_score": 0.0
            },
            "weights": scoring_engine.weights,
            "scores_after_field_note": {},
            "field_note_rationale": {}
        }
