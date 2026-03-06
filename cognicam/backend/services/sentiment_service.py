from typing import List, Dict, Any, Tuple
import re

# Credit risk keywords for flagging
CREDIT_RISK_KEYWORDS = [
    "default", "npa", "fraud", "scam", "raid", "seized", "insolvency",
    "bankruptcy", "nclt", "drt", "recovery", "wilful defaulter", "ed raid",
    "income tax notice", "gst evasion", "money laundering", "shutdown",
    "closure", "layoffs", "losses", "debt trap", "cheque bounce"
]

# Global pipeline for lazy loading
_sentiment_pipeline = None

def _get_pipeline():
    """Get or create sentiment analysis pipeline (lazy loading)"""
    global _sentiment_pipeline
    
    if _sentiment_pipeline is None:
        try:
            print("🤖 Loading DistilBERT (67MB, CPU)...")
            from transformers import pipeline
            
            _sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english",
                device=-1,  # Force CPU
                max_length=512,
                truncation=True
            )
            print("✅ DistilBERT loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to load DistilBERT: {str(e)}")
            print("⚠️ Falling back to rule-based sentiment analysis")
            _sentiment_pipeline = "FALLBACK"
    
    return _sentiment_pipeline

def _rule_based_sentiment(text: str) -> Tuple[str, float]:
    """
    Rule-based sentiment analysis as fallback.
    
    Args:
        text: Text to analyze
        
    Returns:
        Tuple of (label, confidence)
    """
    # Negative indicators
    negative_words = [
        "fraud", "scam", "loss", "default", "npa", "raid", "decline", 
        "shutdown", "bankruptcy", "seized", "liquidation", "crisis"
    ]
    
    # Positive indicators
    positive_words = [
        "profit", "growth", "expansion", "award", "record", "success", 
        "approved", "strong", "robust", "excellent", "achievement"
    ]
    
    text_lower = text.lower()
    
    negative_count = sum(1 for word in negative_words if word in text_lower)
    positive_count = sum(1 for word in positive_words if word in text_lower)
    
    if negative_count > positive_count + 1:
        return "NEGATIVE", min(0.92, 0.60 + negative_count * 0.08)
    elif positive_count > negative_count + 1:
        return "POSITIVE", min(0.92, 0.60 + positive_count * 0.08)
    else:
        return "NEUTRAL", 0.65

def classify_news_sentiment(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Classify sentiment for news articles using DistilBERT or fallback.
    
    Args:
        articles: List of news articles with title and snippet
        
    Returns:
        List of articles with sentiment analysis added
    """
    print(f"📊 Analyzing sentiment for {len(articles)} articles...")
    
    pipeline = _get_pipeline()
    results = []
    
    for i, article in enumerate(articles):
        try:
            # Combine title and snippet for analysis
            text = f"{article.get('title', '')} {article.get('snippet', '')}"
            text = text[:512]  # Truncate to 512 chars
            
            if pipeline == "FALLBACK":
                label, confidence = _rule_based_sentiment(text)
                print(f"📝 Article {i+1}: {label} (rule-based, {confidence:.2f})")
            else:
                # Use DistilBERT
                result = pipeline(text)[0]
                label = result['label']
                confidence = result['score']
                
                # DistilBERT returns POSITIVE/NEGATIVE, convert to NEUTRAL if low confidence
                if confidence < 0.60:
                    label = "NEUTRAL"
                
                print(f"📝 Article {i+1}: {label} ({confidence:.2f})")
            
            # Check for credit risk keywords
            text_lower = text.lower()
            credit_keywords_found = [kw for kw in CREDIT_RISK_KEYWORDS if kw in text_lower]
            credit_risk_flag = (
                (label == "NEGATIVE" and confidence > 0.70) or 
                len(credit_keywords_found) > 0
            )
            
            # Build result
            sentiment_result = {
                "headline": article.get("title", ""),
                "snippet": article.get("snippet", ""),
                "sentiment": label,
                "confidence": round(confidence, 3),
                "credit_risk_flag": credit_risk_flag,
                "credit_keywords": credit_keywords_found,
                "published": article.get("published", ""),
                "source": article.get("source", ""),
                "url": article.get("url", "")
            }
            
            results.append(sentiment_result)
            
        except Exception as e:
            print(f"❌ Error analyzing article {i+1}: {str(e)}")
            # Add neutral result on error
            results.append({
                "headline": article.get("title", ""),
                "snippet": article.get("snippet", ""),
                "sentiment": "NEUTRAL",
                "confidence": 0.5,
                "credit_risk_flag": False,
                "credit_keywords": [],
                "published": article.get("published", ""),
                "source": article.get("source", ""),
                "url": article.get("url", "")
            })
    
    # Print summary
    positive_count = sum(1 for r in results if r["sentiment"] == "POSITIVE")
    negative_count = sum(1 for r in results if r["sentiment"] == "NEGATIVE")
    neutral_count = sum(1 for r in results if r["sentiment"] == "NEUTRAL")
    risk_flagged = sum(1 for r in results if r["credit_risk_flag"])
    
    print(f"📈 Sentiment Analysis Complete: {positive_count} positive, {negative_count} negative, {neutral_count} neutral, {risk_flagged} risk-flagged")
    
    return results

def calculate_sentiment_stats(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate sentiment statistics from analyzed articles.
    
    Args:
        articles: List of articles with sentiment analysis
        
    Returns:
        Dictionary with sentiment statistics
    """
    if not articles:
        return {
            "total": 0,
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "credit_risk_flagged": 0,
            "average_confidence": 0.0
        }
    
    total = len(articles)
    positive = sum(1 for a in articles if a["sentiment"] == "POSITIVE")
    negative = sum(1 for a in articles if a["sentiment"] == "NEGATIVE")
    neutral = sum(1 for a in articles if a["sentiment"] == "NEUTRAL")
    credit_risk_flagged = sum(1 for a in articles if a["credit_risk_flag"])
    
    avg_confidence = sum(a["confidence"] for a in articles) / total
    
    stats = {
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "credit_risk_flagged": credit_risk_flagged,
        "average_confidence": round(avg_confidence, 3),
        "positive_percentage": round((positive / total) * 100, 1),
        "negative_percentage": round((negative / total) * 100, 1),
        "neutral_percentage": round((neutral / total) * 100, 1)
    }
    
    print(f"📊 Sentiment Stats: {stats['positive']}% positive, {stats['negative']}% negative, {stats['neutral']}% neutral")
    return stats
