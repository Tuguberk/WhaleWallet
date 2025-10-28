import json
from datetime import datetime
import os

def load_config(config_path: str = "config.py") -> dict:
    """Load configuration from file"""
    import config
    return {
        "wallets": config.WALLETS,  # Multi-wallet support
        "wallet_address": config.WALLET_ADDRESS,  # Legacy support
        "etherscan_api_key": config.ETHERSCAN_API_KEY,
        "check_interval": config.CHECK_INTERVAL,
        "notification_settings": config.NOTIFICATION_SETTINGS,
        "balance_change_threshold": config.BALANCE_CHANGE_THRESHOLD,
        "position_change_threshold": config.POSITION_CHANGE_THRESHOLD
    }

def save_transaction_log(tx_data: dict, log_file: str = "/app/logs/transactions.log"):
    """Save transaction data to log file"""
    try:
        # Ensure directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        with open(log_file, "a") as f:
            f.write(f"{datetime.now().isoformat()}: {json.dumps(tx_data)}\n")
    except Exception as e:
        print(f"Error saving transaction log: {e}")

def format_wei_to_ether(wei_amount: int) -> float:
    """Convert Wei to Ether"""
    return wei_amount / 10**18

def format_address(address: str) -> str:
    """Format address for display"""
    if len(address) < 10:
        return address
    return f"{address[:6]}...{address[-4:]}"

def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp

def calculate_price_change(old_price: float, new_price: float) -> float:
    """Calculate percentage price change"""
    if old_price == 0:
        return 0
    return ((new_price - old_price) / old_price) * 100

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount"""
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "ETH":
        return f"{amount:.4f} ETH"
    else:
        return f"{amount:.2f} {currency}"
