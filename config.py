import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Configuration file for crypto wallet tracker

# Multiple wallet support
# Format: WALLETS={"Main Wallet":"0x123...","Trading":"0x456...","Savings":"0x789..."}
# Or single wallet (backwards compatible): WALLET_ADDRESS=0x123...
def parse_wallets():
    """Parse wallet configuration from environment variables"""
    wallets_json = os.getenv("WALLETS", "")
    
    if wallets_json:
        try:
            # Multi-wallet format
            wallets = json.loads(wallets_json)
            return wallets
        except json.JSONDecodeError:
            print("⚠️  Invalid WALLETS JSON format. Using single wallet mode.")
    
    # Fallback to single wallet (backwards compatible)
    single_wallet = os.getenv("WALLET_ADDRESS", "YOUR_WALLET_ADDRESS")
    if single_wallet and single_wallet != "YOUR_WALLET_ADDRESS":
        # Use wallet name if provided, otherwise use "Main Wallet"
        wallet_name = os.getenv("WALLET_NAME", "Main Wallet")
        return {wallet_name: single_wallet}
    
    return {}

WALLETS = parse_wallets()
# Legacy support
WALLET_ADDRESS = list(WALLETS.values())[0] if WALLETS else os.getenv("WALLET_ADDRESS", "YOUR_WALLET_ADDRESS")

# Etherscan API configuration
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "YOUR_ETHERSCAN_API_KEY")

# Hyperliquid API configuration
HYPERLIQUID_API_URL = "https://api.hyperliquid.xyz/info"

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")  # Optional - bot will accept /start from any user

# Notification settings
NOTIFICATION_SETTINGS = {
    "telegram": {
        "enabled": True if TELEGRAM_BOT_TOKEN and TELEGRAM_BOT_TOKEN != "YOUR_BOT_TOKEN" else False,
        "bot_token": TELEGRAM_BOT_TOKEN,
        "chat_id": TELEGRAM_CHAT_ID  # Legacy support - not required anymore
    },
    "console": {
        "enabled": True
    }
}

# Tracking intervals (in seconds)
CHECK_INTERVAL = 600  # Check every 10 minutes

# Thresholds for notifications
BALANCE_CHANGE_THRESHOLD = 0.1  # Notify if balance changes more than 0.1 ETH
POSITION_CHANGE_THRESHOLD = 1000  # Notify if position changes more than $1000


def validate_config():
    """
    Validate configuration to ensure all required values are set properly.
    Raises ValueError if configuration is invalid.
    """
    # Check for required environment variables
    required_vars = {
        "ETHERSCAN_API_KEY": ETHERSCAN_API_KEY,
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    }
    
    # Check wallets
    if not WALLETS:
        required_vars["WALLET_ADDRESS"] = WALLET_ADDRESS
    
    # TELEGRAM_CHAT_ID is now optional - bot accepts /start from any user
    
    # Invalid default values that indicate the variable hasn't been set
    invalid_defaults = ["YOUR_", "your_", "SIZIN_", "example", "test"]
    
    errors = []
    
    # Validate wallets
    if not WALLETS:
        errors.append("❌ No wallets configured. Set WALLETS or WALLET_ADDRESS")
    else:
        print(f"✅ Monitoring {len(WALLETS)} wallet(s):")
        for name, address in WALLETS.items():
            print(f"   📍 {name}: {address[:6]}...{address[-4:]}")
    
    for var_name, var_value in required_vars.items():
        if not var_value:
            errors.append(f"❌ {var_name} is not set")
        elif any(default in str(var_value) for default in invalid_defaults):
            errors.append(f"❌ {var_name} contains a placeholder value")
    
    if errors:
        error_msg = "\n".join(errors)
        raise ValueError(
            f"\n{'='*60}\n"
            f"⚠️  CONFIGURATION ERROR\n"
            f"{'='*60}\n"
            f"{error_msg}\n\n"
            f"Please update your .env file with valid values.\n"
            f"See .env.example for reference.\n"
            f"💡 Note: TELEGRAM_CHAT_ID is optional - bot will accept /start from any user\n"
            f"{'='*60}\n"
        )
    
    return True


# Validate configuration on import
try:
    validate_config()
except ValueError as e:
    import sys
    print(str(e))
    sys.exit(1)
