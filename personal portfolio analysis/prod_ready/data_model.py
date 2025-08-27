import pandas as pd
import os
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class NormalizedHolding:
    account_id: str
    account_name: str
    ticker: str
    shares: float
    market_value: float
    account_type: str  # retirement or brokerage
    tax_type: str      # pre_tax, roth, or non_retirement
    asset_class: str   # equity, fixed_income, or other
    owner: str         # Sammy, Nalae, etc.
    brokerage: str     # Schwab, Fidelity, Vanguard, etc.

def load_ref_data(ref_folder: str) -> Dict[str, Dict[str, str]]:
    ref_data = {}
    
    for filename in os.listdir(ref_folder):
        if filename.endswith('.csv'):
            df = pd.read_csv(os.path.join(ref_folder, filename))
            for _, row in df.iterrows():
                account_id = str(row.get('account_id', ''))
                ref_data[account_id] = {
                    'account_type': row.get('account_type', ''),
                    'tax_type': row.get('tax_type', ''),
                    'account_name': row.get('account_name', '')
                }
    
    return ref_data

def normalize_positions(positions_csv_folder: str, ref_data: Dict[str, Dict[str, str]]) -> List[NormalizedHolding]:
    holdings = []
    
    for filename in os.listdir(positions_csv_folder):
        if filename.endswith('.csv'):
            df = pd.read_csv(os.path.join(positions_csv_folder, filename))
            
            for _, row in df.iterrows():
                account_id = str(row.get('account_id', ''))
                account_info = ref_data.get(account_id, {})
                
                holding = NormalizedHolding(
                    account_id=account_id,
                    account_name=account_info.get('account_name', ''),
                    ticker=str(row.get('ticker', '')),
                    shares=float(row.get('shares', 0)),
                    market_value=float(row.get('market_value', 0)),
                    account_type=account_info.get('account_type', ''),
                    tax_type=account_info.get('tax_type', ''),
                    asset_class=str(row.get('asset_class', 'other'))
                )
                holdings.append(holding)
    
    return holdings