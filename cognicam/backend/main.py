from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import routers
from routers.ingestor import router as ingestor_router
from routers.research import router as research_router
from routers.scoring import router as scoring_router
from routers.explainability import router as explainability_router
from routers.report import router as report_router
from routers.auth import router as auth_router
from routers.history import router as history_router
from database import init_db

# Create FastAPI app
app = FastAPI(
    title="COGNICAM API",
    description="Context-Aware Credit Appraisal Engine for Indian SME Lending",
    version="1.0.0"
)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers with /api prefix
app.include_router(ingestor_router, prefix="/api/ingest", tags=["ingestor"])
app.include_router(research_router, prefix="/api/research", tags=["research"])
app.include_router(scoring_router, prefix="/api/scoring", tags=["scoring"])
app.include_router(explainability_router, prefix="/api", tags=["explainability"])
app.include_router(report_router, prefix="/api", tags=["report"])
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(history_router, prefix="/api/history", tags=["history"])

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "COGNICAM Online", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "COGNICAM",
        "version": "1.0.0",
        "description": "Context-Aware Credit Appraisal Engine"
    }

if __name__ == "__main__":
    # Print startup banner
    print("=" * 60)
    print("COGNICAM - Context-Aware Credit Appraisal Engine")
    print("IIT Hyderabad Hackathon 2025")
    print("=" * 60)
    print("🚀 Starting FastAPI server on http://0.0.0.0:8000")
    print("📖 API Documentation: http://0.0.0.0:8000/docs")
    print("=" * 60)
    
    # Run uvicorn server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
