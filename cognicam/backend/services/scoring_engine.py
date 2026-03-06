from typing import Dict, Any, List
import math

class FiveCsEngine:
    """Five Cs credit scoring engine for Indian SME lending"""
    
    def __init__(self):
        self.weights = {
            "character": 0.25,
            "capacity": 0.25,
            "capital": 0.20,
            "collateral": 0.15,
            "conditions": 0.15
        }
        
        self.STRESSED_SECTORS = {
            "real_estate", "crypto", "textile", "construction", "hospitality"
        }
        
        self.GROWTH_SECTORS = {
            "pharma", "it", "agritech", "edtech", "healthcare", "renewable_energy"
        }
    
    def calculate_scores(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate Five Cs scores and credit recommendation.
        """
        # --- Section 1C: Pull inputs from data dict ---
        financial_data = data.get("financial_data", {})
        litigation_cases = data.get("litigation_cases", [])
        news_articles = data.get("news_articles", []) or data.get("news_sentiments", []) # Support both naming conventions
        gstr_flags = data.get("gstr_flags", {})
        field_note = data.get("field_note", "")
        sector = data.get("sector", "general")
        company_info = data.get("company_info", {})
        company_name = company_info.get("name", "Unknown")
        annual_turnover_range = company_info.get("turnover", "₹5-25 cr")
        gstin = company_info.get("gstin", "") or ""

        # Add a name-based jitter for variation (Section 1A)
        name_hash = sum(ord(c) for c in company_name) % 10
        jitter = (name_hash - 5) / 2.0 # -2.5 to 2.0

        # --- Section 1A: Modifiers ---
        SECTOR_MODIFIERS = {
          'it':{'character':3,'capacity':2,'capital':1,'collateral':-3,'conditions':4},
          'it & services':{'character':3,'capacity':2,'capital':1,'collateral':-3,'conditions':4},
          'pharma':{'character':2,'capacity':1,'capital':2,'collateral':1,'conditions':2},
          'pharmaceuticals':{'character':2,'capacity':1,'capital':2,'collateral':1,'conditions':2},
          'real estate':{'character':-2,'capacity':-4,'capital':-2,'collateral':5,'conditions':-5},
          'textile':{'character':-1,'capacity':-2,'capital':-1,'collateral':2,'conditions':-3},
          'textile & apparel':{'character':-1,'capacity':-2,'capital':-1,'collateral':2,'conditions':-3},
          'manufacturing':{'character':0,'capacity':-1,'capital':0,'collateral':2,'conditions':-1},
          'retail':{'character':1,'capacity':2,'capital':-1,'collateral':-1,'conditions':2},
          'agriculture':{'character':1,'capacity':-3,'capital':-2,'collateral':3,'conditions':-4},
          'hospitality':{'character':0,'capacity':-3,'capital':-1,'collateral':2,'conditions':-4},
          'nbfc':{'character':-1,'capacity':3,'capital':-2,'collateral':-2,'conditions':-3},
        }

        TURNOVER_MODS = {
          '1 cr':  {'capacity':-5,'capital':-8,'collateral':-5},
          '5 cr':  {'capacity':-2,'capital':-4,'collateral':-2},
          '25 cr': {'capacity':1, 'capital':2, 'collateral':2},
          '100 cr':{'capacity':3, 'capital':4, 'collateral':4},
        }

        HIGH_RISK_STATES = ['20','21','22','14','15','16','17','18']
        LOW_RISK_STATES  = ['27','29','07','24','33','19']

        # Get inputs from request
        sector_key = (sector or 'manufacturing').lower().strip()
        s_mod = SECTOR_MODIFIERS.get(sector_key,
                {'character':0,'capacity':0,'capital':0,'collateral':0,'conditions':0})

        t_mod = {'capacity':0,'capital':0,'collateral':0}
        turnover_str = (annual_turnover_range or '').lower()
        for key, mod in TURNOVER_MODS.items():
            if key in turnover_str:
                t_mod = mod
                break

        gstin_str = (gstin or '27AABCS1234A1Z5')
        state_code = gstin_str[:2]
        state_adj = 2 if state_code in LOW_RISK_STATES else (-3 if state_code in HIGH_RISK_STATES else 0)

        # Research penalties
        lit_cases  = litigation_cases if isinstance(litigation_cases, list) else []
        news_arts  = news_articles if isinstance(news_articles, list) else []
        active_lit = sum(1 for c in lit_cases if isinstance(c,dict) and
                     c.get('status','').lower() in ['active','pending'])
        neg_news   = sum(1 for a in news_arts if isinstance(a,dict) and a.get('credit_risk_flag', False))
        lit_pen    = min(active_lit * 8, 25)
        news_pen   = min(neg_news * 4, 15)

        print(f"[SCORING] sector={sector_key} s_mod={s_mod} lit_pen={lit_pen} news_pen={news_pen}")

        # Calculate base scores
        character_score, rationale_char = self._calculate_character_score(lit_cases, news_arts, gstr_flags)
        capacity_score, rationale_cap = self._calculate_capacity_score(financial_data, field_note)
        capital_score, rationale_capit = self._calculate_capital_score(financial_data)
        collateral_score, rationale_coll = self._calculate_collateral_score(field_note)
        conditions_score, rationale_cond = self._calculate_conditions_score(sector, news_arts)

        # --- Section 1B: Apply ALL modifiers ---
        def _clamp(v, cap=100): return max(0, min(cap, v))

        character_score  = _clamp(character_score  + s_mod['character']  + state_adj - lit_pen - news_pen + jitter, 96)
        capacity_score   = _clamp(capacity_score   + s_mod['capacity']   + t_mod['capacity'] + jitter)
        capital_score    = _clamp(capital_score    + s_mod['capital']    + t_mod['capital'] + jitter)
        collateral_score = _clamp(collateral_score + s_mod['collateral'] + t_mod['collateral'] + jitter)
        conditions_score = _clamp(conditions_score + s_mod['conditions'] + state_adj + jitter)

        scores = {
            "character": character_score,
            "capacity": capacity_score,
            "capital": capital_score,
            "collateral": collateral_score,
            "conditions": conditions_score
        }

        # Calculate weighted final score
        final_score = sum(scores[c] * self.weights[c] for c in scores.keys())
        final_score = min(97.0, round(final_score, 1))
        
        # Generate recommendation
        recommendation = self._generate_recommendation(final_score, financial_data)
        
        result = {
            "scores": scores,
            "rationales": {
                "character": rationale_char,
                "capacity": rationale_cap,
                "capital": rationale_capit,
                "collateral": rationale_coll,
                "conditions": rationale_cond
            },
            "final_score": final_score,
            "recommendation": recommendation,
            "weights": self.weights.copy()
        }
        
        print(f"✅ Scoring Complete: Final Score {final_score}/100 - {recommendation['decision']}")
        return result
    
    def _calculate_character_score(self, litigation_cases: List[Dict], news_sentiments: List[Dict], gstr_flags: Dict) -> tuple:
        """Calculate Character score based on legal issues, news sentiment, and GST compliance"""
        
        score = 100
        reasons = []
        
        # Check litigation cases
        active_cases = [
            case for case in litigation_cases 
            if isinstance(case, dict) and case.get("status", "").lower() in ["pending", "active"]
        ]
        
        if active_cases:
            deduction = min(len(active_cases) * 15, 60)
            score -= deduction
            reasons.append(f"{len(active_cases)} active litigation cases (-{deduction})")
        
        # Check news sentiment
        flagged_news = [
            article for article in news_sentiments 
            if isinstance(article, dict) and article.get("credit_risk_flag", False)
        ]
        
        if flagged_news:
            deduction = min(len(flagged_news) * 10, 30)
            score -= deduction
            reasons.append(f"{len(flagged_news)} negative news articles (-{deduction})")
        
        # Check GST flags
        gst_flags_list = gstr_flags.get("flags", [])
        
        if "Circular Trading Suspected" in gst_flags_list:
            score -= 20
            reasons.append("Circular trading suspected (-20)")
        
        if "ITC Mismatch" in gst_flags_list:
            score -= 10
            reasons.append("ITC mismatch detected (-10)")
        
        if "Revenue Inflation" in gst_flags_list:
            score -= 10
            reasons.append("Revenue inflation detected (-10)")
        
        score = max(0, score)
        
        if not reasons:
            reasons.append("No significant character issues identified")
        
        rationale = "; ".join(reasons)
        return score, rationale
    
    def _calculate_capacity_score(self, financial_data: Dict, field_note: str) -> tuple:
        """Calculate Capacity score based on financial ratios and operational capacity"""
        
        score = 0
        reasons = []
        
        # Base score from current ratio
        current_ratio = financial_data.get("current_ratio", 1.0)
        
        if current_ratio >= 2.0:
            score = 80
            reasons.append("Strong current ratio")
        elif current_ratio >= 1.5:
            score = 65
            reasons.append("Adequate current ratio")
        elif current_ratio >= 1.0:
            score = 50
            reasons.append("Moderate current ratio")
        else:
            score = 30
            reasons.append("Weak current ratio")
        
        # Add bonus for profitability
        net_profit = financial_data.get("net_profit", 0)
        if net_profit > 0:
            score += 10
            reasons.append("Positive net profit (+10)")
        
        # Add bonus for scale
        annual_turnover = financial_data.get("annual_turnover", 0)
        if annual_turnover >= 10_000_000:
            score += 10
            reasons.append("Significant turnover (+10)")
        
        # Check field note for capacity issues
        capacity_keywords = ["capacity", "idle", "shortage", "shutdown", "underutilized", "halted"]
        field_lower = field_note.lower()
        
        if any(keyword in field_lower for keyword in capacity_keywords):
            score -= 20
            reasons.append("Capacity concerns noted (-20)")
        
        score = max(0, min(100, score))
        rationale = "; ".join(reasons) if reasons else "Standard capacity assessment"
        
        return score, rationale
    
    def _calculate_capital_score(self, financial_data: Dict) -> tuple:
        """Calculate Capital score based on debt-to-equity and asset base"""
        
        score = 0
        reasons = []
        
        # Calculate debt-to-equity ratio
        total_debt = financial_data.get("total_debt", 0)
        total_assets = financial_data.get("total_assets", 1)
        net_worth = max(total_assets - total_debt, 1)
        de_ratio = total_debt / net_worth
        
        if de_ratio < 1:
            score = 85
            reasons.append("Low debt-to-equity ratio")
        elif de_ratio < 2:
            score = 65
            reasons.append("Moderate debt-to-equity ratio")
        elif de_ratio < 3:
            score = 45
            reasons.append("High debt-to-equity ratio")
        else:
            score = 25
            reasons.append("Very high debt-to-equity ratio")
        
        # Add bonus for asset base
        if total_assets >= 5_000_000:
            score += 10
            reasons.append("Strong asset base (+10)")
        
        score = max(0, min(100, score))
        rationale = "; ".join(reasons) if reasons else "Standard capital assessment"
        
        return score, rationale
    
    def _calculate_collateral_score(self, field_note: str) -> tuple:
        """Calculate Collateral score based on field observations"""
        
        score = 60  # Base score
        reasons = []
        
        field_lower = field_note.lower()
        
        # Positive collateral indicators
        positive_keywords = ["mortgaged", "unencumbered", "clear title", "freehold", "registered"]
        if any(keyword in field_lower for keyword in positive_keywords):
            score += 15
            reasons.append("Strong collateral position (+15)")
        
        # Negative collateral indicators
        negative_keywords = ["disputed", "encumbered", "legal hold", "rented", "no collateral"]
        if any(keyword in field_lower for keyword in negative_keywords):
            score -= 20
            reasons.append("Collateral concerns (-20)")
        
        score = max(0, min(100, score))
        rationale = "; ".join(reasons) if reasons else "Standard collateral assessment"
        
        return score, rationale
    
    def _calculate_conditions_score(self, sector: str, news_sentiments: List[Dict]) -> tuple:
        """Calculate Conditions score based on sector outlook and market sentiment"""
        
        score = 65  # Base score
        reasons = []
        
        sector_lower = sector.lower()
        
        # Sector adjustments
        if sector_lower in self.STRESSED_SECTORS:
            score -= 10
            reasons.append("Stressed sector (-10)")
        elif sector_lower in self.GROWTH_SECTORS:
            score += 10
            reasons.append("Growth sector (+10)")
        
        # News sentiment adjustments
        positive_news = sum(1 for article in news_sentiments if isinstance(article, dict) and article.get("sentiment") == "POSITIVE")
        if positive_news >= 2:
            score += 5
            reasons.append("Positive market sentiment (+5)")
        
        score = max(0, min(100, score))
        rationale = "; ".join(reasons) if reasons else "Standard conditions assessment"
        
        return score, rationale
    
    def _generate_recommendation(self, final_score: float, financial_data: Dict) -> Dict[str, Any]:
        """Generate credit recommendation based on final score"""
        
        annual_turnover = financial_data.get("annual_turnover", 0)
        
        if final_score >= 75:
            decision = "APPROVE"
            limit_cr = round(annual_turnover * 0.30 / 1_00_00_000, 2)  # Convert to crores
            rate = 9.5
            grade = "A"
            tenor = "36 months"
        elif final_score >= 60:
            decision = "CONDITIONAL APPROVE"
            limit_cr = round(annual_turnover * 0.20 / 1_00_00_000, 2)
            rate = 11.0
            grade = "B"
            tenor = "24 months"
        elif final_score >= 45:
            decision = "CONDITIONAL APPROVE"
            limit_cr = round(annual_turnover * 0.12 / 1_00_00_000, 2)
            rate = 13.5
            grade = "C"
            tenor = "12 months"
        else:
            decision = "DECLINE"
            limit_cr = 0
            rate = 0
            grade = "D"
            tenor = "N/A"
        
        confidence = min(0.95, max(0.25, (final_score / 100) + 0.1))
        
        recommendation = {
            "decision": decision,
            "credit_limit": limit_cr * 1_00_00_000,  # Convert back to rupees
            "credit_limit_cr": limit_cr,
            "interest_rate": rate,
            "risk_grade": grade,
            "tenor": tenor,
            "confidence": round(confidence, 3),
            "final_score": final_score
        }
        
        return recommendation
