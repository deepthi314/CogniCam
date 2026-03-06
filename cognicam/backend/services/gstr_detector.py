from typing import Dict, Any, List

def detect_circular_trading(gstr2a_data: Dict[str, Any], gstr3b_data: Dict[str, Any], bank_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect GST fraud patterns including circular trading, ITC mismatch, and revenue inflation.
    
    Args:
        gstr2a_data: GSTR-2A data (purchase returns)
        gstr3b_data: GSTR-3B data (summary returns)
        bank_data: Bank statement data
        
    Returns:
        Dictionary with flags, risk level, and detailed analysis
    """
    print("🔍 Starting GST fraud detection analysis...")
    
    flags = []
    risk_factor = 0.0
    details = {}
    
    # CHECK 1 — ITC Mismatch
    itc_claimed = gstr2a_data.get("total_itc_claimed", 0)
    tax_paid = gstr3b_data.get("total_tax_paid", 0)
    
    if tax_paid > 0:
        itc_ratio = itc_claimed / tax_paid
        details["itc_ratio"] = round(itc_ratio, 3)
        
        if itc_ratio > 1.20:
            excess_pct = round((itc_ratio - 1.0) * 100, 1)
            flags.append(f"ITC Mismatch - {excess_pct}% excess claimed")
            risk_factor += 0.35
            print(f"⚠️ ITC Mismatch detected: {itc_ratio:.3f} ratio")
        else:
            print(f"✅ ITC check passed: {itc_ratio:.3f} ratio")
    else:
        details["itc_ratio"] = 0.0
        print("⚠️ No tax paid data available for ITC comparison")
    
    # CHECK 2 — Revenue Inflation
    declared_turnover = gstr3b_data.get("declared_turnover", 0)
    bank_credits = bank_data.get("total_credits", 0)
    
    if declared_turnover > 0:
        inflation_ratio = bank_credits / declared_turnover
        details["revenue_inflation_ratio"] = round(inflation_ratio, 3)
        
        if bank_credits > declared_turnover * 1.30:
            excess_pct = round((inflation_ratio - 1.0) * 100, 1)
            flags.append(f"Revenue Inflation - {excess_pct}% bank credits excess")
            risk_factor += 0.30
            print(f"⚠️ Revenue Inflation detected: {inflation_ratio:.3f} ratio")
        else:
            print(f"✅ Revenue check passed: {inflation_ratio:.3f} ratio")
    else:
        details["revenue_inflation_ratio"] = 0.0
        print("⚠️ No turnover data available for revenue comparison")
    
    # CHECK 3 — Circular Trading
    supplier_gstins = set(gstr2a_data.get("supplier_gstins", []))
    customer_gstins = set(gstr3b_data.get("customer_gstins", []))
    
    if supplier_gstins and customer_gstins:
        overlap = supplier_gstins.intersection(customer_gstins)
        overlap_ratio = len(overlap) / max(len(supplier_gstins), 1)
        details["circular_overlap_ratio"] = round(overlap_ratio, 3)
        
        if overlap_ratio > 0.40:
            flags.append(f"Circular Trading Suspected - {len(overlap)} overlapping parties")
            risk_factor += 0.45
            print(f"⚠️ Circular Trading detected: {overlap_ratio:.3f} overlap ratio")
            print(f"🔗 Overlapping GSTINs: {list(overlap)[:3]}...")
        else:
            print(f"✅ Circular trading check passed: {overlap_ratio:.3f} overlap ratio")
    else:
        details["circular_overlap_ratio"] = 0.0
        print("⚠️ Insufficient GSTIN data for circular trading analysis")
    
    # CHECK 4 — Low Tax Rate
    if declared_turnover > 0:
        effective_rate = tax_paid / declared_turnover
        details["effective_tax_rate"] = round(effective_rate, 4)
        
        if effective_rate < 0.02:
            flags.append(f"Unusually Low Tax Rate - {effective_rate*100:.2f}%")
            risk_factor += 0.20
            print(f"⚠️ Low tax rate detected: {effective_rate*100:.2f}%")
        else:
            print(f"✅ Tax rate check passed: {effective_rate*100:.2f}%")
    else:
        details["effective_tax_rate"] = 0.0
        print("⚠️ No turnover data available for tax rate analysis")
    
    # Compute risk level
    if "Circular Trading Suspected" in " ".join(flags) or len(flags) >= 3:
        risk_level = "High"
        confidence = min(0.99, risk_factor + 0.3)
    elif len(flags) >= 2:
        risk_level = "Medium"
        confidence = min(0.89, risk_factor + 0.2)
    else:
        risk_level = "Low"
        confidence = max(0.1, risk_factor)
    
    # Build explanation
    if flags:
        explanation = f"GST analysis reveals {len(flags)} compliance issues: " + "; ".join(flags[:3])
        if len(flags) > 3:
            explanation += f" and {len(flags) - 3} additional concerns"
    else:
        explanation = "No significant GST compliance anomalies detected"
    
    result = {
        "flags": flags,
        "risk_level": risk_level,
        "confidence_score": round(confidence, 3),
        "explanation": explanation,
        "details": details
    }
    
    print(f"📊 GST Analysis Complete: {risk_level} risk, {len(flags)} flags, {confidence:.1%} confidence")
    return result

def analyze_gstr_compliance_trends(gstr_data: Dict[str, Any], months: int = 12) -> Dict[str, Any]:
    """
    Analyze GSTR filing compliance trends over time.
    
    Args:
        gstr_data: GSTR filing data
        months: Number of months to analyze
        
    Returns:
        Compliance analysis results
    """
    print(f"📈 Analyzing GSTR compliance trends for {months} months...")
    
    filing_status = gstr_data.get("filing_status", {})
    if not filing_status:
        return {"status": "No filing data available"}
    
    # Count timely vs delayed filings
    timely_filings = 0
    delayed_filings = 0
    missed_filings = 0
    
    for month, status in filing_status.items():
        if status.lower() == "filed":
            timely_filings += 1
        elif status.lower() in ["delayed", "late"]:
            delayed_filings += 1
        else:
            missed_filings += 1
    
    total_months = len(filing_status)
    compliance_rate = (timely_filings / total_months) * 100 if total_months > 0 else 0
    
    result = {
        "total_months_analyzed": total_months,
        "timely_filings": timely_filings,
        "delayed_filings": delayed_filings,
        "missed_filings": missed_filings,
        "compliance_rate": round(compliance_rate, 1),
        "compliance_grade": _get_compliance_grade(compliance_rate),
        "risk_flag": compliance_rate < 80
    }
    
    print(f"📊 GSTR Compliance: {compliance_rate:.1f}% ({result['compliance_grade']})")
    return result

def _get_compliance_grade(compliance_rate: float) -> str:
    """Get compliance grade based on filing percentage"""
    if compliance_rate >= 95:
        return "Excellent"
    elif compliance_rate >= 85:
        return "Good"
    elif compliance_rate >= 70:
        return "Average"
    elif compliance_rate >= 50:
        return "Poor"
    else:
        return "Very Poor"
