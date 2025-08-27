from typing import List, Dict
from data_model import NormalizedHolding

def aggregate_by_account_type(holdings: List[NormalizedHolding]) -> Dict[str, float]:
    totals = {"retirement": 0.0, "brokerage": 0.0}
    
    for holding in holdings:
        if holding.account_type in totals:
            totals[holding.account_type] += holding.market_value
    
    return totals

def aggregate_by_tax_type(holdings: List[NormalizedHolding]) -> Dict[str, float]:
    totals = {"pre_tax": 0.0, "roth": 0.0, "non_retirement": 0.0}
    
    for holding in holdings:
        if holding.tax_type in totals:
            totals[holding.tax_type] += holding.market_value
    
    return totals

def aggregate_by_asset_class(holdings: List[NormalizedHolding]) -> Dict[str, float]:
    totals = {"equity": 0.0, "fixed_income": 0.0, "other": 0.0}
    
    for holding in holdings:
        if holding.asset_class in totals:
            totals[holding.asset_class] += holding.market_value
        else:
            totals["other"] += holding.market_value
    
    return totals

def get_equity_fixed_income_ratio(holdings: List[NormalizedHolding]) -> float:
    asset_totals = aggregate_by_asset_class(holdings)
    equity = asset_totals["equity"]
    fixed_income = asset_totals["fixed_income"]
    
    total = equity + fixed_income
    if total == 0:
        return 0.0
    
    return round(equity / total, 2)

def aggregate_by_owner(holdings: List[NormalizedHolding]) -> Dict[str, float]:
    totals = {}
    
    for holding in holdings:
        owner = holding.owner
        if owner not in totals:
            totals[owner] = 0.0
        totals[owner] += holding.market_value
    
    return totals

def aggregate_by_brokerage(holdings: List[NormalizedHolding]) -> Dict[str, float]:
    totals = {}
    
    for holding in holdings:
        brokerage = holding.brokerage
        if brokerage not in totals:
            totals[brokerage] = 0.0
        totals[brokerage] += holding.market_value
    
    return totals