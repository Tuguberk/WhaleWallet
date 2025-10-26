import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, Optional, List

class NotificationSystem:
    def __init__(self, config: Dict):
        self.email_config = config.get("email", {})
        self.telegram_config = config.get("telegram", {})
        self.console_enabled = config.get("console", {}).get("enabled", True)
    
    def send_notification(self, message: str, title: str = "Wallet Update") -> bool:
        """Send notification through all enabled channels"""
        success = True
        
        # Send to console
        if self.console_enabled:
            self._send_to_console(message, title)
        
        # Send email
        if self.email_config.get("enabled", False):
            email_success = self._send_email(message, title)
            success = success and email_success
        
        # Send Telegram
        if self.telegram_config.get("enabled", False):
            telegram_success = self._send_telegram(message)
            success = success and telegram_success
        
        return success
    
    def _send_to_console(self, message: str, title: str):
        """Print notification to console"""
        print(f"\n{'='*50}")
        print(f"🔔 {title} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        print(message)
        print(f"{'='*50}\n")
    
    def _send_email(self, message: str, title: str) -> bool:
        """Send email notification"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config["sender_email"]
            msg['To'] = self.email_config["recipient_email"]
            msg['Subject'] = title
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(self.email_config["smtp_server"], self.email_config["smtp_port"])
            server.starttls()
            server.login(self.email_config["sender_email"], self.email_config["sender_password"])
            text = msg.as_string()
            server.sendmail(self.email_config["sender_email"], self.email_config["recipient_email"], text)
            server.quit()
            
            print("Email notification sent successfully")
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def _send_telegram(self, message: str) -> bool:
        """Send Telegram notification"""
        try:
            url = f"https://api.telegram.org/bot{self.telegram_config['bot_token']}/sendMessage"
            payload = {
                "chat_id": self.telegram_config["chat_id"],
                "text": message,
                "parse_mode": "HTML"
            }
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print("Telegram notification sent successfully")
                return True
            else:
                print(f"Telegram API error: {response.text}")
                return False
        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")
            return False
    
    def format_balance_change(self, old_balance: float, new_balance: float, change: float) -> str:
        """Format balance change notification"""
        direction = "📈" if change > 0 else "📉"
        return f"""
{direction} BALANCE CHANGE DETECTED
Wallet: 0xc2a3...e5f2
Previous Balance: {old_balance:.4f} ETH
New Balance: {new_balance:.4f} ETH
Change: {change:+.4f} ETH ({(change/old_balance*100):+.2f}%)
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    
    def format_position_change(self, positions: Dict, change_type: str = "change") -> str:
        """Format position change notification"""
        if not positions or "marginSummary" not in positions:
            return "Position data unavailable"
        
        margin_summary = positions.get("marginSummary", {})
        account_value = margin_summary.get("accountValue", 0)
        total_notion = margin_summary.get("totalNotion", 0)
        unrealized_pnl = margin_summary.get("unrealizedPnl", 0)
        margin_usage = margin_summary.get("marginUsage", 0)
        
        # Get individual positions
        asset_positions = positions.get("assetPositions", [])
        
        # Choose appropriate emoji and title based on change type
        if change_type == "position_opened":
            emoji = "🚀"
            title = "POSITION OPENED"
        elif change_type == "position_closed":
            emoji = "✅"
            title = "POSITION CLOSED"
        else:
            emoji = "🔄"
            title = "POSITION CHANGED"
        
        summary = f"""
{emoji} {title}
Wallet: 0xc2a3...e5f2
Account Value: ${float(account_value):,.2f}
Total Position Value: ${float(total_notion):,.2f}
Unrealized PnL: ${float(unrealized_pnl):,.2f}
Margin Usage: {float(margin_usage)*100:.2f}%
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Add individual positions if available
        if asset_positions:
            summary += "\n📈 POSITIONS:\n"
            for pos in asset_positions[:5]:  # Show top 5 positions
                if "position" in pos and pos["position"]:
                    position = pos["position"]
                    coin = position.get("coin", "Unknown")
                    size = position.get("szi", 0)
                    entry_price = position.get("entryPx", 0)
                    position_value = position.get("positionValue", 0)
                    unrealized_pnl = position.get("unrealizedPnl", 0)
                    leverage = position.get("leverage", {}).get("value", 0)
                    liquidation_price = position.get("liquidationPx", 0)
                    margin_used = position.get("marginUsed", 0)
                    
                    # Determine side (long if size > 0, short if size < 0)
                    side = "LONG" if float(size) > 0 else "SHORT"
                    
                    # Calculate current price (position value / size)
                    try:
                        current_price = abs(float(position_value) / float(size)) if float(size) != 0 else 0
                    except:
                        current_price = 0
                    
                    if float(size) != 0:
                        summary += f"  • {coin} {side}: {size} @ ${entry_price}\n"
                        summary += f"    PnL: ${unrealized_pnl} | Leverage: {leverage}x\n"
                        summary += f"    Position Value: ${position_value}\n"
                        summary += f"    Liq Price: ${liquidation_price} | Margin Used: ${margin_used}\n\n"
        
        return summary
    
    def format_transaction_alert(self, tx: Dict) -> str:
        """Format transaction notification"""
        value_eth = float(tx.get("value", 0)) / 10**18
        direction = "OUT" if tx["from"].lower() == "0xc2a30212a8ddac9e123944d6e29faddce994e5f2".lower() else "IN"
        
        return f"""
💰 NEW TRANSACTION DETECTED
Direction: {direction}
Value: {value_eth:.4f} ETH
To: {tx.get('to', 'N/A')}
Hash: {tx.get('hash', 'N/A')}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    
    def format_deposit_withdrawal(self, transactions: List[Dict]) -> str:
        """Format deposit/withdrawal notifications"""
        if not transactions:
            return "No transactions to display"
        
        summary = "💰 DEPOSIT/WITHDRAWAL DETECTED\n"
        summary += f"Wallet: 0xc2a3...e5f2\n"
        summary += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for tx in transactions:
            asset = tx.get("asset", "Unknown")
            wallet_address = "0xc2a30212a8ddac9e123944d6e29faddce994e5f2".lower()
            
            # Calculate value based on asset type
            if asset == "ETH":
                value = float(tx.get("value", 0)) / 10**18
                value_str = f"{value:.4f} {asset}"
            else:
                # For tokens (like BTC), the value is already in the correct decimal format
                value = float(tx.get("value", 0)) / (10 ** int(tx.get("tokenDecimal", 18)))
                value_str = f"{value:.6f} {asset}"
            
            # Determine if it's a deposit or withdrawal
            if tx.get("from", "").lower() == wallet_address:
                tx_type = "WITHDRAWAL"
                emoji = "📤"
                recipient = tx.get("to", "Unknown")[:10] + "..." if tx.get("to") else "Unknown"
                summary += f"{emoji} {tx_type}: {value_str}\n"
                summary += f"   To: {recipient}\n"
            elif tx.get("to", "").lower() == wallet_address:
                tx_type = "DEPOSIT"
                emoji = "📥"
                sender = tx.get("from", "Unknown")[:10] + "..." if tx.get("from") else "Unknown"
                summary += f"{emoji} {tx_type}: {value_str}\n"
                summary += f"   From: {sender}\n"
            
            summary += f"   Hash: {tx.get('hash', 'Unknown')[:20]}...\n\n"
        
        return summary
    
    def format_hyperliquid_summary(self, positions: Dict) -> str:
        """Format Hyperliquid position summary"""
        if not positions or "marginSummary" not in positions:
            return "Position data unavailable"
        
        margin_summary = positions.get("marginSummary", {})
        account_value = margin_summary.get("accountValue", 0)
        total_notion = margin_summary.get("totalNotion", 0)
        unrealized_pnl = margin_summary.get("unrealizedPnl", 0)
        margin_usage = margin_summary.get("marginUsage", 0)
        
        # Get individual positions
        asset_positions = positions.get("assetPositions", [])
        
        summary = f"""
📊 HYPERLIQUID POSITION SUMMARY
Wallet: 0xc2a3...e5f2
Account Value: ${float(account_value):,.2f}
Total Position Value: ${float(total_notion):,.2f}
Unrealized PnL: ${float(unrealized_pnl):,.2f}
Margin Usage: {float(margin_usage)*100:.2f}%
Open Positions: {len(asset_positions)}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # Add individual positions if available
        if asset_positions:
            summary += "\n📈 POSITIONS:\n"
            for pos in asset_positions[:5]:  # Show top 5 positions
                if "position" in pos and pos["position"]:
                    coin = pos["position"].get("coin", "Unknown")
                    size = pos["position"].get("size", 0)
                    side = pos["position"].get("side", "Unknown")
                    entry_price = pos["position"].get("entryPx", 0)
                    current_price = pos["position"].get("markPx", 0)
                    
                    if float(size) != 0:
                        summary += f"  • {coin}: {side} {size} @ ${entry_price} (Current: ${current_price})\n"
        
        return summary
