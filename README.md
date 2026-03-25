# ALERT IT — Discord → Pushover Alert Bot

A Discord bot that lets you broadcast instant Pushover notifications to a list of subscribers. Users manage their own subscriptions privately via DM.

---

## How It Works

1. Users DM the bot with their Pushover user key to subscribe.
2. You (or anyone with access) type `!alert <message>` in the Discord server.
3. Every subscriber receives an instant Pushover notification on their device.

---

## Setup

### 1. Prerequisites

- Python 3.12+
- A [Discord bot token](https://discord.com/developers/applications)
- A [Pushover](https://pushover.net) account and application token

### 2. Clone the repo

```bash
git clone https://github.com/XyleExile/ALERT-IT
cd your-repo
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Enable Privileged Intents

In the [Discord Developer Portal](https://discord.com/developers/applications), go to your bot's **Bot** tab and enable:

- ✅ **Message Content Intent**
- ✅ **Server Members Intent**

Both are required for the bot to read messages and verify guild membership from DMs.

### 5. Set environment variables

```bash
export DISCORD_BOT_TOKEN=your_discord_bot_token
export PUSHOVER_APP_TOKEN=your_pushover_app_token
```

### 6. Set up the subscribers file

`subscribers.json` is excluded from the repo to protect user data. Create it from the example file before running the bot:

```bash
cp subscribers.json.example subscribers.json
```

You can leave it as-is — the bot will populate it automatically as users subscribe via DM. If you want to seed it manually, follow the format inside `subscribers.json.example`.

### 7. Run the bot

```bash
python dyor_arba.py
```

---

## Commands

### `!alert <message>`
**Used in:** Any Discord server channel

Sends a Pushover notification to all current subscribers.

```
!alert BTC breaking $100k right now 🚀
```

---

### `!subscribe <pushover_key>`
**Used in:** Private DM with the bot only

Registers your Pushover user key to receive alerts. If you've subscribed before with a different key, it will be updated.

```
!subscribe abc123xyz
```

> ⚠️ If you use this command in a public channel, the bot will **immediately delete your message** and warn you via DM. Never share your Pushover key in public.

---

### `!unsubscribe`
**Used in:** Private DM with the bot only

Removes you from the subscriber list. You will stop receiving all alerts.

```
!unsubscribe
```

> ⚠️ Same as above — using this in a public channel will result in your message being deleted.

---

## File Structure

```
├── main.py                   # Main bot logic and Discord event handlers
├── subscribers_manager.py    # Subscriber CRUD operations (JSON-backed)
├── subscribers.json          # Subscriber data store — gitignored, created from .example
├── subscribers.json.example  # Safe template to copy from when setting up
├── requirements.txt          # Python dependencies
└── .gitignore                # Excludes sensitive files from version control
```

---

## .gitignore

The following `.gitignore` is recommended for this project:

```gitignore
# Sensitive data
subscribers.json
.env

# Python bytecode
__pycache__/
*.pyc
*.pyo

# Virtual environments
.venv/
venv/
env/

# Python packaging
*.egg-info/
dist/
build/
```

> `subscribers.json` is intentionally excluded from version control as it contains real Discord IDs and Pushover keys. Always use `subscribers.json.example` as the committed reference.

---

## Subscribers Data

The `subscribers.json.example` template shows the expected format:

```json
[
  {
    "discord_id": "YOUR_DISCORD_USER_ID",
    "pushover_key": "YOUR_PUSHOVER_USER_KEY"
  }
]
```

You can also add entries manually by editing `subscribers.json` directly while the bot is not running.

---

## Dependencies

| Package | Purpose |
|---|---|
| `discord.py` | Discord bot framework |
| `requests` | HTTP requests to Pushover API |