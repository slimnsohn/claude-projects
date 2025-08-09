#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://api.elections.kalshi.com/v1"

EMAIL = os.getenv("KALSHI_EMAIL")
PASSWORD = os.getenv("KALSHI_PASSWORD")

if not EMAIL or not PASSWORD:
    print("ERROR: Please set KALSHI_EMAIL and KALSHI_PASSWORD in your .env file")
    exit(1)

def authenticate():
    url = f"{API_BASE}/login"
    payload = {
        "email": EMAIL,
        "password": PASSWORD,
    }
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        token = data.get("token")  # Assuming API returns JWT token here
        if not token:
            print("ERROR: Authentication response missing token")
            exit(1)
        return token
    except requests.RequestException as e:
        print(f"Authentication failed: {e}")
        exit(1)

def fetch_deposits(token, user_id, page_size=20, page_number=1):
    url = f"{API_BASE}/users/{user_id}/account/history"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    params = {
        "deposits": "true",
        "withdrawals": "false",
        "credits": "false",
        "page_size": page_size,
        "page_number": page_number,
    }
    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("account_history", [])
    except requests.RequestException as e:
        print(f"Failed fetching deposits: {e}")
        exit(1)

def main():
    token = authenticate()
    # You need to know your user_id. Sometimes returned at login or you can get it separately.
    # For now, put it manually or fetch it if your API supports.
    user_id = os.getenv("KALSHI_EMAIL")
    if not user_id:
        print("ERROR: Please set KALSHI_USER_ID in your .env

