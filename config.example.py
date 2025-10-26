# Configuration file for crypto wallet tracker

# Wallet to track
WALLET_ADDRESS = "YOUR_WALLET_ADDRESS"

# Etherscan API configuration
ETHERSCAN_API_KEY = "YOUR_ETHERSCAN_API_KEY"  # Get from https://etherscan.io/apis

# Hyperliquid API configuration
HYPERLIQUID_API_URL = "https://api.hyperliquid.xyz/info"

# Notification settings
NOTIFICATION_SETTINGS = {
    "email": {
        "enabled": False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": "your_email@gmail.com",
        "sender_password": "your_password",
        "recipient_email": "recipient@example.com"
    },
    "telegram": {
        "enabled": False,
        "bot_token": "YOUR_BOT_TOKEN",
        "chat_id": "YOUR_CHAT_ID"
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
