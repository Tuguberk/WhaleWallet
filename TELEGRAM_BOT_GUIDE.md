# 🤖 Multi-User Telegram Bot Guide

## Overview

WhaleWallet now supports **multi-user subscriptions**! Instead of configuring a single chat ID, the bot can accept `/start` commands from any user or group, allowing multiple people to receive wallet notifications.

## How It Works

1. **Dynamic Subscriptions**: Users send `/start` to the bot to subscribe
2. **Group Support**: Add the bot to a group and send `/start` to get notifications there
3. **Persistent Storage**: Subscribers are saved in `subscribers.json`
4. **Broadcast Notifications**: All wallet events are sent to all active subscribers

## Bot Commands

| Command   | Description                       |
| --------- | --------------------------------- |
| `/start`  | Subscribe to wallet notifications |
| `/stop`   | Unsubscribe from notifications    |
| `/status` | Check your subscription status    |
| `/help`   | Show available commands           |

## Setup Instructions

### 1. Create Your Bot

Talk to [@BotFather](https://t.me/botfather) on Telegram:

```
/newbot
```

Follow the instructions and **copy your bot token**.

### 2. Configure Environment

Edit your `.env` file:

```bash
# Only bot token is required - TELEGRAM_CHAT_ID is optional now!
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

**Note**: You no longer need to set `TELEGRAM_CHAT_ID`!

### 3. Start the Tracker

```bash
# Docker
docker-compose up -d

# Manual
python3 main.py
```

### 4. Subscribe to Notifications

1. **Find your bot** on Telegram (search for the username you chose)
2. **Send `/start`** to the bot
3. **You're subscribed!** You'll receive all wallet notifications

## Using in Groups

### Add Bot to a Group

1. Create a group or open an existing one
2. Click on group name → **Add Members**
3. Search for your bot and add it
4. Send `/start` in the group
5. The **entire group** will now receive notifications!

### Benefits of Group Mode

- 📱 **Team Monitoring**: Share wallet updates with your team
- 💬 **Discussion**: Discuss trades and positions in real-time
- 🔔 **Collective Alerts**: Everyone stays informed simultaneously
- 👥 **Multiple Subscribers**: Different groups can subscribe independently

## Subscriber Management

### View Active Subscribers

Check the console output when starting:

```
🤖 Telegram Bot: Active (3 subscribers)
💡 Users can send /start to subscribe to notifications
```

### Subscriber Data

Subscribers are stored in `subscribers.json`:

```json
{
  "subscribers": [123456789, 987654321, -1001234567890],
  "updated_at": "2025-10-28 15:30:00"
}
```

**Note**: Negative IDs are group chats, positive IDs are individual users.

### Removing Subscribers

Users can unsubscribe anytime:

```
/stop
```

Or manually edit `subscribers.json` (requires restart).

## Docker Persistence

Subscribers are automatically persisted in Docker:

```yaml
volumes:
  - ./subscribers.json:/app/subscribers.json
```

This means subscribers survive container restarts! 🎉

## Example Workflow

### Individual User

```
You: /start
Bot: 🐋 Welcome to WhaleWallet Tracker!
     ✅ You are now subscribed to wallet updates.
     📊 You will receive notifications for:
     • Balance changes
     • Position updates
     • Deposits & Withdrawals
     • Trading activity

[10 minutes later...]
Bot: 📥 DEPOSIT DETECTED
     Amount: 5.0 ETH
     Value: $14,000
     New Balance: 15.5 ETH
```

### Group Chat

```
Admin: /start
Bot: 🐋 Welcome to WhaleWallet Tracker!
     ✅ You are now subscribed to wallet updates.

👥 New group subscription: Crypto Trading Team (ID: -1001234567890)

[Later...]
Bot: 🚀 POSITION OPENED
     Asset: BTC-USD
     Type: Long
     Size: 1.5 BTC
     Entry: $45,000

Member1: Nice entry!
Member2: Let's see how this plays out
```

## Security Considerations

### Public Bots

⚠️ **Warning**: Anyone who finds your bot can subscribe to it!

**Solutions**:

1. **Private Bot**: Don't share your bot's username publicly
2. **Whitelist**: Modify code to check subscriber IDs before accepting
3. **Password**: Add custom authentication in `telegram_bot.py`

### Recommended for Public Bots

If you want a whitelist, edit `telegram_bot.py`:

```python
# Add at the top
ALLOWED_USERS = [123456789, 987654321]  # Your trusted user IDs
ALLOWED_GROUPS = [-1001234567890]  # Your trusted group IDs

# In _process_update method
def _process_update(self, update: Dict[str, Any]):
    chat_id = message.get('chat', {}).get('id')

    # Check whitelist
    if chat_id not in ALLOWED_USERS and chat_id not in ALLOWED_GROUPS:
        self.send_message(chat_id, "❌ Unauthorized. This bot is private.")
        return
```

## Troubleshooting

### Bot Not Responding

**Check:**

1. Bot token is correct in `.env`
2. Bot is actually running (check logs)
3. You sent `/start` to the correct bot

**Debug:**

```bash
# Check logs
docker-compose logs -f

# Or for manual mode
python3 telegram_bot.py YOUR_BOT_TOKEN
```

### Subscribers Not Persisting

**Check:**

1. `subscribers.json` file permissions
2. Docker volume is mounted correctly
3. File exists in the correct directory

**Fix:**

```bash
# Create file manually
echo '{"subscribers": [], "updated_at": ""}' > subscribers.json

# Fix permissions
chmod 644 subscribers.json

# Restart container
docker-compose restart
```

### Group Not Receiving Messages

**Check:**

1. Bot has been added to the group
2. `/start` was sent in the group
3. Bot has permission to send messages

**Fix:**

1. Remove and re-add the bot
2. Make bot an admin (optional but helps)
3. Check bot privacy settings with @BotFather

## Advanced Features

### Broadcast Test

Test broadcasting to all subscribers:

```python
python3 -c "
from telegram_bot import TelegramBotManager
bot = TelegramBotManager('YOUR_BOT_TOKEN')
result = bot.broadcast_message('🧪 Test notification')
print(f'Sent to {result[\"success\"]}/{result[\"total\"]} subscribers')
"
```

### Custom Commands

Add more commands in `telegram_bot.py`:

```python
elif text.startswith('/balance'):
    # Get current balance and send to user
    balance = get_wallet_balance()  # Your function
    self.send_message(chat_id, f"💰 Current Balance: {balance} ETH")

elif text.startswith('/positions'):
    # Get current positions
    positions = get_positions()  # Your function
    self.send_message(chat_id, format_positions(positions))
```

## Migration Guide

### From Single Chat ID to Multi-User

If you're upgrading from the old single-chat-id system:

1. **Keep your old setup working**: Leave `TELEGRAM_CHAT_ID` in `.env`
2. **Start the new bot**: Bot will automatically accept new subscribers
3. **Old chat keeps working**: No interruption to existing notifications
4. **Gradually migrate**: Tell users to send `/start` to subscribe
5. **Remove CHAT_ID**: Once everyone has subscribed, remove `TELEGRAM_CHAT_ID` from `.env`

### Backwards Compatibility

The system is fully backwards compatible. If you set `TELEGRAM_CHAT_ID`, it will still work as before, but you'll also get the multi-user functionality!

## Best Practices

✅ **Do:**

- Keep your bot token private
- Test with `/start` after setup
- Monitor subscriber count
- Backup `subscribers.json`
- Use groups for team monitoring

❌ **Don't:**

- Share bot username publicly (unless intended)
- Forget to add volume mount for `subscribers.json`
- Ignore failed send notifications
- Use same bot for multiple purposes

---

## Need Help?

- 📚 Check main [README.md](./README.md)
- 🐳 See [DOCKER_GUIDE.md](./DOCKER_GUIDE.md)
- 🇹🇷 Turkish guide: [KULLANIM_KILAVUZU.md](./KULLANIM_KILAVUZU.md)
- 🐛 [Open an issue](https://github.com/Tuguberk/WhaleWallet/issues)

**Happy monitoring! 🐋📊**
