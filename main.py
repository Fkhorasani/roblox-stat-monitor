
import json
import os
import sys

from config import (
  DATA_DIRECTORY,
  PREVIOUS_STATS_FILE,
  PLACE_ID,
  DISCORD_WEBHOOK_URL
)
from roblox_api import fetch_all_stats
from discord_webhook import send_discord_webhook


def validate_config():
  if not PLACE_ID:
    raise ValueError("ROBLOX_PLACE_ID is missing or invalid.")

  if not DISCORD_WEBHOOK_URL:
    raise ValueError("DISCORD_WEBHOOK_URL is missing.")


def load_previous_stats():
  if not os.path.exists(PREVIOUS_STATS_FILE):
    print("No previous statistics found. Starting fresh.")
    return None

  try:
    with open(PREVIOUS_STATS_FILE, "r", encoding="utf-8") as file:
      return json.load(file)

  except (json.JSONDecodeError, OSError) as error:
    print(f"Could not load previous statistics: {error}")
    return None


def save_stats(stats):
  os.makedirs(DATA_DIRECTORY, exist_ok=True)

  with open(PREVIOUS_STATS_FILE, "w", encoding="utf-8") as file:
    json.dump(stats, file, indent=2)

  print(f"Statistics saved to {PREVIOUS_STATS_FILE}")


def main():
  print("=" * 45)
  print("       VALORIA STATISTICS MONITOR")
  print("=" * 45)

  validate_config()

  print(f"Place ID: {PLACE_ID}")
  print("Fetching Roblox statistics...")

  previous_stats = load_previous_stats()
  current_stats = fetch_all_stats()

  if not current_stats:
    raise RuntimeError("Failed to retrieve Roblox statistics.")

  print("\nCurrent statistics:")
  print(f"Game: {current_stats.get('game_name', 'Unknown')}")
  print(f"Active players: {current_stats.get('active_players', 0):,}")
  print(f"Total visits: {current_stats.get('total_visits', 0):,}")
  print(f"Favorites: {current_stats.get('favorites', 0):,}")
  print(f"Likes: {current_stats.get('likes', 0):,}")
  print(f"Public servers: {current_stats.get('total_servers', 0):,}")

  print("\nSending Discord notification...")

  send_discord_webhook(current_stats, previous_stats)

  save_stats(current_stats)

  print("\nMonitor completed successfully.")
  print("=" * 45)


if __name__ == "__main__":
  try:
    main()

  except Exception as error:
    print(f"\nERROR: {error}")
    sys.exit(1)
