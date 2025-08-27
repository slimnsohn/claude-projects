import json
from typing import Dict, Any
from data_model import load_ref_data, normalize_positions
from aggregations import (
    aggregate_by_account_type, 
    aggregate_by_tax_type, 
    aggregate_by_asset_class, 
    get_equity_fixed_income_ratio,
    aggregate_by_owner,
    aggregate_by_brokerage
)
from positions_view import total_positions, drilldown_positions, top_n_positions
from sector_view import aggregate_by_sector, sector_weights
from geo_view import aggregate_by_geography, geography_weights

class PortfolioEngine:
    def __init__(self, ref_folder: str, positions_folder: str):
        self.ref_data = load_ref_data(ref_folder)
        self.holdings = normalize_positions(positions_folder, self.ref_data)
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        return {
            "accountTypes": aggregate_by_account_type(self.holdings),
            "taxTypes": aggregate_by_tax_type(self.holdings),
            "assetClasses": aggregate_by_asset_class(self.holdings),
            "equityRatio": get_equity_fixed_income_ratio(self.holdings),
            "geography": aggregate_by_geography(self.holdings),
            "geographyWeights": geography_weights(self.holdings),
            "sectors": self._format_sectors(),
            "topPositions": top_n_positions(self.holdings, 10),
            "positions": self._format_positions(),
            "owners": aggregate_by_owner(self.holdings),
            "brokerages": aggregate_by_brokerage(self.holdings)
        }
    
    def _format_sectors(self) -> Dict[str, Dict[str, float]]:
        sector_totals = aggregate_by_sector(self.holdings)
        sector_pcts = sector_weights(self.holdings)
        
        return {
            sector: {
                "value": value,
                "weight": sector_pcts.get(sector, 0.0)
            }
            for sector, value in sector_totals.items()
        }
    
    def _format_positions(self) -> Dict[str, list]:
        all_positions = total_positions(self.holdings)
        return {
            ticker: drilldown_positions(self.holdings, ticker)
            for ticker in all_positions.keys()
        }
    
    def export_dashboard_json(self, output_file: str):
        data = self.generate_dashboard_data()
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def get_position_summary(self, ticker: str) -> Dict[str, Any]:
        positions = drilldown_positions(self.holdings, ticker)
        if not positions:
            return {"error": f"No position found for {ticker}"}
        
        total_shares = sum(p["shares"] for p in positions)
        total_value = sum(p["market_value"] for p in positions)
        
        return {
            "ticker": ticker,
            "total_shares": total_shares,
            "total_value": total_value,
            "accounts": positions
        }

def create_portfolio_dashboard(ref_folder: str, positions_folder: str, output_file: str = "dashboard_data.json"):
    engine = PortfolioEngine(ref_folder, positions_folder)
    engine.export_dashboard_json(output_file)
    return engine