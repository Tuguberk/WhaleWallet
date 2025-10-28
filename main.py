#!/usr/bin/env python3
"""
Crypto Wallet Tracker
Monitors Ethereum wallet and Hyperliquid positions for changes
"""

import time
import json
from datetime import datetime
import schedule
from wallet_tracker import WalletTracker
from notification_system import NotificationSystem
try:
    from secure_config import load_config, save_transaction_log
except ImportError:
    # Fallback to old config if secure_config is not available
    from utils import load_config, save_transaction_log

class CryptoWalletMonitor:
    def __init__(self):
        self.config = load_config()
        self.wallets = self.config.get("wallets", {})
        
        # Create trackers for each wallet
        self.trackers = {}
        for wallet_name, wallet_address in self.wallets.items():
            self.trackers[wallet_name] = WalletTracker(
                wallet_address, 
                self.config["etherscan_api_key"]
            )
        
        # Pass wallets to notification system
        self.notifier = NotificationSystem(
            self.config["notification_settings"],
            wallets=self.wallets
        )
        self.check_interval = self.config["check_interval"]
        
        print(f"🚀 Starting Multi-Wallet Tracker")
        print(f"📍 Monitoring {len(self.wallets)} wallet(s):")
        for name, address in self.wallets.items():
            print(f"   • {name}: {address[:6]}...{address[-4:]}")
        print(f"⏰ Check interval: {self.check_interval} seconds")
        
        # Show bot status
        if self.notifier.bot_manager:
            subscriber_count = self.notifier.bot_manager.get_subscriber_count()
            print(f"🤖 Telegram Bot: Active ({subscriber_count} subscribers)")
            print(f"💡 Users can send /start to subscribe to notifications")
            
            # Set bot callbacks
            self.notifier.bot_manager.on_new_subscriber = self.send_analysis_to_new_subscriber
            self.notifier.bot_manager.on_analysis_request = self.send_analysis_to_new_subscriber
            
            # Set callback for new subscribers
            self.notifier.bot_manager.on_new_subscriber = self.send_analysis_to_new_subscriber
        else:
            print(f"📵 Telegram notifications: Disabled")
        
    def check_wallet_changes(self):
        """Main check function for all wallets"""
        try:
            print(f"\n🔍 Checking {len(self.wallets)} wallet(s) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check each wallet
            for wallet_name, tracker in self.trackers.items():
                self._check_single_wallet(wallet_name, tracker)
            
            print("✅ All wallet checks completed")
            
        except Exception as e:
            print(f"❌ Error during wallet check: {e}")
    
    def _check_single_wallet(self, wallet_name: str, tracker: WalletTracker):
        """Check a single wallet for changes"""
        try:
            print(f"   Checking {wallet_name}...")
            
            # Check balance changes
            balance_changed, current_balance, change = tracker.check_balance_change()
            if balance_changed:
                message = self.notifier.format_balance_change(
                    tracker.last_known_balance - change, 
                    current_balance, 
                    change,
                    wallet_name=wallet_name
                )
                self.notifier.send_notification(message, f"BALANCE CHANGE - {wallet_name}")
                save_transaction_log({
                    "wallet_name": wallet_name,
                    "type": "balance_change",
                    "old_balance": tracker.last_known_balance - change,
                    "new_balance": current_balance,
                    "change": change
                })
            
            # Check position changes
            positions_changed, positions, change_type = tracker.check_position_changes()
            if positions_changed:
                message = self.notifier.format_position_change(
                    positions, 
                    change_type,
                    wallet_name=wallet_name
                )
                self.notifier.send_notification(message, f"POSITION {change_type.upper()} - {wallet_name}")
                save_transaction_log({
                    "wallet_name": wallet_name,
                    "type": "position_change",
                    "change_type": change_type,
                    "positions": positions
                })
            
            # Check for deposit/withdrawal transactions
            has_deposit_withdrawal, deposit_txs = tracker.check_deposit_withdrawal()
            if has_deposit_withdrawal:
                message = self.notifier.format_deposit_withdrawal(
                    deposit_txs,
                    wallet_name=wallet_name
                )
                self.notifier.send_notification(message, f"DEPOSIT/WITHDRAWAL - {wallet_name}")
                save_transaction_log({
                    "wallet_name": wallet_name,
                    "type": "deposit_withdrawal",
                    "transactions": deposit_txs
                })
            
            if not (balance_changed or positions_changed or has_deposit_withdrawal):
                print(f"      ✅ No changes")
            else:
                print(f"      📢 Notification sent")
            
        except Exception as e:
            print(f"   ❌ Error checking {wallet_name}: {e}")
    
    def send_analysis_to_new_subscriber(self, chat_id: int):
        """Send detailed wallet analysis to a new subscriber"""
        try:
            print(f"📊 Generating analysis for new subscriber: {chat_id}")
            
            for wallet_name, tracker in self.trackers.items():
                try:
                    # Get wallet summary
                    summary = tracker.get_summary()
                    
                    # Build detailed analysis message
                    message = f"📊 <b>WALLET ANALYSIS - {wallet_name}</b>\n\n"
                    
                    # ETH Balance
                    if summary.get('eth_balance'):
                        message += f"💰 <b>ETH Balance:</b> {summary['eth_balance']:.4f} ETH\n"
                    
                    # Wallet Address
                    wallet_addr = summary.get('wallet_address', '')
                    if wallet_addr:
                        message += f"🔗 <b>Address:</b> <code>{wallet_addr[:10]}...{wallet_addr[-8:]}</code>\n\n"
                    
                    # Hyperliquid Positions
                    if summary.get('hyperliquid_positions'):
                        positions = summary['hyperliquid_positions']
                        if positions.get('marginSummary'):
                            margin = positions['marginSummary']
                            account_value = float(margin.get('accountValue', 0))
                            total_ntl_pos = float(margin.get('totalNtlPos', 0))
                            total_raw_usd = float(margin.get('totalRawUsd', 0))
                            withdrawable = float(margin.get('withdrawable', 0))
                            
                            # Calculate total unrealized PnL from all positions
                            total_unrealized_pnl = 0
                            asset_positions = positions.get('assetPositions', [])
                            for pos_data in asset_positions:
                                if pos_data.get('position'):
                                    pos = pos_data['position']
                                    if pos.get('szi') and float(pos['szi']) != 0:
                                        total_unrealized_pnl += float(pos.get('unrealizedPnl', 0))
                            
                            # Calculate margin usage
                            margin_used = account_value - withdrawable if account_value > 0 else 0
                            margin_usage = (margin_used / account_value) if account_value > 0 else 0
                            
                            message += f"📈 <b>Hyperliquid Positions:</b>\n"
                            message += f"💵 <b>Account Value:</b> ${account_value:,.2f}\n"
                            message += f"📊 <b>Position Value:</b> ${abs(total_ntl_pos):,.2f}\n"
                            message += f"💰 <b>Unrealized PnL:</b> ${total_unrealized_pnl:,.2f}\n"
                            message += f"📉 <b>Margin Usage:</b> {margin_usage*100:.2f}%\n\n"
                            
                            # Individual positions
                            asset_positions = positions.get('assetPositions', [])
                            if asset_positions:
                                active_positions = [p for p in asset_positions if p.get('position') and p['position'].get('szi') and float(p['position']['szi']) != 0]
                                if active_positions:
                                    message += f"🔍 <b>Active Positions ({len(active_positions)}):</b>\n"
                                    for pos in active_positions[:3]:  # Show top 3
                                        position = pos['position']
                                        coin = position.get('coin', 'Unknown')
                                        size = float(position.get('szi', 0))
                                        entry_px = float(position.get('entryPx', 0))
                                        unrealized = float(position.get('unrealizedPnl', 0))
                                        leverage = position.get('leverage', {}).get('value', 0)
                                        
                                        side = "🟢 Long" if size > 0 else "🔴 Short"
                                        message += f"\n  {side} <b>{coin}</b>\n"
                                        message += f"    Size: {abs(size):.2f} @ ${entry_px:,.2f}\n"
                                        message += f"    PnL: ${unrealized:,.2f} | Lev: {leverage}x\n"
                    
                    # Recent transactions
                    if summary.get('recent_transactions'):
                        txs = summary['recent_transactions'][:3]
                        if txs:
                            message += f"\n💸 <b>Recent Transactions ({len(txs)}):</b>\n"
                            for tx in txs:
                                value_eth = float(tx.get('value', 0)) / 10**18
                                tx_hash = tx.get('hash', '')[:12]
                                message += f"  • {value_eth:.4f} ETH - <code>{tx_hash}...</code>\n"
                    
                    message += f"\n🕐 <b>Analysis Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    message += f"\n\n<i>You're all set! You'll receive updates when changes occur.</i> 🎯"
                    
                    # Send directly to the new subscriber
                    if self.notifier.bot_manager:
                        self.notifier.bot_manager.send_message(chat_id, message)
                        print(f"   ✅ Analysis sent for {wallet_name}")
                    
                except Exception as e:
                    error_msg = f"⚠️ <b>Error loading analysis for {wallet_name}</b>\n\n{str(e)}"
                    if self.notifier.bot_manager:
                        self.notifier.bot_manager.send_message(chat_id, error_msg)
                    print(f"   ❌ Error generating analysis for {wallet_name}: {e}")
            
            print(f"✅ Analysis complete for subscriber {chat_id}")
            
        except Exception as e:
            print(f"❌ Error sending analysis to {chat_id}: {e}")
    
    def send_initial_summary(self):
        """Send initial wallet summary on startup"""
        try:
            print("📊 Generating initial wallet summary...")
            
            message = f"🚀 <b>WALLET TRACKER STARTED</b>\n\n"
            message += f"💼 <b>Monitoring {len(self.wallets)} wallet(s):</b>\n\n"
            
            # Get summary for each wallet
            for wallet_name, tracker in self.trackers.items():
                try:
                    summary = tracker.get_summary()
                    eth_balance = f"{summary['eth_balance']:.4f} ETH" if summary['eth_balance'] else 'N/A'
                    
                    message += f"📍 <b>{wallet_name}</b>\n"
                    message += f"   � Balance: {eth_balance}\n"
                    message += f"   🔗 {summary['wallet_address'][:10]}...{summary['wallet_address'][-6:]}\n\n"
                except Exception as e:
                    message += f"📍 <b>{wallet_name}</b>\n"
                    message += f"   ⚠️ Error loading: {str(e)}\n\n"
            
            message += f"⏰ <b>Check Interval:</b> {self.check_interval} seconds\n"
            message += f"🕐 <b>Start Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            message += f"<i>Monitoring active... 🟢</i>"
            
            self.notifier.send_notification(message, "TRACKER STARTED")
            
            # Log the tracker start
            save_transaction_log({
                "type": "tracker_started",
                "wallets": list(self.wallets.keys()),
                "timestamp": datetime.now().isoformat()
            })
            
            print("✅ Initial summary sent successfully")
            
        except Exception as e:
            print(f"❌ Error sending initial summary: {e}")
    
    def run_manual_check(self):
        """Run a one-time check and display full summary"""
        print("🔍 Running manual wallet check...")
        
        print(f"\n{'='*60}")
        print(f"📊 MULTI-WALLET SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        for wallet_name, tracker in self.trackers.items():
            try:
                summary = tracker.get_summary()
                
                print(f"💼 {wallet_name}")
                print(f"   Address: {summary['wallet_address']}")
                print(f"   ETH Balance: {summary['eth_balance']:.4f} ETH" if summary['eth_balance'] else "   ETH Balance: N/A")
                
                if summary['hyperliquid_positions']:
                    positions = summary['hyperliquid_positions']
                    if 'marginSummary' in positions:
                        margin = positions['marginSummary']
                        
                        # Calculate total unrealized PnL from positions
                        total_unrealized_pnl = 0
                        asset_positions = positions.get('assetPositions', [])
                        for pos_data in asset_positions:
                            if pos_data.get('position'):
                                pos = pos_data['position']
                                if pos.get('szi') and float(pos['szi']) != 0:
                                    total_unrealized_pnl += float(pos.get('unrealizedPnl', 0))
                        
                        account_value = float(margin.get('accountValue', 0))
                        total_ntl_pos = float(margin.get('totalNtlPos', 0))
                        withdrawable = float(margin.get('withdrawable', 0))
                        margin_used = account_value - withdrawable if account_value > 0 else 0
                        margin_usage = (margin_used / account_value) if account_value > 0 else 0
                        
                        print(f"   📈 Hyperliquid:")
                        print(f"      Account Value: ${account_value:,.2f}")
                        print(f"      Position Value: ${abs(total_ntl_pos):,.2f}")
                        print(f"      Unrealized PnL: ${total_unrealized_pnl:,.2f}")
                        print(f"      Margin Usage: {margin_usage*100:.2f}%")
                
                if summary['recent_transactions']:
                    print(f"   💰 Recent Transactions:")
                    for tx in summary['recent_transactions'][:3]:
                        value_eth = float(tx.get('value', 0)) / 10**18
                        print(f"      • {value_eth:.4f} ETH - {tx['hash'][:10]}...")
                
                print()  # Empty line between wallets
                
            except Exception as e:
                print(f"   ❌ Error loading {wallet_name}: {e}\n")
        
        print(f"{'='*60}")
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        self.send_initial_summary()
        
        # Schedule regular checks
        schedule.every(self.check_interval).seconds.do(self.check_wallet_changes)
        
        print(f"🔄 Monitoring started. Checking every {self.check_interval} seconds.")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")

def main():
    monitor = CryptoWalletMonitor()
    
    # Check command line arguments
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        monitor.run_manual_check()
    else:
        monitor.start_monitoring()

if __name__ == "__main__":
    main()
