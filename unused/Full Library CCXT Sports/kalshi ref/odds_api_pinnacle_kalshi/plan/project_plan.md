# Pinnacle-Kalshi Mispricing Detection System - Project Plan

## Phase 1: Project Foundation & Setup
### 1.1 Directory Structure Setup
- [x] Create `prod_ready/` folder for stable production modules
- [x] Create `tests/` folder for unit tests and validation
- [x] Create `debug/` folder for temporary/debug code  
- [x] Create `plan/` folder for design notes and checklists
- [x] Create `keys/` folder for API credentials (not version controlled)

### 1.2 Data Schema Design
- [ ] Define normalized odds schema structure
- [ ] Document required fields: game_date, game_time, home_team, away_team, home_odds, away_odds
- [ ] Create schema validation utilities
- [ ] Document odds conversion formulas and fee adjustments

## Phase 2: Pinnacle API Integration Module
### 2.1 Pinnacle Data Ingestion
- [ ] Create `pinnacle_client.py` in debug folder
- [ ] Implement OddsAPI connection for Pinnacle sportsbook
- [ ] Filter for MLB moneyline markets only
- [ ] Parse and normalize Pinnacle response format
- [ ] Handle API rate limiting and error responses

### 2.2 Pinnacle Testing & Validation
- [ ] Create unit tests for Pinnacle client
- [ ] Validate data format and completeness
- [ ] Test error handling scenarios
- [ ] Move stable version to `prod_ready/`

## Phase 3: Kalshi API Integration Module  
### 3.1 Kalshi Data Ingestion
- [ ] Create `kalshi_client.py` in debug folder
- [ ] Implement Kalshi API connection for MLB markets
- [ ] Parse Kalshi market data and extract relevant games
- [ ] Normalize Kalshi response to match schema
- [ ] Handle Kalshi-specific data structures

### 3.2 Kalshi Testing & Validation
- [ ] Create unit tests for Kalshi client
- [ ] Validate market data extraction
- [ ] Test API authentication and error handling
- [ ] Move stable version to `prod_ready/`

## Phase 4: Odds Conversion & Utilities
### 4.1 Conversion Logic Implementation
- [ ] Create `odds_converter.py` utility module
- [ ] Implement percentage to American odds conversion
- [ ] Add Kalshi fee adjustments to conversion calculations
- [ ] Validate conversion examples:
  - 40% = +140
  - 45% = +114  
  - 50% = -107
  - 70% = -262
  - 85% = -606
  - 95% = -2396

### 4.2 Conversion Testing
- [ ] Unit tests for all conversion scenarios
- [ ] Edge case testing (very high/low percentages)
- [ ] Fee adjustment validation
- [ ] Move to `prod_ready/` when validated

## Phase 5: Data Integration & Comparison
### 5.1 Data Alignment Module
- [ ] Create `data_aligner.py` for matching games across platforms
- [ ] Implement team name normalization/mapping
- [ ] Handle time zone differences and game scheduling
- [ ] Create unified data structure for comparison

### 5.2 Mispricing Detection Logic
- [ ] Create `mispricing_detector.py` for opportunity identification
- [ ] Define threshold parameters for significant discrepancies
- [ ] Calculate expected value and profit margins
- [ ] Generate actionable mispricing alerts

## Phase 6: Integration Testing & Production Readiness
### 6.1 End-to-End Testing
- [ ] Integration tests with live API data
- [ ] Validate complete data flow: fetch → normalize → compare → detect
- [ ] Performance testing and optimization
- [ ] Error handling for API failures

### 6.2 Production Deployment
- [ ] Move all validated modules to `prod_ready/`
- [ ] Create main orchestration script
- [ ] Documentation for production usage
- [ ] Setup logging and monitoring

## Required API Keys
Please provide the following files in the `keys/` folder:
- `odds_api_key.txt` - OddsAPI key for Pinnacle data
- `kalshi_credentials.txt` - Kalshi API credentials (format: username:password or API key)

## Success Criteria
- Both APIs successfully fetched and parsed
- Odds conversion working with provided test cases
- Game matching between platforms functional
- Clear mispricing opportunities identified
- All code modules in `prod_ready/` folder tested and stable

## Current Status
- **Phase 1**: Ready to begin
- **Next Step**: Create directory structure and begin Pinnacle API module