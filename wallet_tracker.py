import requests
import json
from datetime import datetime
import time
from typing import Dict, List, Optional, Tuple

class WalletTracker:
    def __init__(self, wallet_address: str, etherscan_api_key: str):
        self.wallet_address = wallet_address
        self.etherscan_api_key = etherscan_api_key
        self.base_url = "https://api.etherscan.io/api"
        self.hyperliquid_url = "https://api.hyperliquid.xyz/info"
        self.last_known_balance = None
        self.last_known_positions = None
        
    def get_eth_balance(self) -> Optional[float]:
        """Get current ETH balance"""
        try:
            params = {
                "module": "account",
                "action": "balance",
                "address": self.wallet_address,
                "tag": "latest",
                "apikey": self.etherscan_api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            if data["status"] == "1":
                return float(data["result"]) / 10**18  # Convert from Wei to ETH
            return None
        except Exception as e:
            print(f"Error getting ETH balance: {e}")
            return None
    
    def get_token_transfers(self, limit: int = 10) -> List[Dict]:
        """Get recent token transfers"""
        try:
            params = {
                "module": "account",
                "action": "tokentx",
                "address": self.wallet_address,
                "sort": "desc",
                "apikey": self.etherscan_api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            if data["status"] == "1":
                return data["result"][:limit]
            return []
        except Exception as e:
            print(f"Error getting token transfers: {e}")
            return []
    
    def get_normal_transactions(self, limit: int = 10) -> List[Dict]:
        """Get recent normal transactions"""
        try:
            params = {
                "module": "account",
                "action": "txlist",
                "address": self.wallet_address,
                "sort": "desc",
                "apikey": self.etherscan_api_key
            }
            response = requests.get(self.base_url, params=params)
            data = response.json()
            if data["status"] == "1":
                return data["result"][:limit]
            return []
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    def check_deposit_withdrawal(self) -> Tuple[bool, List[Dict]]:
        """Check for new deposit or withdrawal transactions (ETH and tokens)"""
        try:
            # Get recent transactions and token transfers
            recent_eth_txs = self.get_normal_transactions(5)
            recent_token_txs = self.get_token_transfers(10)
            
            all_transfers = []
            current_time = int(time.time())
            
            # Check ETH transfers
            for tx in recent_eth_txs:
                # Check if it's a simple ETH transfer (not contract interaction)
                if (tx.get("to") == self.wallet_address.lower() or 
                    tx.get("from") == self.wallet_address.lower()) and \
                   tx.get("isError", "0") == "0" and \
                   float(tx.get("value", 0)) > 0:  # Has ETH value
                    
                    tx_time = int(tx.get("timeStamp", 0))
                    
                    # Check if transaction is within last check interval (10 minutes)
                    if current_time - tx_time <= 600:  # 600 seconds = 10 minutes
                        tx["asset"] = "ETH"
                        all_transfers.append(tx)
            
            # Check token transfers (including BTC and other ERC-20 tokens)
            for tx in recent_token_txs:
                tx_time = int(tx.get("timeStamp", 0))
                
                # Check if transaction is within last check interval (10 minutes)
                if current_time - tx_time <= 600:  # 600 seconds = 10 minutes
                    tx["asset"] = tx.get("tokenSymbol", "Unknown")
                    all_transfers.append(tx)
            
            if all_transfers:
                return True, all_transfers
            return False, []
            
        except Exception as e:
            print(f"Error checking deposits/withdrawals: {e}")
            return False, []
    
    def get_hyperliquid_positions(self) -> Optional[Dict]:
        """Get Hyperliquid perpetual positions"""
        try:
            payload = {
                "type": "clearinghouseState",
                "user": self.wallet_address
            }
            response = requests.post(self.hyperliquid_url, json=payload)
            data = response.json()
            if data and "marginSummary" in data:
                return data
            return None
        except Exception as e:
            print(f"Error getting Hyperliquid positions: {e}")
            return None
    
    def check_balance_change(self) -> Tuple[bool, float, float]:
        """Check if balance has changed significantly"""
        current_balance = self.get_eth_balance()
        if current_balance is None:
            return False, 0, 0
        
        if self.last_known_balance is None:
            self.last_known_balance = current_balance
            return False, current_balance, 0
        
        change = abs(current_balance - self.last_known_balance)
        if change > 0.1:  # Significant change threshold
            significant_change = True
        else:
            significant_change = False
        
        self.last_known_balance = current_balance
        return significant_change, current_balance, change
    
    def check_position_changes(self) -> Tuple[bool, Dict, str]:
        """Check if positions have opened, closed, or significantly changed"""
        current_positions = self.get_hyperliquid_positions()
        if current_positions is None:
            return False, {}, "position_data_unavailable"
        
        if self.last_known_positions is None:
            self.last_known_positions = current_positions
            return False, current_positions, "initial_setup"
        
        # Extract current and previous positions
        current_asset_positions = current_positions.get("assetPositions", [])
        previous_asset_positions = self.last_known_positions.get("assetPositions", [])
        
        # Create dictionaries of positions by coin for easier comparison
        current_pos_dict = {}
        previous_pos_dict = {}
        
        for pos in current_asset_positions:
            if "position" in pos and pos["position"]:
                coin = pos["position"].get("coin", "")
                size = float(pos["position"].get("szi", 0))
                current_pos_dict[coin] = size
        
        for pos in previous_asset_positions:
            if "position" in pos and pos["position"]:
                coin = pos["position"].get("coin", "")
                size = float(pos["position"].get("szi", 0))
                previous_pos_dict[coin] = size
        
        # Check for position changes
        changes_detected = False
        change_type = "none"
        
        # Check for new positions opened
        for coin, size in current_pos_dict.items():
            if size != 0:
                if coin not in previous_pos_dict or previous_pos_dict[coin] == 0:
                    changes_detected = True
                    change_type = "position_opened"
                    break
                # Check for significant size change (more than 5% change)
                elif abs(size - previous_pos_dict[coin]) / abs(previous_pos_dict[coin]) > 0.05:
                    changes_detected = True
                    change_type = "position_changed"
                    break
        
        # Check for positions closed
        if not changes_detected:
            for coin, size in previous_pos_dict.items():
                if size != 0 and (coin not in current_pos_dict or current_pos_dict[coin] == 0):
                    changes_detected = True
                    change_type = "position_closed"
                    break
        
        self.last_known_positions = current_positions
        return changes_detected, current_positions, change_type
    
    def get_summary(self) -> Dict:
        """Get comprehensive wallet summary"""
        balance = self.get_eth_balance()
        positions = self.get_hyperliquid_positions()
        recent_txs = self.get_normal_transactions(5)
        token_txs = self.get_token_transfers(5)
        
        # Calculate additional statistics
        stats = self.calculate_position_stats(positions) if positions else {}
        
        return {
            "wallet_address": self.wallet_address,
            "eth_balance": balance,
            "hyperliquid_positions": positions,
            "position_stats": stats,
            "recent_transactions": recent_txs,
            "token_transfers": token_txs,
            "timestamp": datetime.now().isoformat()
        }
    
    def calculate_position_stats(self, positions: Dict) -> Dict:
        """Calculate detailed position statistics"""
        try:
            margin_summary = positions.get("marginSummary", {})
            asset_positions = positions.get("assetPositions", [])
            
            account_value = float(margin_summary.get("accountValue", 0))
            total_ntl_pos = float(margin_summary.get("totalNtlPos", 0))
            margin_used = float(margin_summary.get("totalMarginUsed", 0))
            
            # Calculate PnL
            total_unrealized_pnl = 0
            long_value = 0
            short_value = 0
            position_count = 0
            winning_positions = 0
            
            for pos_data in asset_positions:
                if "position" in pos_data and pos_data["position"]:
                    position = pos_data["position"]
                    pnl = float(position.get("unrealizedPnl", 0))
                    position_value = float(position.get("positionValue", 0))
                    size = float(position.get("szi", 0))
                    
                    if size != 0:  # Active position
                        position_count += 1
                        total_unrealized_pnl += pnl
                        
                        if size > 0:  # Long position
                            long_value += position_value
                        else:  # Short position
                            short_value += abs(position_value)
                        
                        if pnl > 0:
                            winning_positions += 1
            
            # Calculate win rate
            win_rate = (winning_positions / position_count * 100) if position_count > 0 else 0
            
            # Calculate ROE (Return on Equity)
            roe = (total_unrealized_pnl / account_value * 100) if account_value > 0 else 0
            
            return {
                "account_value": account_value,
                "total_position_value": total_ntl_pos,
                "long_value": long_value,
                "short_value": short_value,
                "total_unrealized_pnl": total_unrealized_pnl,
                "position_count": position_count,
                "winning_positions": winning_positions,
                "win_rate": win_rate,
                "roe_percentage": roe,
                "leverage": total_ntl_pos / account_value if account_value > 0 else 0,
                "long_percentage": (long_value / total_ntl_pos * 100) if total_ntl_pos > 0 else 0,
                "short_percentage": (short_value / total_ntl_pos * 100) if total_ntl_pos > 0 else 0
            }
        except Exception as e:
            print(f"Error calculating position stats: {e}")
            return {}
