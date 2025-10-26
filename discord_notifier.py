import requests
import json
from datetime import datetime
from typing import Dict

class DiscordNotifier:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def send_notification(self, message: str, title: str = "Wallet Update") -> bool:
        """Send notification to Discord via webhook"""
        try:
            payload = {
                "embeds": [{
                    "title": f"🔔 {title}",
                    "description": message,
                    "color": 5814783,  # Blue color
                    "timestamp": datetime.now().isoformat()
                }]
            }
            
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code == 204:
                print("Discord notification sent successfully")
                return True
            else:
                print(f"Discord API error: {response.text}")
                return False
        except Exception as e:
            print(f"Failed to send Discord notification: {e}")
            return False
    
    def format_balance_change(self, old_balance: float, new_balance: float, change: float) -> str:
        """Format balance change notification for Discord"""
        direction = "📈" if change > 0 else "📉"
        return f"""
{direction} **BALANCE CHANGE DETECTED**
**Wallet:** `0xc2a3...e5f2`
**Previous Balance:** {old_balance:.4f} ETH
**New Balance:** {new_balance:.4f} ETH
**Change:** {change:+.4f} ETH ({(change/old_balance*100):+.2f}%)
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    
    def format_position_change(self, positions: Dict) -> str:
        """Format position change notification for Discord"""
        if not positions or "marginSummary" not in positions:
            return "Position data unavailable"
        
        margin_summary = positions.get("marginSummary", {})
        account_value = margin_summary.get("accountValue", 0)
        total_notion = margin_summary.get("totalNotion", 0)
        margin_usage = margin_summary.get("marginUsage", 0)
        
        return f"""
🔄 **POSITION CHANGE DETECTED**
**Wallet:** `0xc2a3...e5f2`
**Account Value:** ${float(account_value):,.2f}
**Total Position Value:** ${float(total_notion):,.2f}
**Margin Usage:** {float(margin_usage)*100:.2f}%
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
