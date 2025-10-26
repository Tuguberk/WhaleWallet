#!/usr/bin/env python3
"""
Telegram Bot Helper - Multiple methods to get Chat ID
"""

import requests
import json

def get_bot_info(bot_token):
    """Get bot information"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url)
        data = response.json()
        
        if data["ok"]:
            bot_info = data["result"]
            print(f"Bot Name: {bot_info['first_name']}")
            print(f"Bot Username: @{bot_info['username']}")
            print(f"Bot ID: {bot_info['id']}")
            return bot_info
        else:
            print(f"Error getting bot info: {data.get('description', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def check_updates(bot_token):
    """Check for updates/messages"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        data = response.json()
        
        if data["ok"]:
            if data["result"]:
                print("\nFound messages:")
                for update in data["result"]:
                    if "message" in update:
                        message = update["message"]
                        chat = message["chat"]
                        chat_id = chat["id"]
                        chat_type = chat.get("type", "unknown")
                        name = chat.get("first_name", "")
                        username = chat.get("username", "")
                        
                        print(f"\nChat ID: {chat_id}")
                        print(f"Type: {chat_type}")
                        if name:
                            print(f"Name: {name}")
                        if username:
                            print(f"Username: @{username}")
                        
                        return chat_id
            else:
                print("\nNo messages found.")
                print("Please send a message to your bot first.")
                return None
        else:
            print(f"API Error: {data.get('description', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"Error checking updates: {e}")
        return None

def main():
    bot_token = "8309783593:AAFkOWkfJlmNJowcx5rMGxq4kBG5fKlqPww"
    
    print("🤖 Telegram Bot Helper")
    print("="*50)
    
    # Get bot info
    print("Getting bot information...")
    bot_info = get_bot_info(bot_token)
    
    if bot_info:
        print(f"\nDirect bot link: https://t.me/{bot_info['username']}")
        print(f"Or search for: @{bot_info['username']} in Telegram")
        
        # Check for messages
        print("\nChecking for messages...")
        chat_id = check_updates(bot_token)
        
        if chat_id:
            print(f"\n✅ SUCCESS! Your Chat ID: {chat_id}")
            print("\nUpdate your config.py:")
            print('"telegram": {')
            print('    "enabled": true,')
            print(f'    "bot_token": "{bot_token}",')
            print(f'    "chat_id": "{chat_id}"')
            print('}')
            
            # Test notification
            test_notification(bot_token, chat_id)
        else:
            print("\n❌ No chat ID found.")
            print("Please:")
            print("1. Open Telegram")
            print("2. Search for @YourBotUsername")
            print("3. Send a message to the bot")
            print("4. Run this script again")

def test_notification(bot_token, chat_id):
    """Test sending a message"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "✅ Telegram setup successful!\n\nYour crypto wallet tracker is now configured to send notifications to Telegram.",
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("\n✅ Test message sent successfully!")
        else:
            print(f"\n❌ Failed to send test message: {response.text}")
    except Exception as e:
        print(f"\n❌ Error sending test message: {e}")

if __name__ == "__main__":
    main()
