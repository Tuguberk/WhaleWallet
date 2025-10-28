import requests
from datetime import datetime
from typing import Dict, Optional, List
import time
from telegram_bot import TelegramBotManager

class NotificationSystem:
    def __init__(self, config: Dict, wallets: Dict = None):
        self.telegram_config = config.get("telegram", {})
        self.console_enabled = config.get("console", {}).get("enabled", True)
        self._last_telegram_call = 0
        self._min_telegram_interval = 0.034  # ~30 messages per second limit
        
        # Initialize bot manager for multi-user support
        self.bot_manager = None
        if self.telegram_config.get("enabled", False):
            bot_token = self.telegram_config.get("bot_token")
            if bot_token:
                self.bot_manager = TelegramBotManager(bot_token)
                # Set wallet information for /wallets command
                if wallets:
                    self.bot_manager.wallets = wallets
                self.bot_manager.start_polling()
    
    def send_notification(self, message: str, title: str = "Wallet Update") -> bool:
        """Send notification through all enabled channels"""
        success = True
        
        # Send to console
        if self.console_enabled:
            self._send_to_console(message, title)
        
        # Send Telegram
        if self.telegram_config.get("enabled", False):
            telegram_success = self._send_telegram(message)
            success = success and telegram_success
        
        return success
    
    def _send_to_console(self, message: str, title: str):
        """Print notification to console with enhanced formatting"""
        # Add color codes for better visibility
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'end': '\033[0m'
        }
        
        print(f"\n{colors['cyan']}{'='*60}{colors['end']}")
        print(f"{colors['bold']}{colors['yellow']}🔔 {title} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{colors['end']}")
        print(f"{colors['cyan']}{'='*60}{colors['end']}")
        
        # Format message with colors for better readability
        formatted_lines = []
        for line in message.split('\n'):
            if line.strip():
                # Color coding based on content
                if '📊' in line or 'POSITION SUMMARY' in line:
                    formatted_lines.append(f"{colors['bold']}{colors['blue']}{line}{colors['end']}")
                elif '📈' in line or 'POSITION BREAKDOWN' in line:
                    formatted_lines.append(f"{colors['bold']}{colors['cyan']}{line}{colors['end']}")
                elif '🔍' in line or 'ACTIVE POSITIONS' in line:
                    formatted_lines.append(f"{colors['bold']}{colors['magenta']}{line}{colors['end']}")
                elif '🟢' in line:
                    formatted_lines.append(f"{colors['green']}{line}{colors['end']}")
                elif '🔴' in line:
                    formatted_lines.append(f"{colors['red']}{line}{colors['end']}")
                elif '💰' in line or 'DEPOSIT' in line or 'WITHDRAWAL' in line:
                    formatted_lines.append(f"{colors['bold']}{colors['yellow']}{line}{colors['end']}")
                elif '🚀' in line or 'POSITION OPENED' in line:
                    formatted_lines.append(f"{colors['bold']}{colors['green']}{line}{colors['end']}")
                elif '✅' in line or 'POSITION CLOSED' in line:
                    formatted_lines.append(f"{colors['bold']}{colors['blue']}{line}{colors['end']}")
                elif '🔄' in line or 'POSITION CHANGED' in line:
                    formatted_lines.append(f"{colors['bold']}{colors['yellow']}{line}{colors['end']}")
                elif '$' in line and ('PnL:' in line or 'Value:' in line):
                    # Highlight monetary values
                    formatted_lines.append(f"{colors['green']}{line}{colors['end']}")
                elif line.startswith('•'):
                    formatted_lines.append(f"  {colors['white']}{line}{colors['end']}")
                elif line.startswith('   '):
                    formatted_lines.append(f"    {colors['cyan']}{line}{colors['end']}")
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        print('\n'.join(formatted_lines))
        print(f"{colors['cyan']}{'='*60}{colors['end']}\n")
    
    def _send_telegram(self, message: str) -> bool:
        """Send Telegram notification to all subscribers with rate limiting and error handling"""
        if not self.bot_manager:
            print("⚠️  Bot manager not initialized")
            return False
        
        # Rate limiting
        elapsed = time.time() - self._last_telegram_call
        if elapsed < self._min_telegram_interval:
            time.sleep(self._min_telegram_interval - elapsed)
        
        try:
            # Broadcast to all subscribers
            results = self.bot_manager.broadcast_message(message)
            self._last_telegram_call = time.time()
            
            if results["success"] > 0:
                print(f"✅ Telegram notification sent to {results['success']}/{results['total']} subscribers")
                if results["failed"] > 0:
                    print(f"⚠️  Failed to send to {results['failed']} subscribers")
                return True
            else:
                print(f"❌ Failed to send Telegram notifications to all {results['total']} subscribers")
                return False
                
        except Exception as e:
            print(f"❌ Unexpected error sending Telegram notification: {type(e).__name__}: {e}")
            return False
    
    def format_balance_change(self, old_balance: float, new_balance: float, change: float, wallet_name: str = "Main Wallet") -> str:
        """Format balance change notification"""
        direction = "📈" if change > 0 else "📉"
        return f"""
{direction} <b>BALANCE CHANGE</b>

💼 <b>Wallet:</b> {wallet_name}
📊 <b>Previous:</b> {old_balance:.4f} ETH
📊 <b>New:</b> {new_balance:.4f} ETH
💸 <b>Change:</b> {change:+.4f} ETH ({(change/old_balance*100):+.2f}%)
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
    
    def format_position_change(self, positions: Dict, change_type: str = "change", wallet_name: str = "Main Wallet") -> str:
        """Format position change notification"""
        if not positions or "marginSummary" not in positions:
            return f"📊 Position data unavailable for {wallet_name}"
        
        margin_summary = positions.get("marginSummary", {})
        account_value = float(margin_summary.get("accountValue", 0))
        total_ntl_pos = float(margin_summary.get("totalNtlPos", 0))
        withdrawable = float(margin_summary.get("withdrawable", 0))
        
        # Calculate total unrealized PnL from all positions
        total_unrealized_pnl = 0
        asset_positions = positions.get("assetPositions", [])
        for pos_data in asset_positions:
            if pos_data.get('position'):
                pos = pos_data['position']
                if pos.get('szi') and float(pos['szi']) != 0:
                    total_unrealized_pnl += float(pos.get('unrealizedPnl', 0))
        
        # Calculate margin usage
        margin_used = account_value - withdrawable if account_value > 0 else 0
        margin_usage = (margin_used / account_value) if account_value > 0 else 0
        
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
{emoji} <b>{title}</b>

💼 <b>Wallet:</b> {wallet_name}
📊 <b>Account Value:</b> ${account_value:,.2f}
💵 <b>Position Value:</b> ${abs(total_ntl_pos):,.2f}
💰 <b>Unrealized PnL:</b> ${total_unrealized_pnl:,.2f}
📈 <b>Margin Usage:</b> {margin_usage*100:.2f}%
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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
    
    def format_deposit_withdrawal(self, transactions: List[Dict], wallet_name: str = "Main Wallet") -> str:
        """Format deposit/withdrawal notifications"""
        if not transactions:
            return "No transactions to display"
        
        summary = f"💰 <b>DEPOSIT/WITHDRAWAL DETECTED</b>\n\n"
        summary += f"💼 <b>Wallet:</b> {wallet_name}\n"
        summary += f"🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
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
                summary += f"{emoji} <b>{tx_type}:</b> {value_str}\n"
                summary += f"   📍 <b>To:</b> <code>{recipient}</code>\n"
            elif tx.get("to", "").lower() == wallet_address:
                tx_type = "DEPOSIT"
                emoji = "📥"
                sender = tx.get("from", "Unknown")[:10] + "..." if tx.get("from") else "Unknown"
                summary += f"{emoji} <b>{tx_type}:</b> {value_str}\n"
                summary += f"   📍 <b>From:</b> <code>{sender}</code>\n"
            
            summary += f"   🔗 <b>Hash:</b> <code>{tx.get('hash', 'Unknown')[:20]}...</code>\n\n"
        
        return summary
    
    def format_hyperliquid_summary(self, positions: Dict, stats: Dict = None) -> str:
        """Format Hyperliquid position summary with detailed statistics"""
        if not positions or "marginSummary" not in positions:
            return "Position data unavailable"
        
        margin_summary = positions.get("marginSummary", {})
        account_value = float(margin_summary.get("accountValue", 0))
        total_ntl_pos = float(margin_summary.get("totalNtlPos", 0))
        withdrawable = float(margin_summary.get("withdrawable", 0))
        
        # Calculate total unrealized PnL from all positions
        total_unrealized_pnl = 0
        asset_positions = positions.get("assetPositions", [])
        for pos_data in asset_positions:
            if pos_data.get('position'):
                pos = pos_data['position']
                if pos.get('szi') and float(pos['szi']) != 0:
                    total_unrealized_pnl += float(pos.get('unrealizedPnl', 0))
        
        # Calculate margin usage
        margin_used = account_value - withdrawable if account_value > 0 else 0
        margin_usage = (margin_used / account_value) if account_value > 0 else 0
        
        # Get individual positions
        asset_positions = positions.get("assetPositions", [])
        
        # If stats provided, use detailed statistics
        if stats:
            total_pos_value = stats.get("total_position_value", abs(total_ntl_pos))
            long_value = stats.get("long_value", 0)
            short_value = stats.get("short_value", 0)
            win_rate = stats.get("win_rate", 0)
            leverage = stats.get("leverage", 0)
            long_pct = stats.get("long_percentage", 0)
            short_pct = stats.get("short_percentage", 0)
            
            summary = f"""
📊 HYPERLIQUID POSITION SUMMARY
Wallet: 0xc2a3...e5f2
Account Value: ${account_value:,.2f}
Total Position Value: ${total_pos_value:,.2f}
Unrealized PnL: ${total_unrealized_pnl:,.2f}
Margin Usage: {margin_usage*100:.2f}%
Open Positions: {stats.get('position_count', len(asset_positions))}
Win Rate: {win_rate:.1f}%
Leverage: {leverage:.2f}x
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📈 POSITION BREAKDOWN:
• Long: ${long_value:,.2f} ({long_pct:.1f}%)
• Short: ${short_value:,.2f} ({short_pct:.1f}%)
            """
        else:
            # Fallback to original format if no stats provided
            summary = f"""
📊 HYPERLIQUID POSITION SUMMARY
Wallet: 0xc2a3...e5f2
Account Value: ${account_value:,.2f}
Total Position Value: ${abs(total_ntl_pos):,.2f}
Unrealized PnL: ${total_unrealized_pnl:,.2f}
Margin Usage: {margin_usage*100:.2f}%
Open Positions: {len(asset_positions)}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        
        # Add individual positions if available
        if asset_positions:
            summary += "\n🔍 ACTIVE POSITIONS:\n"
            for pos_data in asset_positions[:5]:  # Show top 5 positions
                if "position" in pos_data and pos_data["position"]:
                    position = pos_data["position"]
                    coin = position.get("coin", "Unknown")
                    size = float(position.get("szi", 0))
                    entry_price = float(position.get("entryPx", 0))
                    position_value = float(position.get("positionValue", 0))
                    pnl = float(position.get("unrealizedPnl", 0))
                    leverage = position.get("leverage", {}).get("value", 0)
                    liquidation_price = float(position.get("liquidationPx", 0))
                    
                    if size != 0:  # Only show active positions
                        side = "LONG" if size > 0 else "SHORT"
                        size_abs = abs(size)
                        pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
                        margin_used = float(position.get("marginUsed", 0))
                        
                        # Calculate current price and other metrics
                        current_price = abs(position_value / size) if size != 0 else 0
                        roe = float(position.get("returnOnEquity", 0)) * 100
                        funding = position.get("cumFunding", {})
                        funding_since_open = float(funding.get("sinceOpen", 0))
                        funding_change = float(funding.get("sinceChange", 0))
                        funding_emoji = "💰" if funding_since_open > 0 else "💸" if funding_since_open < 0 else "⚪"
                        
                        summary += f"  {pnl_emoji} {coin} {side}: {size_abs:,.2f} @ ${entry_price:,.2f}\n"
                        summary += f"     Current: ${current_price:,.2f} | PnL: ${pnl:,.2f} ({roe:+.2f}%)\n"
                        summary += f"     Value: ${position_value:,.2f} | Lev: {leverage}x | ROE: {roe:+.1f}%\n"
                        summary += f"     Liq Price: ${liquidation_price:,.2f} | Margin: ${margin_used:,.2f}\n"
                        summary += f"     {funding_emoji} Funding: ${funding_since_open:+,.2f} (${funding_change:+,.2f} recent)\n\n"
        
        return summary
