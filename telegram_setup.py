#!/usr/bin/env python3
"""
Telegram Bot Kurulum Yardımcısı
Bu script ile chat_id'nizi kolayca öğrenebilirsiniz
"""

import requests
import time

def get_chat_id(bot_token: str) -> str:
    """Botunuzun chat_id'sini almak için yardımcı fonksiyon"""
    try:
        # 1. Botunuza bir mesaj gönderin
        print(f"1. Lütfen botunuza bir mesaj gönderin: https://t.me/{bot_token.split(':')[0]}")
        print("2. Herhangi bir mesaj gönderin (örn: /start)")
        input("Mesaj gönderdikten sonra Enter tuşuna basın...")
        
        # 2. Son mesajları al
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        data = response.json()
        
        if data["ok"]:
            if data["result"]:
                # Son mesajın chat_id'sini al
                last_message = data["result"][-1]
                chat_id = last_message["message"]["chat"]["id"]
                print(f"✅ Chat ID'niz: {chat_id}")
                return str(chat_id)
            else:
                print("❌ Henüz mesaj bulunamadı. Lütfen botunuza bir mesaj gönderin.")
                return None
        else:
            print(f"❌ Hata: {data.get('description', 'Bilinmeyen hata')}")
            return None
            
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        return None

def test_telegram_notification(bot_token: str, chat_id: str) -> bool:
    """Telegram bildirimini test etmek için fonksiyon"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": "🔔 Kripto Cüzdan Takip Sistemi Test Mesajı\n\nBotunuz başarıyla çalışıyor!",
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("✅ Test mesajı başarıyla gönderildi!")
            return True
        else:
            print(f"❌ Mesaj gönderilemedi: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
        return False

def main():
    print("🤖 Telegram Bot Kurulum Yardımcısı")
    print("="*50)
    
    # Bot token'ı al
    bot_token = input("BotFather'dan aldığınız Bot Token'ı girin: ").strip()
    
    if not bot_token:
        print("❌ Bot Token boş olamaz!")
        return
    
    # Chat ID al
    chat_id = get_chat_id(bot_token)
    
    if chat_id:
        # Test mesajı gönder
        print("\n3. Test mesajı gönderiliyor...")
        test_telegram_notification(bot_token, chat_id)
        
        print("\n✅ Kurulum tamamlandı!")
        print(f"📝 .env dosyasına ekleyin:")
        print(f"TELEGRAM_ENABLED=true")
        print(f"TELEGRAM_BOT_TOKEN={bot_token}")
        print(f"TELEGRAM_CHAT_ID={chat_id}")

if __name__ == "__main__":
    main()
