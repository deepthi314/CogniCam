from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class ResearchRequest(BaseModel):
    company_name: str = Field(..., description="Company name to research")
    gstin: Optional[str] = Field("", description="GSTIN of the company")
    promoter_name: Optional[str] = Field("", description="Promoter/Director name")
    sector: Optional[str] = Field("General", description="Business sector")

class ScoringRequest(BaseModel):
    financial_data: Dict[str, Any] = Field(..., description="Extracted financial data")
    litigation_cases: List[Dict[str, Any]] = Field(default_factory=list, description="Litigation cases found")
    news_sentiments: List[Dict[str, Any]] = Field(default_factory=list, description="News articles with sentiment")
    gstr_flags: Dict[str, Any] = Field(default_factory=dict, description="GST compliance flags")
    field_note: Optional[str] = Field("", description="Field officer observations")
    sector: Optional[str] = Field("general", description="Business sector")
    company_info: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional company info (GSTIN, turnover)")

class ExplainRequest(BaseModel):
    scores: Dict[str, float] = Field(..., description="Five Cs scores")

class ReportRequest(BaseModel):
    company_name: str = Field(..., description="Company name")
    financial_data: Dict[str, Any] = Field(..., description="Financial data")
    scores: Dict[str, Any] = Field(..., description="Five Cs scores with rationales")
    recommendation: Dict[str, Any] = Field(..., description="Credit recommendation")
    mca_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="MCA registry data")
    litigation_cases: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Litigation cases")
    news_articles: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="News articles")
    gstr_flags: Optional[Dict[str, Any]] = Field(default_factory=dict, description="GST compliance flags")
    shap_explanation: Optional[Dict[str, Any]] = Field(default_factory=dict, description="SHAP explainability")
    field_note: Optional[str] = Field("", description="Field officer notes")

# Response models for API consistency
class APIResponse(BaseModel):
    status: str = Field(..., description="API call status")
    message: Optional[str] = Field(None, description="Optional message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

class IngestionResponse(BaseModel):
    status: str
    extracted_data: Dict[str, Any]
    gstr_flags: Dict[str, Any]
    raw_text_preview: str
    files_processed: List[str]

class ResearchResponse(BaseModel):
    status: str
    mca_data: Dict[str, Any]
    litigation_cases: List[Dict[str, Any]]
    news_articles_with_sentiment: List[Dict[str, Any]]
    news_summary: str
    sentiment_stats: Dict[str, Any]
    promoter_research: Optional[Dict[str, Any]] = None
    sector_headwinds: Optional[Dict[str, Any]] = None

class ScoringResponse(BaseModel):
    status: str
    scores: Dict[str, int]
    rationales: Dict[str, str]
    final_score: float
    recommendation: Dict[str, Any]
    weights: Dict[str, float]
    scores_after_field_note: Optional[Dict[str, int]] = None
    field_note_rationale: Optional[Dict[str, str]] = None

class ExplainabilityResponse(BaseModel):
    status: str
    shap_values: Dict[str, float]
    top_positive_factor: str
    top_positive_label: str
    top_negative_factor: str
    top_negative_label: str
    approval_probability: float
    explanation_text: str
    base_value: float
