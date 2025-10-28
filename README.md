<div align="center">

# 🐋 WhaleWallet

### _Professional Crypto Portfolio Tracker & Alert System_

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Monitor your crypto portfolio like a whale 🐳 Get instant alerts on position changes, deposits, withdrawals, and balance movements!**

[Features](#-features) • [Quick Start](#-quick-start) • [Configuration](#%EF%B8%8F-configuration) • [Documentation](#-documentation)

</div>

---

## 🎯 Overview

WhaleWallet is a professional-grade cryptocurrency portfolio monitoring system that tracks your Ethereum wallet and Hyperliquid perpetual positions in real-time. Get instant Telegram notifications for every important event - never miss a trade, deposit, or withdrawal again!

### 💡 Why WhaleWallet?

- **🔍 Smart Monitoring**: Intelligent change detection with configurable thresholds
- **⚡ Real-time Alerts**: Instant Telegram notifications for all portfolio events
- **🛡️ Secure**: No hardcoded secrets, environment-based configuration
- **🐳 Docker Ready**: One-command deployment with production-grade setup
- **📊 Multi-Chain**: Supports Ethereum mainnet and Hyperliquid perpetuals
- **🎛️ Customizable**: Flexible notification settings and check intervals

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 💰 Wallet Monitoring

- ✅ ETH balance tracking
- ✅ ERC-20 token transfers
- ✅ Deposit detection
- ✅ Withdrawal alerts
- ✅ Transaction history
- ✅ Balance change thresholds

</td>
<td width="50%">

### 📈 Position Tracking

- ✅ Hyperliquid perpetuals
- ✅ Position open/close detection
- ✅ Size change alerts
- ✅ PnL monitoring
- ✅ Leverage tracking
- ✅ Multi-position support

</td>
</tr>
</table>

### 🔔 Smart Notifications

WhaleWallet sends Telegram alerts **only** when important events occur:

| Event                   | Notification Type         | Example                                   |
| ----------------------- | ------------------------- | ----------------------------------------- |
| 🚀 **Position Opened**  | New position detected     | "New BTC-USD Long: $50,000 @ 10x"         |
| ✅ **Position Closed**  | Position fully closed     | "Closed ETH-USD Short: +$1,234 PnL"       |
| 🔄 **Position Changed** | Size/leverage modified    | "ETH-USD position +2.5 ETH (15.0 → 17.5)" |
| 📥 **Deposit**          | Funds added to wallet     | "Deposit: 5.0 ETH"                        |
| 📤 **Withdrawal**       | Funds removed             | "Withdrawal: 1000 USDC"                   |
| 💸 **Balance Change**   | Significant balance shift | "Balance: 10.5 ETH → 15.2 ETH (+4.7)"     |

---

## 🚀 Quick Start

### Option 1: Docker (Recommended) 🐳

The fastest way to get started! Everything is containerized and ready to go.

```bash
# 1️⃣ Clone the repository
git clone https://github.com/Tuguberk/WhaleWallet.git
cd WhaleWallet

# 2️⃣ Configure your environment
cp .env.example .env
nano .env  # Add your API keys and wallet address

# 3️⃣ Run the quick start script
./docker-start.sh

# OR manually with Docker Compose
docker-compose up -d

# 4️⃣ View live logs
docker-compose logs -f
```

**That's it!** 🎉 Your wallet is now being monitored 24/7!

📖 **Need help?** Check out the [Complete Docker Guide](./DOCKER_GUIDE.md)

---

### Option 2: Manual Installation 🔧

For development or if you prefer running without Docker.

```bash
# 1️⃣ Clone and setup virtual environment
git clone https://github.com/Tuguberk/WhaleWallet.git
cd WhaleWallet
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Configure environment
cp .env.example .env
nano .env  # Add your configuration

# 4️⃣ Run the tracker
python3 main.py
```

---

## ⚙️ Configuration

### Step 1: Create Telegram Bot 🤖

1. **Open Telegram** and search for [@BotFather](https://t.me/botfather)
2. **Send** `/newbot` command
3. **Choose** a name for your bot (e.g., "My Whale Tracker")
4. **Choose** a username (e.g., "mywhale_tracker_bot")
5. **Copy** the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID 💬

```bash
# Option A: Using helper script
python3 get_chat_id.py

# Option B: Manual method
# 1. Send a message to your bot in Telegram
# 2. Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
# 3. Look for "chat":{"id": YOUR_CHAT_ID}
```

### Step 3: Get API Keys 🔑

#### Etherscan API Key

1. Go to [Etherscan](https://etherscan.io/)
2. Create account / Login
3. Navigate to **API-KEYs** section
4. Create new API key (Free tier is sufficient)

#### Wallet Address

- Your Ethereum wallet address you want to monitor
- Example: `0x1234567890123456789012345678901234567890`

### Step 4: Configure Environment Variables 📝

Create `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your values:

```bash
# 🔑 Required Configuration
WALLET_ADDRESS=0xYourWalletAddressHere
ETHERSCAN_API_KEY=YourEtherscanAPIKey
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789

# ⚙️ Optional Settings (with defaults)
CHECK_INTERVAL=600                    # Check every 10 minutes
BALANCE_CHANGE_THRESHOLD=0.1          # Alert if balance changes by 0.1 ETH
POSITION_CHANGE_THRESHOLD=5           # Alert if position changes by 5%
ENABLE_NOTIFICATIONS=true             # Enable/disable notifications
```

### Environment Variables Explained

| Variable                    | Required | Description                | Example        |
| --------------------------- | -------- | -------------------------- | -------------- |
| `WALLET_ADDRESS`            | ✅ Yes   | Ethereum wallet to monitor | `0x1234...`    |
| `ETHERSCAN_API_KEY`         | ✅ Yes   | API key from Etherscan     | `ABC123...`    |
| `TELEGRAM_BOT_TOKEN`        | ✅ Yes   | Token from @BotFather      | `123:ABC...`   |
| `TELEGRAM_CHAT_ID`          | ✅ Yes   | Your Telegram chat ID      | `123456789`    |
| `CHECK_INTERVAL`            | ❌ No    | Seconds between checks     | `600` (10 min) |
| `BALANCE_CHANGE_THRESHOLD`  | ❌ No    | Min ETH change to alert    | `0.1`          |
| `POSITION_CHANGE_THRESHOLD` | ❌ No    | Min % change to alert      | `5`            |
| `ENABLE_NOTIFICATIONS`      | ❌ No    | Toggle notifications       | `true`         |

---

## 🎮 Usage

### Running the Tracker

#### 🐳 Docker (Recommended)

```bash
# Start the tracker
docker-compose up -d

# View live logs
docker-compose logs -f

# Check status
docker-compose ps

# Stop the tracker
docker-compose stop

# Restart the tracker
docker-compose restart

# Stop and remove container
docker-compose down
```

#### 🔧 Manual Mode

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run continuous monitoring (checks every 10 minutes)
python3 main.py

# Run one-time check
python3 main.py --check

# Run with debug output
python3 main.py --debug
```

### Notification Examples 📱

<details>
<summary>Click to see example notifications</summary>

```
🚀 Position Opened
Asset: BTC-USD
Type: Long
Size: 1.5 BTC
Entry: $45,000
Leverage: 10x
Value: $67,500
```

```
✅ Position Closed
Asset: ETH-USD
Type: Short
Size: 25 ETH
Exit: $2,800
PnL: +$1,234.56 (+4.5%)
```

```
� Deposit Detected
Amount: 5.0 ETH
Value: $14,000
New Balance: 15.5 ETH
```

```
�🔄 Position Changed
Asset: SOL-USD
Change: +150 SOL
Old Size: 500 SOL → New Size: 650 SOL
Leverage: 5x → 7x
```

</details>

---

## 🏗️ Architecture

```
WhaleWallet/
├── � Docker Configuration
│   ├── Dockerfile                    # Container definition
│   ├── docker-compose.yml            # Development setup
│   ├── docker-compose.prod.yml       # Production setup
│   └── .dockerignore                 # Build optimization
│
├── 🎯 Core Application
│   ├── main.py                       # Main application entry
│   ├── wallet_tracker.py             # Wallet monitoring logic
│   ├── notification_system.py        # Telegram notifications
│   └── utils.py                      # Helper functions
│
├── ⚙️ Configuration
│   ├── config.py                     # Configuration loader
│   ├── .env.example                  # Environment template
│   └── requirements.txt              # Python dependencies
│
├── �️ Helper Scripts
│   ├── get_chat_id.py               # Get Telegram chat ID
│   ├── telegram_helper.py           # Telegram utilities
│   ├── security_check.py            # Security scanner
│   └── docker-start.sh              # Quick start script
│
└── 📚 Documentation
    ├── README.md                     # This file
    ├── DOCKER_GUIDE.md              # Docker deployment guide
    ├── KULLANIM_KILAVUZU.md         # Turkish usage guide
    └── SECURITY_REPORT.md           # Security audit report
```

---

## 📚 Documentation

| Document                                              | Description                                            |
| ----------------------------------------------------- | ------------------------------------------------------ |
| 🐳 [**DOCKER_GUIDE.md**](./DOCKER_GUIDE.md)           | Complete Docker deployment guide with production setup |
| 🇹🇷 [**KULLANIM_KILAVUZU.md**](./KULLANIM_KILAVUZU.md) | Turkish usage guide (Türkçe kullanım kılavuzu)         |
| 🔒 [**SECURITY_REPORT.md**](./SECURITY_REPORT.md)     | Security audit and best practices                      |
| 📝 [**CHANGELOG.md**](./CHANGELOG.md)                 | Version history and changes                            |

---

## 🔧 Advanced Configuration

### Custom Check Intervals

Modify check frequency in `.env`:

```bash
CHECK_INTERVAL=300  # Check every 5 minutes
CHECK_INTERVAL=900  # Check every 15 minutes
CHECK_INTERVAL=1800 # Check every 30 minutes
```

### Notification Thresholds

Fine-tune when you receive alerts:

```bash
# Only alert if ETH balance changes by 0.5 or more
BALANCE_CHANGE_THRESHOLD=0.5

# Only alert if position changes by 10% or more
POSITION_CHANGE_THRESHOLD=10
```

### Docker Production Deployment

For production with enhanced security:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

Features:

- 🔒 Read-only filesystem
- 🛡️ No new privileges
- 📊 Resource limits (1 CPU, 512MB RAM)
- 📁 Compressed log rotation
- 🌐 Isolated network

---

## 🛠️ Troubleshooting

<details>
<summary><b>❌ Module 'config' not found</b></summary>

**Solution:** Rebuild Docker image

```bash
docker-compose build --no-cache
docker-compose up -d
```

</details>

<details>
<summary><b>❌ Telegram bot not responding</b></summary>

**Check:**

1. Bot token is correct in `.env`
2. Chat ID is correct
3. You've sent `/start` to the bot

**Test:**

```bash
python3 test_notification.py
```

</details>

<details>
<summary><b>❌ Etherscan API errors</b></summary>

**Common causes:**

- Invalid API key
- Rate limit exceeded (free tier: 5 calls/sec)
- Network issues

**Solution:** Wait a few minutes and check API key

</details>

<details>
<summary><b>🐳 Docker container keeps restarting</b></summary>

**Check logs:**

```bash
docker-compose logs whalewallet
```

**Common issues:**

- Missing `.env` file
- Invalid configuration values
- Network connectivity issues
</details>

---

## 🔒 Security Best Practices

✅ **Do:**

- Store secrets in `.env` file (never commit to Git)
- Use strong, unique API keys
- Regularly rotate your Telegram bot token
- Keep dependencies updated: `pip install -r requirements.txt --upgrade`
- Run security scan: `python3 security_check.py`

❌ **Don't:**

- Commit `.env` file to version control
- Share your bot token publicly
- Use the same token for multiple projects
- Hardcode secrets in code
- Run as root in production

---

## 📦 Dependencies

| Package         | Version | Purpose                         |
| --------------- | ------- | ------------------------------- |
| `requests`      | ≥2.25.1 | HTTP requests for APIs          |
| `schedule`      | ≥1.1.0  | Scheduled task execution        |
| `web3`          | ≥5.28.0 | Ethereum blockchain interaction |
| `python-dotenv` | ≥0.19.0 | Environment variable management |

**Python Version:** 3.11+ (3.6+ supported)

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch: `git checkout -b feature/amazing-feature`
3. 💾 Commit your changes: `git commit -m 'Add amazing feature'`
4. 📤 Push to branch: `git push origin feature/amazing-feature`
5. 🎉 Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/WhaleWallet.git
cd WhaleWallet

# Create development environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install development dependencies
pip install pytest black flake8 mypy

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License - Free to use, modify, and distribute
Copyright (c) 2025 WhaleWallet
```

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=Tuguberk/WhaleWallet&type=Date)](https://star-history.com/#Tuguberk/WhaleWallet&Date)

---

## 📧 Support & Contact

- 🐛 **Bug Reports:** [Open an issue](https://github.com/Tuguberk/WhaleWallet/issues)
- 💡 **Feature Requests:** [Start a discussion](https://github.com/Tuguberk/WhaleWallet/discussions)
- 📧 **Email:** [your-email@example.com](mailto:your-email@example.com)
- 💬 **Telegram:** [@YourTelegramHandle](https://t.me/YourTelegramHandle)

---

## 🙏 Acknowledgments

- 🦄 **Etherscan** - For providing excellent blockchain APIs
- 🔷 **Hyperliquid** - For perpetual futures tracking capabilities
- 💬 **Telegram** - For reliable bot API
- 🐍 **Python Community** - For amazing libraries and tools

---

<div align="center">

### Made with ❤️ by the WhaleWallet Team

**Track like a whale, stay ahead of the market! 🐋📈**

[⬆ Back to Top](#-whalewallet)

</div>
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
