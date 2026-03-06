from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Optional
from database import save_appraisal, get_user_appraisals, get_appraisal_by_id, delete_appraisal, get_dashboard_stats, get_portfolio_analytics
from routers.auth import get_current_user
import json

router = APIRouter()

@router.get("/analytics")
async def get_analytics(request: Request):
    user, _ = get_current_user(request)
    analytics = get_portfolio_analytics(user['id'])
    return analytics

@router.get("/")
async def get_history(request: Request, page: int = 1, limit: int = 10, search: str = "", decision: str = "all"):
    user, _ = get_current_user(request)
    offset = (page - 1) * limit
    results = get_user_appraisals(user['id'], limit=limit, offset=offset, search=search, decision_filter=decision)
    return results

@router.get("/stats")
async def history_stats(request: Request):
    user, _ = get_current_user(request)
    stats = get_dashboard_stats(user['id'])
    return stats

@router.get("/{id}")
async def get_history_detail(id: int, request: Request):
    user, _ = get_current_user(request)
    appraisal = get_appraisal_by_id(id, user['id'])
    if not appraisal:
        raise HTTPException(status_code=404, detail="Appraisal not found")
        
    if appraisal.get('full_report_json'):
        appraisal['full_report_json'] = json.loads(appraisal['full_report_json'])
    
    return appraisal

@router.delete("/{id}")
async def archive_history(id: int, request: Request):
    user, _ = get_current_user(request)
    success = delete_appraisal(id, user['id'])
    if not success:
        raise HTTPException(status_code=404, detail="Appraisal not found or already deleted")
    return {"message": "Appraisal archived"}

@router.post("/save")
async def save_history(request: Request):
    user, token = get_current_user(request)
    data = await request.json()
    data['token'] = token
    appraisal_id = save_appraisal(user['id'], data)
    return {"id": appraisal_id, "message": "Appraisal saved"}
