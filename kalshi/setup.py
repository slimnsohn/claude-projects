#!/usr/bin/env python3
"""
Setup script for Kalshi PNL Analysis Tool.
Run this to install dependencies and set up the environment.
"""

import os
import sys
import subprocess
import shutil

def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("Kalshi PNL Analysis Tool - Setup")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Error: Python 3.8+ required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("Failed to install dependencies. Try running manually:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        shutil.copy('.env.example', '.env')
        print("✓ Created .env file from template")
        print("⚠️  IMPORTANT: Edit .env file with your Kalshi credentials before running fetch_data.py")
    else:
        print("✓ .env file already exists")
    
    # Create data directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('exports', exist_ok=True)
    print("✓ Created data and exports directories")
    
    print("\n" + "=" * 40)
    print("Setup Complete!")
    print("=" * 40)
    print("\nNext steps:")
    print("1. Edit .env file with your Kalshi API credentials:")
    print("   - Get API key from your Kalshi account settings")
    print("   - OR use email/password")
    print()
    print("2. Fetch your trading data:")
    print("   python fetch_data.py")
    print()
    print("3. Open the web dashboard:")
    print("   python -m http.server 8000")
    print("   Then visit http://localhost:8000/dashboard.html")
    print()

if __name__ == "__main__":
    main()