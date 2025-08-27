from typing import List, Dict
from data_model import NormalizedHolding

TICKER_TO_GEOGRAPHY = {
    "AAPL": "domestic_equity",
    "MSFT": "domestic_equity",
    "GOOGL": "domestic_equity",
    "AMZN": "domestic_equity",
    "TSLA": "domestic_equity",
    "META": "domestic_equity",
    "NVDA": "domestic_equity",
    "BRK.B": "domestic_equity",
    "JPM": "domestic_equity",
    "JNJ": "domestic_equity",
    "V": "domestic_equity",
    "PG": "domestic_equity",
    "HD": "domestic_equity",
    "MA": "domestic_equity",
    "UNH": "domestic_equity",
    "DIS": "domestic_equity",
    "ADBE": "domestic_equity",
    "PYPL": "domestic_equity",
    "NFLX": "domestic_equity",
    "CRM": "domestic_equity",
    "KO": "domestic_equity",
    "PFE": "domestic_equity",
    "CMCSA": "domestic_equity",
    "INTC": "domestic_equity",
    "VZ": "domestic_equity",
    "T": "domestic_equity",
    "ABT": "domestic_equity",
    "NKE": "domestic_equity",
    "TMO": "domestic_equity",
    "COST": "domestic_equity",
    "VTIAX": "international_equity",
    "VXUS": "international_equity",
    "FTIHX": "international_equity",
    "SWISX": "international_equity",
    "EFA": "international_equity",
    "VEA": "international_equity",
    "IEFA": "international_equity",
    "VBTLX": "bonds",
    "FXNAX": "bonds",
    "BND": "bonds",
    "AGG": "bonds",
    "VTEB": "bonds",
    "VGIT": "bonds",
    "VGLT": "bonds"
}

def aggregate_by_geography(holdings: List[NormalizedHolding]) -> Dict[str, float]:
    geography_totals = {"domestic_equity": 0.0, "international_equity": 0.0, "bonds": 0.0}
    
    for holding in holdings:
        geography = TICKER_TO_GEOGRAPHY.get(holding.ticker, "domestic_equity")
        geography_totals[geography] += holding.market_value
    
    return geography_totals

def geography_weights(holdings: List[NormalizedHolding]) -> Dict[str, float]:
    geography_totals = aggregate_by_geography(holdings)
    total_value = sum(geography_totals.values())
    
    if total_value == 0:
        return {"domestic_equity": 0.0, "international_equity": 0.0, "bonds": 0.0}
    
    return {
        geography: round((value / total_value) * 100, 2)
        for geography, value in geography_totals.items()
    }