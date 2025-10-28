#!/usr/bin/env python3
"""
Telegram Bot Manager
Handles bot commands and manages subscribers
"""

import json
import os
from typing import Set, Dict, Any
import threading
import time
import requests

class TelegramBotManager:
    def __init__(self, bot_token: str, subscribers_file: str = None):
        self.bot_token = bot_token
        # Check environment variable first, then use parameter, finally fallback to default
        self.subscribers_file = (
            os.getenv('SUBSCRIBERS_FILE') or 
            subscribers_file or 
            "subscribers.json"
        )
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.subscribers_file) if os.path.dirname(self.subscribers_file) else '.', exist_ok=True)
        self.subscribers: Set[int] = self._load_subscribers()
        self.last_update_id = 0
        self.running = False
        self.thread = None
        self.wallets = {}  # Will be set by external code
        self.on_new_subscriber = None  # Callback function for new subscribers
        self.on_analysis_request = None  # Callback function for analysis requests
        self.api_base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def _load_subscribers(self) -> Set[int]:
        """Load subscribers from JSON file"""
        if os.path.exists(self.subscribers_file):
            try:
                with open(self.subscribers_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('subscribers', []))
            except Exception as e:
                print(f"⚠️  Error loading subscribers: {e}")
                return set()
        return set()
    
    def _save_subscribers(self):
        """Save subscribers to JSON file"""
        try:
            with open(self.subscribers_file, 'w') as f:
                json.dump({
                    'subscribers': list(self.subscribers),
                    'updated_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving subscribers: {e}")
    
    def add_subscriber(self, chat_id: int) -> bool:
        """Add a new subscriber"""
        if chat_id not in self.subscribers:
            self.subscribers.add(chat_id)
            self._save_subscribers()
            print(f"✅ New subscriber added: {chat_id}")
            return True
        return False
    
    def remove_subscriber(self, chat_id: int) -> bool:
        """Remove a subscriber"""
        if chat_id in self.subscribers:
            self.subscribers.remove(chat_id)
            self._save_subscribers()
            print(f"❌ Subscriber removed: {chat_id}")
            return True
        return False
    
    def get_subscribers(self) -> Set[int]:
        """Get all active subscribers"""
        return self.subscribers.copy()
    
    def get_subscriber_count(self) -> int:
        """Get number of active subscribers"""
        return len(self.subscribers)
    
    def _is_user_admin(self, chat_id: int, user_id: int) -> bool:
        """Check if user is admin in a group/supergroup/channel"""
        try:
            response = requests.get(
                f"{self.api_base_url}/getChatMember",
                params={
                    'chat_id': chat_id,
                    'user_id': user_id
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    status = data.get('result', {}).get('status', '')
                    # Admin, creator or anonymous admin
                    return status in ['creator', 'administrator']
            
            return False
            
        except Exception as e:
            print(f"⚠️  Error checking admin status: {e}")
            return False
    
    def _check_permission(self, chat_id: int, user_id: int, chat_type: str, username: str = None, command: str = None) -> tuple[bool, str]:
        """
        Check if user has permission to use bot commands
        Returns: (has_permission: bool, error_message: str)
        
        Permission levels:
        - Private chats: All commands allowed
        - Group chats:
          * Admin-only: /start, /stop (subscription management)
          * Public: /analysis, /info, /status, /wallets, /help (information commands)
        """
        # Private chats: always allow
        if chat_type == 'private':
            return True, None
        
        # Define admin-only commands
        admin_only_commands = ['/start', '/stop']
        
        # Check if command requires admin permission
        requires_admin = False
        if command:
            for admin_cmd in admin_only_commands:
                if command.startswith(admin_cmd):
                    requires_admin = True
                    break
        
        # If command doesn't require admin, allow for everyone in groups
        if not requires_admin:
            return True, None
        
        # For admin-only commands, check if user is admin
        is_admin = self._is_user_admin(chat_id, user_id)
        
        if not is_admin:
            user_mention = f"@{username}" if username else f"User {user_id}"
            error_msg = (
                f"🔒 <b>Admin Permission Required</b>\n\n"
                f"Sorry {user_mention}, only group admins can use this command.\n\n"
                f"<b>Admin Commands:</b> /start, /stop\n"
                f"<b>Public Commands:</b> /analysis, /info, /status, /wallets, /help\n\n"
                f"<i>Contact a group admin to manage subscriptions.</i>"
            )
            return False, error_msg
        
        return True, None
    
    def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """Send message to a specific chat"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"⚠️  Error sending message to {chat_id}: {e}")
            return False
    
    def broadcast_message(self, text: str, parse_mode: str = "HTML") -> Dict[str, int]:
        """Broadcast message to all subscribers"""
        results = {"success": 0, "failed": 0, "total": len(self.subscribers)}
        
        for chat_id in self.subscribers.copy():
            if self.send_message(chat_id, text, parse_mode):
                results["success"] += 1
            else:
                results["failed"] += 1
                # Don't remove failed sends immediately - might be temporary issue
        
        return results
    
    def _get_updates(self, offset: int = 0) -> Dict[str, Any]:
        """Get updates from Telegram API"""
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
            params = {
                "offset": offset,
                "timeout": 30,
                "allowed_updates": ["message"]
            }
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            print(f"⚠️  Error getting updates: {e}")
            return {}
    
    def _process_update(self, update: Dict[str, Any]):
        """Process a single update"""
        try:
            message = update.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '')
            chat_type = message.get('chat', {}).get('type', 'private')
            chat_title = message.get('chat', {}).get('title', 'Private Chat')
            user_id = message.get('from', {}).get('id')
            username = message.get('from', {}).get('username', 'Unknown')
            
            if not chat_id or not text:
                return
            
            # Check if user has permission (pass command for permission level check)
            has_permission, error_msg = self._check_permission(chat_id, user_id, chat_type, username, text)
            if not has_permission:
                self.send_message(chat_id, error_msg)
                # Log unauthorized attempt
                if chat_type != 'private':
                    print(f"🚫 Unauthorized admin command attempt by @{username} (ID: {user_id}) in {chat_title} (ID: {chat_id}): {text.split()[0]}")
                return
            
            # Handle /start command
            if text.startswith('/start'):
                is_new = self.add_subscriber(chat_id)
                if is_new:
                    welcome_msg = (
                        f"🐋 <b>Welcome to WhaleWallet Tracker!</b>\n\n"
                        f"✅ You are now subscribed to wallet updates.\n\n"
                        f"📊 You will receive notifications for:\n"
                        f"• Balance changes\n"
                        f"• Position updates\n"
                        f"• Deposits & Withdrawals\n"
                        f"• Trading activity\n\n"
                        f"Use /stop to unsubscribe anytime."
                    )
                    self.send_message(chat_id, welcome_msg)
                    
                    # Log subscription info
                    if chat_type == 'private':
                        print(f"📱 New subscription from @{username} (ID: {chat_id})")
                    else:
                        print(f"👥 New group subscription: {chat_title} (ID: {chat_id})")
                    
                    # Send wallet analysis to new subscriber
                    if self.on_new_subscriber:
                        try:
                            self.on_new_subscriber(chat_id)
                        except Exception as e:
                            print(f"⚠️  Error sending initial analysis to {chat_id}: {e}")
                else:
                    self.send_message(
                        chat_id,
                        "✅ You are already subscribed to updates!"
                    )
            
            # Handle /stop command
            elif text.startswith('/stop'):
                if self.remove_subscriber(chat_id):
                    self.send_message(
                        chat_id,
                        "👋 You have been unsubscribed. Use /start to subscribe again."
                    )
                else:
                    self.send_message(
                        chat_id,
                        "⚠️  You are not subscribed."
                    )
            
            # Handle /status command
            elif text.startswith('/status'):
                if chat_id in self.subscribers:
                    # Get subscriber info
                    chat_type_emoji = "👤" if chat_type == "private" else "👥"
                    chat_name = chat_title if chat_type != "private" else f"@{username}"
                    
                    status_msg = (
                        f"📊 <b>Subscription Status</b>\n\n"
                        f"{chat_type_emoji} <b>Subscriber:</b> {chat_name}\n"
                        f"🆔 <b>Chat ID:</b> <code>{chat_id}</code>\n"
                        f"✅ <b>Status:</b> Active\n"
                        f"👥 <b>Total Subscribers:</b> {self.get_subscriber_count()}\n"
                        f"🔔 <b>Notifications:</b> Enabled\n\n"
                        f"<i>You will receive all wallet updates!</i>"
                    )
                    self.send_message(chat_id, status_msg)
                else:
                    self.send_message(
                        chat_id,
                        "❌ You are not subscribed. Send /start to subscribe."
                    )
            
            # Handle /help command
            elif text.startswith('/help'):
                # Show different help based on chat type
                if chat_type == 'private':
                    help_msg = (
                        f"🐋 <b>WhaleWallet Bot Commands</b>\n\n"
                        f"<b>Available Commands:</b>\n"
                        f"/start - Subscribe to notifications\n"
                        f"/stop - Unsubscribe from notifications\n"
                        f"/status - Check your subscription status\n"
                        f"/analysis - Get latest wallet analysis\n"
                        f"/wallets - View monitored wallet addresses\n"
                        f"/info - View tracker system information\n"
                        f"/help - Show this help message\n\n"
                        f"<b>Notification Types:</b>\n"
                        f"🚀 Position Opened\n"
                        f"✅ Position Closed\n"
                        f"🔄 Position Changed\n"
                        f"📥 Deposits (ETH, BTC, Tokens)\n"
                        f"📤 Withdrawals\n"
                        f"💸 Balance Changes\n\n"
                        f"<b>Features:</b>\n"
                        f"• Real-time wallet monitoring\n"
                        f"• Multi-wallet support\n"
                        f"• Position tracking\n"
                        f"• Smart alerts\n"
                        f"• Multi-user support\n\n"
                        f"<i>Questions? Open an issue on GitHub!</i>"
                    )
                else:
                    # Group chat - show permission info
                    help_msg = (
                        f"🐋 <b>WhaleWallet Bot Commands</b>\n\n"
                        f"<b>🔓 Public Commands (Everyone):</b>\n"
                        f"/analysis - Get latest wallet analysis\n"
                        f"/status - Check subscription status\n"
                        f"/wallets - View monitored addresses\n"
                        f"/info - Tracker system information\n"
                        f"/help - Show this help message\n\n"
                        f"<b>🔒 Admin Only Commands:</b>\n"
                        f"/start - Subscribe group to notifications\n"
                        f"/stop - Unsubscribe group from notifications\n\n"
                        f"<b>Notification Types:</b>\n"
                        f"🚀 Position Opened\n"
                        f"✅ Position Closed\n"
                        f"🔄 Position Changed\n"
                        f"📥 Deposits (ETH, BTC, Tokens)\n"
                        f"📤 Withdrawals\n"
                        f"💸 Balance Changes\n\n"
                        f"<b>Features:</b>\n"
                        f"• Real-time wallet monitoring\n"
                        f"• Multi-wallet support\n"
                        f"• Position tracking\n"
                        f"• Smart alerts\n"
                        f"• Group notifications\n\n"
                        f"<i>Admin permissions protect group subscriptions!</i>"
                    )
                self.send_message(chat_id, help_msg)
            
            # Handle /info command
            elif text.startswith('/info'):
                try:
                    import time
                    from datetime import datetime
                    
                    # Get wallet count
                    wallet_count = len(self.wallets) if self.wallets else 1
                    
                    # Get system info
                    info_msg = (
                        f"ℹ️ <b>Tracker System Information</b>\n\n"
                        f"🤖 <b>Bot Status:</b> Active\n"
                        f"👥 <b>Active Subscribers:</b> {self.get_subscriber_count()}\n"
                        f"💼 <b>Monitored Wallets:</b> {wallet_count}\n"
                        f"⏰ <b>Check Interval:</b> 10 minutes\n"
                        f"🔔 <b>Notification System:</b> Telegram\n"
                        f"📊 <b>Monitoring:</b>\n"
                        f"  • ETH Balance\n"
                        f"  • ERC-20 Tokens\n"
                        f"  • Hyperliquid Positions\n"
                        f"  • Deposits & Withdrawals\n\n"
                        f"⚙️ <b>Thresholds:</b>\n"
                        f"  • Balance: ≥0.1 ETH change\n"
                        f"  • Position: ≥5% change\n\n"
                        f"🕐 <b>Current Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                        f"💡 <i>Use /wallets to see wallet details</i>\n"
                        f"<i>System running smoothly! 🟢</i>"
                    )
                    self.send_message(chat_id, info_msg)
                except Exception as e:
                    self.send_message(chat_id, f"⚠️ Error getting system info: {str(e)}")
            
            # Handle /wallets command
            elif text.startswith('/wallets'):
                try:
                    if not self.wallets:
                        self.send_message(chat_id, "⚠️ No wallet information available")
                        return
                    
                    wallets_msg = f"💼 <b>Monitored Wallets ({len(self.wallets)})</b>\n\n"
                    
                    for name, address in self.wallets.items():
                        short_addr = f"{address[:6]}...{address[-4:]}"
                        wallets_msg += f"📍 <b>{name}</b>\n"
                        wallets_msg += f"   <code>{short_addr}</code>\n"
                        wallets_msg += f"   <a href='https://etherscan.io/address/{address}'>View on Etherscan</a>\n\n"
                    
                    wallets_msg += f"<i>All wallets are being monitored 24/7</i>"
                    
                    self.send_message(chat_id, wallets_msg)
                except Exception as e:
                    self.send_message(chat_id, f"⚠️ Error getting wallet info: {str(e)}")
            
            # Handle /analysis command
            elif text.startswith('/analysis'):
                # Check if user is subscribed
                if chat_id not in self.subscribers:
                    self.send_message(
                        chat_id,
                        "⚠️ You need to subscribe first! Send /start to subscribe."
                    )
                    return
                
                # Send loading message
                self.send_message(chat_id, "📊 <b>Generating wallet analysis...</b>\n\n<i>Please wait...</i>")
                
                # Call analysis callback if available
                if self.on_analysis_request:
                    try:
                        self.on_analysis_request(chat_id)
                    except Exception as e:
                        self.send_message(
                            chat_id,
                            f"⚠️ <b>Error generating analysis</b>\n\n{str(e)}"
                        )
                else:
                    self.send_message(
                        chat_id,
                        "⚠️ Analysis feature is not available at the moment."
                    )

            
        except Exception as e:
            print(f"⚠️  Error processing update: {e}")
    
    def _poll_updates(self):
        """Poll for updates in a loop"""
        print("🤖 Telegram bot polling started...")
        
        while self.running:
            try:
                result = self._get_updates(self.last_update_id + 1)
                updates = result.get('result', [])
                
                for update in updates:
                    self.last_update_id = update.get('update_id', self.last_update_id)
                    self._process_update(update)
                
                time.sleep(1)  # Small delay between polls
                
            except Exception as e:
                print(f"⚠️  Error in polling loop: {e}")
                time.sleep(5)  # Wait longer on error
    
    def start_polling(self):
        """Start polling for updates in a background thread"""
        if self.running:
            print("⚠️  Bot is already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._poll_updates, daemon=True)
        self.thread.start()
        print(f"✅ Telegram bot started (Subscribers: {self.get_subscriber_count()})")
    
    def stop_polling(self):
        """Stop polling for updates"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("🛑 Telegram bot stopped")


if __name__ == "__main__":
    # Test the bot manager
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python telegram_bot.py <BOT_TOKEN>")
        sys.exit(1)
    
    bot_token = sys.argv[1]
    bot = TelegramBotManager(bot_token)
    
    print("\n🤖 Starting Telegram Bot Manager...")
    print(f"📊 Current subscribers: {bot.get_subscriber_count()}")
    
    bot.start_polling()
    
    print("\n✅ Bot is running. Press Ctrl+C to stop.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping bot...")
        bot.stop_polling()
        print("👋 Goodbye!")
