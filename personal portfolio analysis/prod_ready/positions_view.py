from typing import List, Dict
from data_model import NormalizedHolding

def total_positions(holdings: List[NormalizedHolding]) -> Dict[str, Dict[str, float]]:
    positions = {}
    
    for holding in holdings:
        ticker = holding.ticker
        if ticker not in positions:
            positions[ticker] = {"total_shares": 0.0, "total_market_value": 0.0}
        
        positions[ticker]["total_shares"] += holding.shares
        positions[ticker]["total_market_value"] += holding.market_value
    
    return positions

def drilldown_positions(holdings: List[NormalizedHolding], ticker: str) -> List[Dict]:
    breakdown = []
    
    for holding in holdings:
        if holding.ticker == ticker:
            breakdown.append({
                "account_id": holding.account_id,
                "account_name": holding.account_name,
                "shares": holding.shares,
                "market_value": holding.market_value,
                "account_type": holding.account_type,
                "tax_type": holding.tax_type
            })
    
    return breakdown

def top_n_positions(holdings: List[NormalizedHolding], n: int) -> List[Dict[str, float]]:
    positions = total_positions(holdings)
    
    sorted_positions = sorted(
        [(ticker, data["total_market_value"]) for ticker, data in positions.items()],
        key=lambda x: x[1],
        reverse=True
    )[:n]
    
    return [
        {
            "ticker": ticker,
            "total_shares": positions[ticker]["total_shares"],
            "total_market_value": market_value
        }
        for ticker, market_value in sorted_positions
    ]