#!/usr/bin/env python3
"""
Get Telegram Chat ID using the bot token from config
"""

import requests

def get_chat_id(bot_token: str) -> str:
    """Get chat_id from bot messages"""
    try:
        # 1. Instructions for user
        print(f"1. Open this link in your browser: https://t.me/{bot_token.split(':')[0]}")
        print("2. Send any message to the bot (e.g., /start or hello)")
        print("3. After sending the message, press Enter here...")
        input("Press Enter after sending the message to the bot...")
        
        # 2. Get recent messages
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        data = response.json()
        
        if data["ok"]:
            if data["result"]:
                # Get chat_id from last message
                last_message = data["result"][-1]
                chat_id = last_message["message"]["chat"]["id"]
                print(f"✅ Your Chat ID: {chat_id}")
                return str(chat_id)
            else:
                print("❌ No messages found yet. Please send a message to your bot first.")
                return None
        else:
            print(f"❌ Error: {data.get('description', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return None

def test_telegram_notification(bot_token: str, chat_id: str) -> bool:
    """Test telegram notification"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "🔔 Crypto Wallet Tracker Test Message\n\nYour bot is working correctly!",
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Test message sent successfully!")
            return True
        else:
            print(f"❌ Failed to send message: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return False

def main():
    print("🤖 Getting Telegram Chat ID")
    print("="*50)
    
    # Bot token from config
    bot_token = "8309783593:AAFkOWkfJlmNJowcx5rMGxq4kBG5fKlqPww"
    
    # Get chat ID
    chat_id = get_chat_id(bot_token)
    
    if chat_id:
        # Send test message
        print("\n3. Sending test message...")
        test_telegram_notification(bot_token, chat_id)
        
        print("\n✅ Setup complete!")
        print(f"📝 Update your config.py with:")
        print(f'"telegram": {{')
        print(f'    "enabled": true,')
        print(f'    "bot_token": "{bot_token}",')
        print(f'    "chat_id": "{chat_id}"')
        print(f'}}')

if __name__ == "__main__":
    main()
