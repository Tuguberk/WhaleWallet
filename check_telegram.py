#!/usr/bin/env python3
"""
Check Telegram for chat ID without interactive input
"""

import requests

def check_messages():
    """Check for messages and get chat_id"""
    bot_token = "8309783593:AAFkOWkfJlmNJowcx5rMGxq4kBG5fKlqPww"
    
    print("🤖 Checking for Telegram messages...")
    print(f"Bot link: https://t.me/{bot_token.split(':')[0]}")
    print()
    print("Please:")
    print("1. Click the link above")
    print("2. Send a message to the bot (any message)")
    print("3. Run this script again to get your Chat ID")
    print()
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        data = response.json()
        
        if data["ok"]:
            if data["result"]:
                print("📬 Messages found:")
                for msg in data["result"]:
                    if "message" in msg:
                        chat_id = msg["message"]["chat"]["id"]
                        chat_info = msg["message"]["chat"]
                        
                        # Display chat info
                        chat_type = chat_info.get("type", "unknown")
                        first_name = chat_info.get("first_name", "")
                        username = chat_info.get("username", "")
                        
                        print(f"  Chat ID: {chat_id}")
                        print(f"  Type: {chat_type}")
                        if first_name:
                            print(f"  Name: {first_name}")
                        if username:
                            print(f"  Username: @{username}")
                        print()
                
                last_message = data["result"][-1]
                chat_id = last_message["message"]["chat"]["id"]
                
                print(f"✅ Use this Chat ID: {chat_id}")
                print()
                print("Update your config.py telegram section:")
                print('"telegram": {')
                print('    "enabled": true,')
                print(f'    "bot_token": "{bot_token}",')
                print(f'    "chat_id": "{chat_id}"')
                print('}')
                return chat_id
            else:
                print("❌ No messages found. Please send a message to the bot first.")
                return None
        else:
            print(f"❌ API Error: {data.get('description', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return None

if __name__ == "__main__":
    check_messages()
