import pandas as pd
import re
import os
from typing import List, Dict
from data_model import NormalizedHolding

def clean_currency_value(value_str: str) -> float:
    """Convert currency string like '$1,234.56' to float"""
    if pd.isna(value_str) or value_str == '' or value_str == '--':
        return 0.0
    
    # Remove currency symbols, commas, quotes, and spaces
    cleaned = str(value_str).replace('$', '').replace(',', '').replace('"', '').strip()
    
    # Handle parentheses as negative numbers
    if cleaned.startswith('(') and cleaned.endswith(')'):
        cleaned = '-' + cleaned[1:-1]
    
    try:
        return float(cleaned)
    except ValueError:
        return 0.0

def extract_account_id_from_text(text: str) -> str:
    """Extract account ID from text like 'Individual ...400' or 'Rollover_IRA ...423'"""
    # Look for ...XXX pattern
    match = re.search(r'\.\.\.(\d+)', str(text))
    if match:
        return match.group(1)
    return ''

def map_schwab_account_to_id(account_text: str) -> str:
    """Map Schwab account names to account IDs"""
    text = str(account_text).lower()
    if 'roth_contributory_ira' in text and '454' in text:
        return '454'
    elif 'individual' in text and '872' in text:
        return '872'
    elif 'rollover_ira' in text and '330' in text:
        return '330'
    elif 'individual' in text and '400' in text:
        return '400'
    elif 'rollover_ira' in text and '423' in text:
        return '423'
    elif 'roth_contributory_ira' in text and '858' in text:
        return '858'
    return ''

def classify_asset_class(symbol: str, security_type: str = '') -> str:
    """Classify asset based on symbol and security type"""
    symbol = str(symbol).upper()
    security_type = str(security_type).lower()
    
    # Cash equivalents
    if any(cash_indicator in symbol for cash_indicator in ['CASH', 'VMFXX', 'FDRXX']):
        return 'cash'
    
    # Bond funds
    bond_indicators = ['VBILX', 'FXNAX', 'BND', 'AGG', 'VTEB', 'VGIT', 'VGLT']
    if any(bond in symbol for bond in bond_indicators):
        return 'fixed_income'
    
    # ETFs and mutual funds are typically equity unless specified otherwise
    if 'etf' in security_type or 'fund' in security_type:
        return 'equity'
    
    # Default to equity for individual stocks
    return 'equity'

def parse_schwab_csv(file_path: str) -> List[Dict]:
    """Parse Schwab CSV format"""
    holdings = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    current_account_id = ''
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Check if this line contains an account header
        line_clean = line.replace('"', '').strip()
        
        # Try to extract account ID from patterns like "Individual ...400" or "Rollover_IRA ...423"
        account_match = extract_account_id_from_text(line_clean)
        if account_match:
            current_account_id = account_match
            continue
        
        # Try mapping schwab account names
        schwab_account_id = map_schwab_account_to_id(line_clean)
        if schwab_account_id:
            current_account_id = schwab_account_id
            continue
        
        # Skip header lines
        if 'Symbol,Description,Qty' in line:
            continue
        
        # Skip total and cash lines
        if any(skip_term in line for skip_term in ['Account Total', 'Cash & Cash Investments']):
            continue
            
        # Process data lines
        parts = [p.replace('"', '').strip() for p in line.split(',')]
        if len(parts) >= 15 and parts[0] and parts[0] not in ['Symbol', 'Account Total', '']:
            try:
                symbol = parts[0]
                shares = clean_currency_value(parts[2])
                market_value = clean_currency_value(parts[6])
                security_type = parts[14] if len(parts) > 14 else ''
                
                if symbol and shares > 0 and current_account_id:
                    holdings.append({
                        'account_id': current_account_id,
                        'symbol': symbol,
                        'shares': shares,
                        'market_value': 0.0,  # Will be calculated from real-time prices
                        'asset_class': classify_asset_class(symbol, security_type)
                    })
            except (ValueError, IndexError):
                continue
    
    return holdings

def parse_fidelity_csv(file_path: str) -> List[Dict]:
    """Parse Fidelity CSV format"""
    df = pd.read_csv(file_path, encoding='utf-8')
    holdings = []
    
    for _, row in df.iterrows():
        account_id = str(row.get('Account Number', ''))
        account_name = str(row.get('Account Name', ''))
        symbol = str(row.get('Symbol', ''))
        shares = clean_currency_value(row.get('Quantity', 0))
        
        # Skip empty rows
        if not symbol or symbol == 'nan' or not account_id or account_id == 'nan':
            continue
        
        # Map Fidelity account numbers to unique IDs (include owner to avoid collisions)
        # Both Sammy and Nalae have account 52719 at Fidelity but different account names
        if account_id == '52719':
            if 'MILLENNIUM' in account_name.upper():
                account_id = '719'  # Sammy's Fidelity 401k
                account_name = "Sammy Fidelity 401k"
            elif 'LG' in account_name.upper():
                account_id = '720'  # Nalae's Fidelity 401k (unique ID)  
                account_name = "Nalae Fidelity 401k"
            else:
                account_id = '719'  # Default fallback
        elif account_id == '237980409':
            # This might be a different account, skip for now
            continue
        
        # Calculate market value - try multiple columns
        market_value = 0
        
        # Try Current Value first (full format)
        market_value = clean_currency_value(row.get('Current Value', 0))
        
        # If not found, try calculating from Last Price and Quantity (simple format)
        if market_value == 0:
            price = clean_currency_value(row.get('Last Price', 0))
            if price > 0 and shares > 0:
                market_value = price * shares
        
        # For simple format without prices, estimate based on known fund prices
        if market_value == 0 and shares > 0:
            # Rough estimates for common funds (you can update these)
            rough_prices = {
                'VOO': 450,  # S&P 500 ETF
                'VSORX': 25,  # Real Estate
                'FXNAX': 10   # Bond fund
            }
            if symbol in rough_prices:
                market_value = shares * rough_prices[symbol]
        
        if symbol and shares > 0:
            holdings.append({
                'account_id': account_id,
                'account_name': account_name,  # Include the updated account name
                'symbol': symbol,
                'shares': shares,
                'market_value': 0.0,  # Will be calculated from real-time prices
                'asset_class': classify_asset_class(symbol)
            })
    
    return holdings

def parse_vanguard_csv(file_path: str) -> List[Dict]:
    """Parse Vanguard CSV format"""
    df = pd.read_csv(file_path, encoding='utf-8')
    holdings = []
    
    for _, row in df.iterrows():
        account_id = str(row.get('Account Number', ''))
        symbol = str(row.get('Symbol', ''))
        shares = clean_currency_value(row.get('Shares', 0))
        market_value = clean_currency_value(row.get('Total Value', 0))
        
        # Remove 'x' prefix from Vanguard account IDs
        if account_id.startswith('x'):
            account_id = account_id[1:]
        
        if symbol and shares > 0 and account_id:
            holdings.append({
                'account_id': account_id,
                'symbol': symbol,
                'shares': shares,
                'market_value': 0.0,  # Will be calculated from real-time prices
                'asset_class': classify_asset_class(symbol)
            })
    
    return holdings

def extract_owner_and_brokerage_from_filename(filename: str) -> tuple[str, str]:
    """Extract owner and brokerage from filename"""
    filename_lower = filename.lower()
    
    # Extract owner
    owner = "Unknown"
    if filename_lower.startswith('ss_') or 'sammy' in filename_lower:
        owner = "Sammy"
    elif filename_lower.startswith('nk') or 'nalae' in filename_lower:
        owner = "Nalae"
    elif 'vanguard' in filename_lower:
        # Vanguard accounts belong to Sammy based on account numbers
        owner = "Sammy"
    
    # Extract brokerage
    brokerage = "Unknown"
    if 'schwab' in filename_lower:
        brokerage = "Schwab"
    elif 'fidelity' in filename_lower:
        brokerage = "Fidelity"
    elif 'vanguard' in filename_lower:
        brokerage = "Vanguard"
    
    return owner, brokerage

def parse_all_portfolio_csvs(folder_path: str, ref_data: Dict[str, Dict[str, str]]) -> List[NormalizedHolding]:
    """Parse all CSV files in the folder and return normalized holdings"""
    all_holdings = []
    
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV files: {csv_files}")
    
    for filename in csv_files:
        file_path = os.path.join(folder_path, filename)
        print(f"\nProcessing {filename}...")
        
        # Extract owner and brokerage from filename
        owner, brokerage = extract_owner_and_brokerage_from_filename(filename)
        print(f"  Detected - Owner: {owner}, Brokerage: {brokerage}")
        
        try:
            holdings = []
            
            # Try all parsers to handle different formats
            if 'schwab' in filename.lower():
                holdings = parse_schwab_csv(file_path)
            elif 'fidelity' in filename.lower():
                holdings = parse_fidelity_csv(file_path)
            elif 'vanguard' in filename.lower():
                holdings = parse_vanguard_csv(file_path)
            else:
                # Try to auto-detect format by trying each parser
                print(f"  Unknown filename format, trying auto-detection...")
                for parser_name, parser_func in [
                    ("Schwab", parse_schwab_csv),
                    ("Fidelity", parse_fidelity_csv), 
                    ("Vanguard", parse_vanguard_csv)
                ]:
                    try:
                        holdings = parser_func(file_path)
                        if holdings:
                            print(f"  Successfully parsed with {parser_name} parser")
                            if brokerage == "Unknown":
                                brokerage = parser_name
                            break
                    except Exception as e:
                        continue
                
                if not holdings:
                    print(f"  Could not parse {filename} with any parser")
                    continue
            
            print(f"  Found {len(holdings)} holdings")
            
            # Convert to NormalizedHolding objects
            for holding in holdings:
                account_id = holding['account_id']
                account_info = ref_data.get(account_id, {})
                
                # If no account info found, still create holding but mark as unknown
                if not account_info:
                    print(f"    Warning: No account info found for account_id '{account_id}'")
                
                # Use account name from holding if available (for cases like Fidelity splits)
                # Otherwise fall back to ref_data lookup
                account_name = holding.get('account_name') or account_info.get('account_name', f'Account {account_id}')
                
                normalized = NormalizedHolding(
                    account_id=account_id,
                    account_name=account_name,
                    ticker=holding['symbol'],
                    shares=holding['shares'],
                    market_value=0.0,  # Will be calculated from real-time prices
                    account_type=account_info.get('account_type', 'unknown'),
                    tax_type=account_info.get('tax_type', 'unknown'),
                    asset_class=holding['asset_class'],
                    owner=owner,
                    brokerage=brokerage
                )
                all_holdings.append(normalized)
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\nTotal holdings parsed: {len(all_holdings)}")
    return all_holdings