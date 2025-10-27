import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration file for crypto wallet tracker

# Wallet to track
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS", "YOUR_WALLET_ADDRESS")

# Etherscan API configuration
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "YOUR_ETHERSCAN_API_KEY")

# Hyperliquid API configuration
HYPERLIQUID_API_URL = "https://api.hyperliquid.xyz/info"

# Telegram configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")

# Email configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "your_email@gmail.com")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "your_password")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "recipient@example.com")

# Notification settings
NOTIFICATION_SETTINGS = {
    "email": {
        "enabled": True if EMAIL_SENDER and EMAIL_PASSWORD and EMAIL_RECIPIENT else False,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "sender_email": EMAIL_SENDER,
        "sender_password": EMAIL_PASSWORD,
        "recipient_email": EMAIL_RECIPIENT
    },
    "telegram": {
        "enabled": True if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID else False,
        "bot_token": TELEGRAM_BOT_TOKEN,
        "chat_id": TELEGRAM_CHAT_ID
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

