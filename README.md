# Balina2Droid - Crypto Wallet Tracker

A Python application that monitors Ethereum wallet and Hyperliquid positions for changes and sends notifications via Telegram.

## Features

- **Wallet Monitoring**: Tracks ETH balance changes and token transfers
- **Position Tracking**: Monitors Hyperliquid perpetual positions
- **Smart Notifications**: Only sends notifications for important events:
  - Position opened/closed/changed
  - Deposits and withdrawals (ETH, BTC, and other ERC-20 tokens)
  - Significant balance changes
- **Telegram Integration**: Real-time notifications via Telegram bot
- **Configurable**: 10-minute check intervals

## Installation

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/Tuguberk/WhaleWallet.git
cd WhaleWallet

# 2. Configure environment variables
cp .env.example .env
nano .env  # Edit with your values

# 3. Start with Docker Compose
docker-compose up -d

# 4. View logs
docker-compose logs -f
```

**That's it!** 🎉 See [DOCKER_GUIDE.md](./DOCKER_GUIDE.md) for detailed documentation.

### Option 2: Manual Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Create a Telegram bot:

   - Contact [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot and get the bot token

2. Get your Chat ID:

   - Send a message to your bot
   - Run `python3 get_chat_id.py` to get your chat ID

3. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Edit `.env` with your settings:
     ```bash
     WALLET_ADDRESS=your_wallet_address
     ETHERSCAN_API_KEY=your_etherscan_api_key
     TELEGRAM_BOT_TOKEN=your_bot_token
     TELEGRAM_CHAT_ID=your_chat_id
     ```

## Usage

### Manual Check

```bash
python3 main.py --check
```

### Continuous Monitoring

```bash
python3 main.py
```

The application will check for changes every 10 minutes and send notifications for:

- 🚀 Position Opened
- ✅ Position Closed
- 🔄 Position Changed
- 📥 Deposits (ETH, BTC, tokens)
- 📤 Withdrawals (ETH, BTC, tokens)

## Requirements

- Python 3.6+
- requests>=2.25.1
- schedule>=1.1.0
- web3>=5.28.0
- python-dotenv>=0.19.0

## Project Structure

```
WhaleWallet/
├── main.py                    # Main application entry point
├── wallet_tracker.py          # Wallet and position tracking logic
├── notification_system.py     # Telegram & console notifications
├── config.py                  # Configuration file
├── config.example.py          # Example configuration template
├── utils.py                   # Utility functions
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
├── get_chat_id.py             # Helper to get Telegram chat ID
├── telegram_helper.py         # Telegram utility functions
├── telegram_setup.py          # Interactive Telegram setup
├── test_notification.py       # Test notification system
├── debug_positions.py         # Debug position tracking
└── README.md                  # This file
```

## Helper Scripts

- **get_chat_id.py**: Simple script to retrieve your Telegram chat ID
- **telegram_helper.py**: Advanced Telegram bot utilities
- **telegram_setup.py**: Interactive setup for Telegram bot configuration
- **test_notification.py**: Test your notification setup
- **debug_positions.py**: Debug and view current positions

## Security Notes

- Never commit `.env` file with sensitive data to version control
- Use `.env.example` as a template for your environment variables
- Keep your API keys and bot tokens secure
- The `.env` file is already included in `.gitignore`
