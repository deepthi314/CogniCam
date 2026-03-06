from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from pydantic import BaseModel
from typing import Optional
from database import (
    authenticate_user, create_session, create_user, 
    get_user_from_token, invalidate_session, get_dashboard_stats,
    update_user_profile, update_user_password
)

router = APIRouter()

class ProfileUpdateRequest(BaseModel):
    full_name: str
    organization: str
    email: str
    role: Optional[str] = None

class PasswordUpdateRequest(BaseModel):
    new_password: str

# ... existing code ...

@router.put("/profile")
async def update_profile(req: ProfileUpdateRequest, request: Request):
    user, _ = get_current_user(request)
    success = update_user_profile(user['id'], req.full_name, req.organization, req.email, req.role)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update profile")
    return {"message": "Profile updated successfully"}

@router.put("/password")
async def update_password(req: PasswordUpdateRequest, request: Request):
    user, _ = get_current_user(request)
    # Basic validation
    if len(req.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    success = update_user_password(user['id'], req.new_password)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update password")
    return {"message": "Password updated successfully"}

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str
    organization: str

def get_current_user(request: Request):
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    
    if not token:
        token = request.cookies.get("cognicam_token")
        
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    user = get_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user, token

@router.post("/login")
async def login(req: LoginRequest, response: Response):
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
        
    token = create_session(user['id'])
    
    response.set_cookie(
        key="cognicam_token",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax"
    )
    
    return {"token": token, "user": user}

@router.post("/register")
async def register(req: RegisterRequest, response: Response):
    if len(req.username) < 3 or len(req.username) > 20:
        raise HTTPException(status_code=400, detail="Username must be between 3 and 20 characters")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
    user = create_user(req.username, req.email, req.password, req.full_name, req.organization)
    if not user:
        raise HTTPException(status_code=400, detail="Username or email already exists")
        
    token = create_session(user['id'])
    
    response.set_cookie(
        key="cognicam_token",
        value=token,
        httponly=True,
        max_age=86400,
        samesite="lax"
    )
    
    return {"token": token, "user": user}

@router.post("/logout")
async def logout(request: Request, response: Response):
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    if not token:
        token = request.cookies.get("cognicam_token")
        
    if token:
        invalidate_session(token)
        
    response.delete_cookie("cognicam_token")
    return {"message": "Logged out"}

@router.get("/me")
async def get_me(request: Request):
    user, _ = get_current_user(request)
    stats = get_dashboard_stats(user['id'])
    return {"user": user, "stats": stats}

@router.get("/verify")
async def verify_token(request: Request):
    try:
        user, _ = get_current_user(request)
        return {"valid": True, "user": user}
    except HTTPException:
        return {"valid": False, "user": None}
