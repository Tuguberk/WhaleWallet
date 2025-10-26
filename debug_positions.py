#!/usr/bin/env python3
"""
Debug script to check Hyperliquid position data structure
"""

import requests
import json
from utils import load_config

def debug_positions():
    # Load configuration
    config = load_config()
    wallet_address = config["wallet_address"]
    
    # Get position data
    url = "https://api.hyperliquid.xyz/info"
    payload = {
        "type": "clearinghouseState",
        "user": wallet_address
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        
        print("Hyperliquid API Response Structure:")
        print("="*50)
        print(json.dumps(data, indent=2, default=str))
        
        # Check for positions
        if "assetPositions" in data:
            print("\n\nAsset Positions:")
            print("="*50)
            positions = data["assetPositions"]
            print(f"Number of positions: {len(positions)}")
            
            for i, pos in enumerate(positions):
                print(f"\nPosition {i+1}:")
                print(json.dumps(pos, indent=2, default=str))
        else:
            print("\nNo 'assetPositions' found in response")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_positions()
