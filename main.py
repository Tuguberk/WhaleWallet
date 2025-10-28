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
        self.wallet_address = self.config["wallet_address"]
        self.tracker = WalletTracker(
            self.wallet_address, 
            self.config["etherscan_api_key"]
        )
        self.notifier = NotificationSystem(self.config["notification_settings"])
        self.check_interval = self.config["check_interval"]
        
        print(f"🚀 Starting wallet tracker for: {self.wallet_address}")
        print(f"⏰ Check interval: {self.check_interval} seconds")
        print(f" Telegram notifications: {'Enabled' if self.config['notification_settings']['telegram']['enabled'] else 'Disabled'}")
        
    def check_wallet_changes(self):
        """Main check function for wallet changes"""
        try:
            print(f"\n🔍 Checking wallet at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Check balance changes
            balance_changed, current_balance, change = self.tracker.check_balance_change()
            if balance_changed:
                message = self.notifier.format_balance_change(
                    self.tracker.last_known_balance - change, 
                    current_balance, 
                    change
                )
                self.notifier.send_notification(message, "BALANCE CHANGE")
                save_transaction_log({
                    "type": "balance_change",
                    "old_balance": self.tracker.last_known_balance - change,
                    "new_balance": current_balance,
                    "change": change
                })
            
            # Check position changes
            positions_changed, positions, change_type = self.tracker.check_position_changes()
            if positions_changed:
                message = self.notifier.format_position_change(positions, change_type)
                self.notifier.send_notification(message, f"POSITION {change_type.upper()}")
                save_transaction_log({
                    "type": "position_change",
                    "change_type": change_type,
                    "positions": positions
                })
            
            # Check for deposit/withdrawal transactions
            has_deposit_withdrawal, deposit_txs = self.tracker.check_deposit_withdrawal()
            if has_deposit_withdrawal:
                message = self.notifier.format_deposit_withdrawal(deposit_txs)
                self.notifier.send_notification(message, "DEPOSIT/WITHDRAWAL")
                save_transaction_log({
                    "type": "deposit_withdrawal",
                    "transactions": deposit_txs
                })
            
            # Only print completion message if there were no important changes
            if not (balance_changed or positions_changed or has_deposit_withdrawal):
                print("✅ No important changes detected")
            else:
                print("✅ Check completed - notifications sent")
            
        except Exception as e:
            print(f"❌ Error during wallet check: {e}")
    
    def send_initial_summary(self):
        """Send initial wallet summary on startup"""
        try:
            print("📊 Generating initial wallet summary...")
            summary = self.tracker.get_summary()
            
            # Basic summary
            eth_balance = f"{summary['eth_balance']:.4f} ETH" if summary['eth_balance'] else 'N/A'
            message = f"""
🚀 WALLET TRACKER STARTED
Wallet: {summary['wallet_address']}
ETH Balance: {eth_balance}
Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Monitoring active...
            """
            
            self.notifier.send_notification(message, "TRACKER STARTED")
            
            # Log the tracker start
            save_transaction_log({
                "type": "tracker_started",
                "wallet_address": summary['wallet_address'],
                "eth_balance": eth_balance,
                "start_time": datetime.now().isoformat()
            })
            
            # Send Hyperliquid summary if available
            if summary['hyperliquid_positions']:
                hl_summary = self.notifier.format_hyperliquid_summary(
                    summary['hyperliquid_positions'], 
                    summary.get('position_stats', {})
                )
                self.notifier.send_notification(hl_summary, "INITIAL POSITIONS")
                
                # Log initial positions with detailed stats
                save_transaction_log({
                    "type": "initial_positions",
                    "hyperliquid_summary": summary['hyperliquid_positions'],
                    "position_stats": summary.get('position_stats', {}),
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            print(f"❌ Error sending initial summary: {e}")
    
    def run_manual_check(self):
        """Run a one-time check and display full summary"""
        print("🔍 Running manual wallet check...")
        summary = self.tracker.get_summary()
        
        print(f"\n{'='*60}")
        print(f"📊 WALLET SUMMARY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        print(f"Wallet: {summary['wallet_address']}")
        print(f"ETH Balance: {summary['eth_balance']:.4f} ETH" if summary['eth_balance'] else "ETH Balance: N/A")
        
        if summary['hyperliquid_positions']:
            print(f"\n📈 Hyperliquid Positions:")
            positions = summary['hyperliquid_positions']
            if 'marginSummary' in positions:
                margin = positions['marginSummary']
                print(f"  Account Value: ${float(margin.get('accountValue', 0)):,.2f}")
                print(f"  Total Position Value: ${float(margin.get('totalNotion', 0)):,.2f}")
                print(f"  Margin Usage: {float(margin.get('marginUsage', 0))*100:.2f}%")
        
        if summary['recent_transactions']:
            print(f"\n💰 Recent Transactions:")
            for tx in summary['recent_transactions'][:3]:
                value_eth = float(tx.get('value', 0)) / 10**18
                print(f"  • {value_eth:.4f} ETH - {tx['hash'][:10]}...")
        
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
