import json
from pathlib import Path

# Path to the JSON file containing subscriber entries
dataset = Path("subscribers.json")


def load_subscribers():
    """
    Load subscriber entries from the JSON file.
    Expected format: a list of objects, each with:
      - discord_id: str
      - pushover_key: str
    Returns a list of dicts.
    """
    try:
        data = json.loads(dataset.read_text())
        if not isinstance(data, list):
            raise ValueError("Subscribers JSON must be a list of objects")
        for entry in data:
            if 'discord_id' not in entry or 'pushover_key' not in entry:
                raise ValueError("Each entry requires 'discord_id' and 'pushover_key'")
        return data
    except FileNotFoundError:
        print(f"⚠️ File not found: {dataset}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in {dataset}: {e}")
        return []
    except Exception as e:
        print(f"❌ Error loading subscribers: {e}")
        return []


def get_all_pushover_keys():
    """
    Return a list of all pushover_key strings from subscribers.json.
    """
    return [entry['pushover_key'] for entry in load_subscribers()]


def add_subscriber(discord_id: str, pushover_key: str) -> tuple[bool, str]:
    """
    Add a new subscriber to subscribers.json.
    - If the discord_id already exists with the same key: no-op, returns (False, 'already_subscribed').
    - If the discord_id exists with a different key: updates the key, returns (True, 'updated').
    - Otherwise: appends a new entry, returns (True, 'added').
    """
    subs = load_subscribers()

    for entry in subs:
        if entry['discord_id'] == discord_id:
            if entry['pushover_key'] == pushover_key:
                return False, 'already_subscribed'
            # Update existing key
            entry['pushover_key'] = pushover_key
            dataset.write_text(json.dumps(subs, indent=2))
            return True, 'updated'

    # New subscriber
    subs.append({'discord_id': discord_id, 'pushover_key': pushover_key})
    dataset.write_text(json.dumps(subs, indent=2))
    return True, 'added'


def remove_subscriber(discord_id: str) -> tuple[bool, str]:
    """
    Remove a subscriber from subscribers.json by discord_id.
    - discord_id found  → removes all matching entries, returns (True, 'removed')
    - discord_id absent → returns (False, 'not_found')
    """
    subs = load_subscribers()
    filtered = [entry for entry in subs if entry['discord_id'] != discord_id]

    if len(filtered) == len(subs):
        return False, 'not_found'

    dataset.write_text(json.dumps(filtered, indent=2))
    return True, 'removed'


def list_subscribers():
    """Prints all subscriber entries."""
    subs = load_subscribers()
    if not subs:
        print("No subscribers found.")
        return
    for entry in subs:
        print(f"Discord ID: {entry['discord_id']} -> Pushover Key: {entry['pushover_key']}")


if __name__ == '__main__':
    list_subscribers()