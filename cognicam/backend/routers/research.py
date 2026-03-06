from fastapi import APIRouter
from models.schemas import ResearchRequest
import asyncio
from services.scraper_service import scrape_mca_director_details, scrape_ecourts_litigation, scrape_google_news
from services.sentiment_service import classify_news_sentiment, calculate_sentiment_stats
from services.llm_service import summarize_news

router = APIRouter()

@router.post("/research", response_model=dict)
async def research_company(request: ResearchRequest):
    """
    Perform comprehensive research on company including MCA data, litigation cases, and news sentiment.
    """
    print(f"🔍 Starting research for: {request.company_name}")
    
    try:
        # Build search query
        query = f"{request.company_name} {request.promoter_name}".strip()
        print(f"📝 Search query: {query}")
        
        # Run all scrapers concurrently
        print("🌐 Starting concurrent deep research...")
        
        loop = asyncio.get_event_loop()
        from services.scraper_service import research_promoter, get_sector_headwinds
        
        # Create tasks for concurrent execution
        mca_task = loop.run_in_executor(None, scrape_mca_director_details, request.company_name)
        litigation_task = loop.run_in_executor(None, scrape_ecourts_litigation, request.company_name)
        news_task = loop.run_in_executor(None, scrape_google_news, query)
        promoter_task = loop.run_in_executor(None, research_promoter, request.promoter_name or request.company_name)
        sector_task = loop.run_in_executor(None, get_sector_headwinds, request.sector or "General")
        
        # Wait for all tasks to complete
        mca_data, litigation_cases, news_articles, promoter_res, sector_res = await asyncio.gather(
            mca_task, litigation_task, news_task, promoter_task, sector_task
        )
        
        print(f"✅ Deep Research results aggregated.")
        
        # Run sentiment analysis
        sentiment_task = loop.run_in_executor(None, classify_news_sentiment, news_articles)
        news_with_sentiment = await sentiment_task
        
        # Calculate sentiment statistics
        stats_task = loop.run_in_executor(None, calculate_sentiment_stats, news_with_sentiment)
        sentiment_stats = await stats_task
        
        # Generate news summary
        summary_task = loop.run_in_executor(None, summarize_news, news_with_sentiment)
        news_summary = await summary_task
        
        # Prepare response
        response = {
            "status": "success",
            "mca_data": mca_data,
            "litigation_cases": litigation_cases,
            "news_articles_with_sentiment": news_with_sentiment,
            "news_summary": news_summary,
            "sentiment_stats": sentiment_stats,
            "promoter_research": promoter_res,
            "sector_headwinds": sector_res
        }
        
        return response
        
    except Exception as e:
        print(f"❌ Research failed: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "mca_data": {},
            "litigation_cases": [],
            "news_articles_with_sentiment": [],
            "news_summary": "Research failed due to processing error",
            "sentiment_stats": {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "credit_risk_flagged": 0,
                "average_confidence": 0.0
            }
        }
