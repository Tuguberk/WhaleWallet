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
- requests
- schedule

## Security Notes

- Never commit `.env` file with sensitive data to version control
- Use `.env.example` as a template for your environment variables
- Keep your API keys and bot tokens secure
- The `.env` file is already included in `.gitignore`
