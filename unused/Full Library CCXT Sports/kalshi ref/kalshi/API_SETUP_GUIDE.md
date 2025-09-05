# Kalshi API Setup Guide

## Overview
This guide will help you set up and test your Kalshi API integration. The API setup has been updated to use the official `kalshi-python` library with the correct endpoints.

## What Was Fixed

### Issues Found and Resolved:
1. **Wrong API Endpoint**: Updated from `https://api.elections.kalshi.com/v1` to `https://api.elections.kalshi.com/trade-api/v2`
2. **Outdated Library Usage**: Switched from manual HTTP requests to the official `kalshi-python` library
3. **Unicode Encoding**: Fixed Unicode character issues on Windows
4. **Missing Dependencies**: Ensured all required packages are properly installed

### Key Changes:
- Updated `kalshi_client.py` to use the official Kalshi Python SDK
- Fixed API endpoints to use Trade API v2
- Removed Unicode characters that caused Windows encoding issues
- Added proper error handling with detailed API exceptions

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test API Configuration
Run the test script to verify everything is working:
```bash
python test_api_setup.py
```

You should see:
```
============================================================
KALSHI API SETUP TEST
============================================================

[OK] kalshi-python library imported successfully
[OK] API configuration created: https://api.elections.kalshi.com/trade-api/v2
[OK] API client created successfully
[OK] Auth API instantiated
[OK] Portfolio API instantiated
[OK] Exchange API instantiated

SUCCESS: ALL TESTS PASSED!
```

### 3. Set Up Your Credentials
Run the credential setup script:
```bash
python setup_credentials.py
```

This will:
- Prompt you for your Kalshi email and password
- Create a secure `.env` file with your credentials
- Provide next steps for testing

### 4. Test Authentication
After setting up credentials, test the connection:
```bash
python kalshi_client.py
```

With valid credentials, you should see:
```
2025-08-17 15:20:16,827 - INFO - Starting authentication...
2025-08-17 15:20:16,982 - INFO - Authentication successful!
2025-08-17 15:20:16,984 - INFO - Starting comprehensive data fetch...
```

### 5. Fetch Your Trading Data
Run the data fetcher:
```bash
python fetch_data.py
```

## File Structure

- `kalshi_client.py` - Main API client (FIXED)
- `test_api_setup.py` - Test script to verify setup (NEW)
- `setup_credentials.py` - Interactive credential setup (NEW)
- `fetch_data.py` - Data fetching script
- `data_manager.py` - Data storage and export utilities
- `.env.template` - Template for environment variables (NEW)
- `.env` - Your actual credentials (created by setup script)

## API Endpoints Used

The client now uses the correct Kalshi Trade API v2 endpoints:
- **Base URL**: `https://api.elections.kalshi.com/trade-api/v2`
- **Authentication**: `/login` (POST with email/password)
- **Portfolio Data**: Various `/portfolio/*` endpoints
- **Exchange Status**: Public endpoint for connectivity testing

## Troubleshooting

### Common Issues:

1. **401 Unauthorized**
   - Check your email and password in `.env`
   - Verify your Kalshi account is active

2. **404 Not Found**
   - API endpoint has been updated, ensure you're using the latest code

3. **400 Bad Request**
   - Usually means invalid credentials format
   - Run `python setup_credentials.py` to recreate `.env`

4. **Unicode Errors**
   - All Unicode characters have been removed from the codebase
   - If you still see issues, check your terminal encoding

### Test Commands:

```bash
# Test basic setup
python test_api_setup.py

# Test with placeholder credentials (should get 400 error)
python kalshi_client.py

# Set up real credentials
python setup_credentials.py

# Test with real credentials
python kalshi_client.py

# Fetch all your data
python fetch_data.py
```

## Security Notes

- Your `.env` file contains sensitive credentials
- Never commit `.env` to version control
- The `.env` file is already in `.gitignore`
- Use different credentials for testing vs production

## Next Steps

1. **Test the setup** with your actual Kalshi credentials
2. **Run data fetch** to get your trading history
3. **Explore the dashboard** to view your data
4. **Set up automated fetching** if needed

The API client is now properly configured and should work with current Kalshi API endpoints.