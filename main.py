import discord
import requests
import os
from subscribers_manager import get_all_pushover_keys, add_subscriber, remove_subscriber

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
PUSHOVER_APP_TOKEN = os.getenv("PUSHOVER_APP_TOKEN")

# === Discord Intents ===
intents = discord.Intents.default()
intents.message_content = True
intents.members = True          # Required: lets the bot fetch member lists to verify DM users

# Create client
client = discord.Client(intents=intents)


def send_pushover(message: str, user_keys: list[str]) -> bool:
    """
    Send a Pushover alert to each user_key in user_keys.
    Returns True if all succeed, False otherwise.
    """
    ok = True
    for key in user_keys:
        payload = {
            'token': PUSHOVER_APP_TOKEN,
            'user': key,
            'message': message,
            'title': 'DEGEN Alert',
            'priority': +1
        }
        resp = requests.post('https://api.pushover.net/1/messages.json', data=payload)
        if resp.status_code != 200:
            print(f"Failed to send to {key}: {resp.status_code} {resp.text}")
            ok = False
    return ok


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")


async def is_member_of_any_guild(user: discord.User) -> bool:
    """
    Returns True if the user shares at least one guild with this bot.
    Relies on the 'members' privileged intent being enabled.
    """
    for guild in client.guilds:
        if guild.get_member(user.id) is not None:
            return True
    return False


async def handle_dm_only_violation(message: discord.Message, command: str):
    """
    Called when a DM-only command is used in a public channel.
    Deletes the message immediately and warns the user via DM.
    """
    try:
        await message.delete()
    except discord.Forbidden:
        pass  # Bot lacks Manage Messages permission; still warn the user
    try:
        await message.author.send(
            f"🔒 **Your message was deleted to protect your privacy.**\n"
            f"Please only use `{command}` in a **private DM with me**, "
            f"never in a public channel."
        )
    except discord.Forbidden:
        pass  # User has DMs disabled; nothing more we can do


@client.event
async def on_message(message: discord.Message):
    # Ignore messages from the bot itself
    if message.author.id == client.user.id:
        return

    content = message.content.strip()
    content_lower = content.lower()
    is_dm = isinstance(message.channel, discord.DMChannel)

    # ------------------------------------------------------------------ #
    #  SUBSCRIBE COMMAND                                                   #
    # ------------------------------------------------------------------ #
    if content_lower.startswith('!subscribe'):

        if not is_dm:
            await handle_dm_only_violation(message, '!subscribe <your_pushover_key>')
            return

        parts = content.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            await message.channel.send(
                "⚠️ Usage: `!subscribe <your_pushover_key>`\n"
                "Example: `!subscribe abc123xyz`"
            )
            return

        pushover_key = parts[1].strip()

        in_guild = await is_member_of_any_guild(message.author)
        if not in_guild:
            await message.channel.send(
                "🚫 You must be a member of the Discord server to subscribe."
            )
            return

        discord_id = str(message.author.id)
        _, status = add_subscriber(discord_id, pushover_key)

        if status == 'already_subscribed':
            await message.channel.send("ℹ️ You're already subscribed with that Pushover key. No changes made.")
        elif status == 'updated':
            await message.channel.send("✅ Your Pushover key has been **updated** successfully.")
        else:
            await message.channel.send("✅ You've been **subscribed** successfully! You'll now receive alerts.")

        return

    # ------------------------------------------------------------------ #
    #  UNSUBSCRIBE COMMAND                                                 #
    # ------------------------------------------------------------------ #
    if content_lower.startswith('!unsubscribe'):

        if not is_dm:
            await handle_dm_only_violation(message, '!unsubscribe')
            return

        discord_id = str(message.author.id)
        _, status = remove_subscriber(discord_id)

        if status == 'not_found':
            await message.channel.send("ℹ️ You're not currently subscribed. Nothing to remove.")
        else:
            await message.channel.send("✅ You've been **unsubscribed** successfully. You won't receive any more alerts. Sad to see you go.")

        return

    # ------------------------------------------------------------------ #
    #  ALERT COMMAND                                                       #
    # ------------------------------------------------------------------ #
    if not content_lower.startswith('!alert '):
        return

    alert = content[len('!alert '):].strip()
    if not alert:
        await message.channel.send("⚠️ Please provide a message after `!alert`.")
        return

    keys = get_all_pushover_keys()
    if not keys:
        await message.channel.send("⚠️ No subscribers found.")
        return

    success = send_pushover(alert, keys)
    if success:
        await message.channel.send(f"✅ Alert sent to {len(keys)} subscribers.")
    else:
        await message.channel.send(f"❌ Some alerts failed (see console output).")


if __name__ == '__main__':
    if not DISCORD_BOT_TOKEN or not PUSHOVER_APP_TOKEN:
        print("Error: Set DISCORD_BOT_TOKEN and PUSHOVER_APP_TOKEN as environment variables.")
        exit(1)
    client.run(DISCORD_BOT_TOKEN)