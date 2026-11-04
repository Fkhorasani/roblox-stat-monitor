
import os
import json
import time
from datetime import datetime

from config import (
  INTERVAL_MINUTES,
  DATA_DIRECTORY,
  PREVIOUS_STATS_FILE
)

from roblox_api import fetch_all_stats
from discord_webhook import send_discord_webhook


def load_previous_stats():
  if not os.path.exists(PREVIOUS_STATS_FILE):
    return None

  try:
    with open(PREVIOUS_STATS_FILE, "r") as file:
      return json.load(file)

  except (json.JSONDecodeError, OSError):
    print("[Storage] Could not read previous stats.")
    return None


def save_stats(stats):
  os.makedirs(DATA_DIRECTORY, exist_ok=True)

  temp_file = PREVIOUS_STATS_FILE + ".tmp"

  with open(temp_file, "w") as file:
    json.dump(stats, file, indent=2)

  os.replace(temp_file, PREVIOUS_STATS_FILE)


def print_stats(stats):
  print("\n" + "=" * 50)
  print("           VALORIA STATISTICS")
  print("=" * 50)

  print(f"Game: {stats['game_name']}")
  print(f"Active Players: {stats['active_players']:,}")
  print(f"Total Visits: {stats['total_visits']:,}")
  print(f"Favorites: {stats['favorites']:,}")
  print(f"Likes: {stats['likes']:,}")
  print(f"Public Servers: {stats['public_servers']}")
  print(
    f"Players in Listed Servers: "
    f"{stats['players_in_listed_servers']}"
  )

  print("\n" + "-" * 50)
  print("           SERVER BREAKDOWN")
  print("-" * 50)

  for index, server in enumerate(
    sorted(
      stats["server_list"],
      key=lambda item: item["players"],
      reverse=True
    ),
    1
  ):
    print(
      f"Server #{index}: "
      f"{server['players']}/{server['max_players']} "
      f"({server['occupancy']}%)"
    )

  if not stats["pagination_complete"]:
    print("\nWARNING: Server listing is incomplete.")

  print("=" * 50)


def run_monitor():
  print("\n[Monitor] Starting Valoria monitoring...")

  previous_stats = load_previous_stats()

  print("[Monitor] Fetching Roblox statistics...")

  stats = fetch_all_stats()

  print_stats(stats)

  print("\n[Monitor] Sending Discord webhook...")

  send_discord_webhook(stats, previous_stats)

  # Save only after a successful Discord delivery.
  save_stats(stats)

  print("[Monitor] Statistics saved successfully.")


def main():
  os.makedirs(DATA_DIRECTORY, exist_ok=True)

  print("=" * 50)
  print("       VALORIA ROBLOX MONITOR")
  print("=" * 50)

  print(f"Monitoring interval: {INTERVAL_MINUTES} minutes")
  print("Press CTRL+C to stop.\n")

  while True:
    start_time = time.monotonic()

    try:
      print(
        f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
      )

      run_monitor()

    except KeyboardInterrupt:
      raise

    except Exception as error:
      print(f"\n[ERROR] {type(error).__name__}: {error}")
      print("[Monitor] Will retry at the next interval.")

    elapsed = time.monotonic() - start_time

    wait_seconds = max(
      0,
      INTERVAL_MINUTES * 60 - elapsed
    )

    print(
      f"\n[Monitor] Next update in "
      f"{wait_seconds / 60:.1f} minutes."
    )

    try:
      time.sleep(wait_seconds)

    except KeyboardInterrupt:
      raise


if __name__ == "__main__":
  try:
    main()

  except KeyboardInterrupt:
    print("\n[Monitor] Monitoring stopped.")
