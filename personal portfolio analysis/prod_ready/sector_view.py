from typing import List, Dict
from data_model import NormalizedHolding

TICKER_TO_SECTOR = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL": "Technology",
    "AMZN": "Consumer Discretionary",
    "TSLA": "Consumer Discretionary",
    "META": "Technology",
    "NVDA": "Technology",
    "BRK.B": "Financials",
    "JPM": "Financials",
    "JNJ": "Healthcare",
    "V": "Financials",
    "PG": "Consumer Staples",
    "HD": "Consumer Discretionary",
    "MA": "Financials",
    "UNH": "Healthcare",
    "DIS": "Communication Services",
    "ADBE": "Technology",
    "PYPL": "Financials",
    "NFLX": "Communication Services",
    "CRM": "Technology",
    "KO": "Consumer Staples",
    "PFE": "Healthcare",
    "CMCSA": "Communication Services",
    "INTC": "Technology",
    "VZ": "Communication Services",
    "T": "Communication Services",
    "ABT": "Healthcare",
    "NKE": "Consumer Discretionary",
    "TMO": "Healthcare",
    "COST": "Consumer Staples"
}

def aggregate_by_sector(holdings: List[NormalizedHolding]) -> Dict[str, float]:
    sector_totals = {}
    
    for holding in holdings:
        sector = TICKER_TO_SECTOR.get(holding.ticker, "Other")
        if sector not in sector_totals:
            sector_totals[sector] = 0.0
        sector_totals[sector] += holding.market_value
    
    return sector_totals

def sector_weights(holdings: List[NormalizedHolding]) -> Dict[str, float]:
    sector_totals = aggregate_by_sector(holdings)
    total_value = sum(sector_totals.values())
    
    if total_value == 0:
        return {}
    
    return {
        sector: round((value / total_value) * 100, 2)
        for sector, value in sector_totals.items()
    }