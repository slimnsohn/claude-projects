#!/usr/bin/env python3
"""
PNL Calculator for Kalshi trading data.
Analyzes trades, positions, and calculates comprehensive trading metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class PNLCalculator:
    """Calculate PNL and trading metrics from Kalshi data."""
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize with comprehensive trading data."""
        self.data = data
        self.orders_df = pd.DataFrame(data.get('orders', []))
        self.fills_df = pd.DataFrame(data.get('fills', []))
        self.positions_df = pd.DataFrame(data.get('positions', []))
        self.settlements_df = pd.DataFrame(data.get('settlements', []))
        self.transactions_df = pd.DataFrame(data.get('transactions', []))
        self.history_df = pd.DataFrame(data.get('account_history', []))
        
        # Process dataframes
        self._process_dataframes()
    
    def _process_dataframes(self):
        """Clean and process all dataframes."""
        # All dataframes to process
        dataframes = [
            (self.orders_df, 'orders'),
            (self.fills_df, 'fills'),
            (self.positions_df, 'positions'),
            (self.settlements_df, 'settlements'),
            (self.transactions_df, 'transactions'),
            (self.history_df, 'account_history')
        ]
        
        for df, df_name in dataframes:
            if not df.empty:
                # Convert timestamp columns
                timestamp_cols = ['created_at', 'timestamp', 'ts', 'settled_at', 'updated_at']
                for col in timestamp_cols:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                
                # Convert numeric columns
                numeric_cols = [
                    'price', 'count', 'size', 'payout', 'cost', 'amount',
                    'balance', 'settlement_amount', 'fee'
                ]
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Log processing summary
        record_counts = []
        for df, df_name in dataframes:
            record_counts.append(f"{len(df)} {df_name}")
        
        logger.info(f"Processed: {', '.join(record_counts)}")
    
    def calculate_trade_pnl(self) -> pd.DataFrame:
        """Calculate PNL for each trade."""
        if self.fills_df.empty:
            logger.warning("No fills data available for PNL calculation")
            return pd.DataFrame()
        
        trades = self.fills_df.copy()
        
        # Calculate basic PNL metrics
        if 'cost' in trades.columns and 'payout' in trades.columns:
            trades['gross_pnl'] = trades['payout'] - trades['cost']
        elif 'price' in trades.columns and 'size' in trades.columns:
            # Alternative calculation if cost/payout not available
            trades['gross_pnl'] = trades['price'] * trades['size']
        
        # Calculate fees (if available)
        if 'fees' in trades.columns:
            trades['net_pnl'] = trades['gross_pnl'] - trades['fees']
        else:
            trades['net_pnl'] = trades['gross_pnl']
        
        # Add win/loss classification
        trades['is_win'] = trades['net_pnl'] > 0
        trades['is_loss'] = trades['net_pnl'] < 0
        
        return trades
    
    def calculate_position_pnl(self) -> pd.DataFrame:
        """Calculate PNL by position/market."""
        trades = self.calculate_trade_pnl()
        if trades.empty:
            return pd.DataFrame()
        
        # Group by market or ticker
        groupby_col = 'ticker' if 'ticker' in trades.columns else 'market_ticker'
        if groupby_col not in trades.columns:
            logger.warning("No market identifier found for position analysis")
            return pd.DataFrame()
        
        position_pnl = trades.groupby(groupby_col).agg({
            'gross_pnl': ['sum', 'count', 'mean'],
            'net_pnl': ['sum', 'mean'],
            'is_win': 'sum',
            'is_loss': 'sum'
        }).round(4)
        
        # Flatten column names
        position_pnl.columns = ['_'.join(col).strip() for col in position_pnl.columns.values]
        
        # Calculate additional metrics
        position_pnl['total_trades'] = position_pnl['gross_pnl_count']
        position_pnl['win_rate'] = (position_pnl['is_win_sum'] / position_pnl['total_trades'] * 100).round(2)
        position_pnl['avg_win'] = trades[trades['is_win']].groupby(groupby_col)['net_pnl'].mean().fillna(0)
        position_pnl['avg_loss'] = trades[trades['is_loss']].groupby(groupby_col)['net_pnl'].mean().fillna(0)
        
        # Sort by total PNL
        position_pnl = position_pnl.sort_values('net_pnl_sum', ascending=False)
        
        return position_pnl.reset_index()
    
    def calculate_daily_pnl(self) -> pd.DataFrame:
        """Calculate daily PNL."""
        trades = self.calculate_trade_pnl()
        if trades.empty:
            return pd.DataFrame()
        
        # Find timestamp column
        timestamp_col = None
        for col in ['created_at', 'timestamp', 'ts']:
            if col in trades.columns:
                timestamp_col = col
                break
        
        if not timestamp_col:
            logger.warning("No timestamp column found for daily analysis")
            return pd.DataFrame()
        
        # Extract date
        trades['date'] = trades[timestamp_col].dt.date
        
        daily_pnl = trades.groupby('date').agg({
            'gross_pnl': 'sum',
            'net_pnl': 'sum',
            'is_win': 'sum',
            'is_loss': 'sum'
        }).round(4)
        
        daily_pnl['total_trades'] = daily_pnl['is_win'] + daily_pnl['is_loss']
        daily_pnl['win_rate'] = (daily_pnl['is_win'] / daily_pnl['total_trades'] * 100).round(2)
        daily_pnl['cumulative_pnl'] = daily_pnl['net_pnl'].cumsum()
        
        return daily_pnl.reset_index()
    
    def calculate_summary_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive trading metrics."""
        trades = self.calculate_trade_pnl()
        
        if trades.empty:
            return {
                'error': 'No trade data available for analysis',
                'total_trades': 0,
                'total_pnl': 0
            }
        
        # Basic metrics
        total_trades = len(trades)
        total_pnl = trades['net_pnl'].sum() if 'net_pnl' in trades.columns else 0
        gross_pnl = trades['gross_pnl'].sum() if 'gross_pnl' in trades.columns else 0
        
        # Win/Loss metrics
        wins = trades[trades['net_pnl'] > 0] if 'net_pnl' in trades.columns else pd.DataFrame()
        losses = trades[trades['net_pnl'] < 0] if 'net_pnl' in trades.columns else pd.DataFrame()
        
        win_count = len(wins)
        loss_count = len(losses)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0
        
        # Average win/loss
        avg_win = wins['net_pnl'].mean() if not wins.empty else 0
        avg_loss = losses['net_pnl'].mean() if not losses.empty else 0
        
        # Risk metrics
        profit_factor = abs(wins['net_pnl'].sum() / losses['net_pnl'].sum()) if not losses.empty and losses['net_pnl'].sum() != 0 else float('inf')
        
        # Drawdown calculation (simplified)
        daily_pnl = self.calculate_daily_pnl()
        max_drawdown = 0
        if not daily_pnl.empty and 'cumulative_pnl' in daily_pnl.columns:
            peak = daily_pnl['cumulative_pnl'].expanding().max()
            drawdown = (daily_pnl['cumulative_pnl'] - peak)
            max_drawdown = drawdown.min()
        
        # Time analysis
        first_trade = None
        last_trade = None
        trading_days = 0
        
        if not trades.empty:
            timestamp_col = None
            for col in ['created_at', 'timestamp', 'ts']:
                if col in trades.columns:
                    timestamp_col = col
                    break
            
            if timestamp_col:
                first_trade = trades[timestamp_col].min()
                last_trade = trades[timestamp_col].max()
                if first_trade and last_trade:
                    trading_days = (last_trade - first_trade).days
        
        return {
            'total_trades': total_trades,
            'total_pnl': round(total_pnl, 2),
            'gross_pnl': round(gross_pnl, 2),
            'win_count': win_count,
            'loss_count': loss_count,
            'win_rate': round(win_rate, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 'Infinite',
            'max_drawdown': round(max_drawdown, 2),
            'first_trade': first_trade.strftime('%Y-%m-%d') if first_trade else None,
            'last_trade': last_trade.strftime('%Y-%m-%d') if last_trade else None,
            'trading_days': trading_days,
            'avg_daily_pnl': round(total_pnl / max(trading_days, 1), 2) if trading_days > 0 else 0
        }
    
    def get_best_worst_trades(self, n: int = 5) -> Dict[str, pd.DataFrame]:
        """Get the best and worst trades."""
        trades = self.calculate_trade_pnl()
        if trades.empty:
            return {'best': pd.DataFrame(), 'worst': pd.DataFrame()}
        
        pnl_col = 'net_pnl' if 'net_pnl' in trades.columns else 'gross_pnl'
        
        # Get relevant columns for display
        display_cols = [pnl_col]
        if 'ticker' in trades.columns:
            display_cols.append('ticker')
        if 'market_ticker' in trades.columns:
            display_cols.append('market_ticker')
        
        # Add timestamp if available
        for col in ['created_at', 'timestamp', 'ts']:
            if col in trades.columns:
                display_cols.append(col)
                break
        
        best_trades = trades.nlargest(n, pnl_col)[display_cols]
        worst_trades = trades.nsmallest(n, pnl_col)[display_cols]
        
        return {'best': best_trades, 'worst': worst_trades}
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive trading report."""
        logger.info("Generating PNL report...")
        
        report = {
            'summary': self.calculate_summary_metrics(),
            'daily_pnl': self.calculate_daily_pnl().to_dict('records'),
            'position_pnl': self.calculate_position_pnl().to_dict('records'),
            'best_worst': {
                'best': self.get_best_worst_trades()['best'].to_dict('records'),
                'worst': self.get_best_worst_trades()['worst'].to_dict('records')
            },
            'generated_at': datetime.now().isoformat()
        }
        
        logger.info("PNL report generated successfully")
        return report


def main():
    """Test the PNL calculator with sample data."""
    from data_manager import DataManager
    
    dm = DataManager()
    data = dm.load_latest_data()
    
    if not data:
        print("No data found. Run fetch_data.py first.")
        return
    
    # Calculate PNL
    calc = PNLCalculator(data)
    report = calc.generate_report()
    
    # Display summary
    summary = report['summary']
    print("\n" + "="*50)
    print("TRADING PERFORMANCE SUMMARY")
    print("="*50)
    print(f"Total Trades: {summary['total_trades']}")
    print(f"Total PNL: ${summary['total_pnl']}")
    print(f"Win Rate: {summary['win_rate']}%")
    print(f"Average Win: ${summary['avg_win']}")
    print(f"Average Loss: ${summary['avg_loss']}")
    print(f"Profit Factor: {summary['profit_factor']}")
    print(f"Max Drawdown: ${summary['max_drawdown']}")
    print(f"Trading Period: {summary['first_trade']} to {summary['last_trade']}")
    
    # Save report
    import json
    with open('data/pnl_report.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nFull report saved to data/pnl_report.json")


if __name__ == "__main__":
    main()