#!/usr/bin/env python3
"""
Test script for detailed position notifications
"""

from wallet_tracker import WalletTracker
from notification_system import NotificationSystem
from utils import load_config

def test_position_notification():
    # Load configuration
    config = load_config()
    
    # Initialize tracker and notification system
    tracker = WalletTracker(
        config["wallet_address"], 
        config["etherscan_api_key"]
    )
    notifier = NotificationSystem(config["notification_settings"])
    
    # Get current positions
    print("📊 Getting current positions...")
    positions = tracker.get_hyperliquid_positions()
    
    if positions:
        print("✅ Positions retrieved successfully!")
        
        # Format and display detailed position notification (test with "position_changed" type)
        message = notifier.format_position_change(positions, "position_changed")
        print("\n" + "="*50)
        print("DETAILED POSITION NOTIFICATION:")
        print("="*50)
        print(message)
        
        # Send notification to Telegram
        print("\n📱 Sending to Telegram...")
        notifier.send_notification(message, "POSITION CHANGED")
        
        print("\n✅ Test completed!")
    else:
        print("❌ Failed to retrieve positions")

if __name__ == "__main__":
    test_position_notification()
