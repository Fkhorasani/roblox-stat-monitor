
import requests
from datetime import datetime, timezone

from config import DISCORD_WEBHOOK_URL


def format_number(number):
  return f"{number:,}"


def calculate_change(current, previous):
  if previous is None:
    return ""

  difference = current - previous

  if difference > 0:
    return f"📈 +{format_number(difference)}"

  if difference < 0:
    return f"📉 {format_number(difference)}"

  return "➖ No change"


def get_occupancy_emoji(occupancy):
  if occupancy >= 90:
    return "🔴"

  if occupancy >= 70:
    return "🟡"

  return "🟢"


def create_summary_embed(stats, previous_stats=None):
  previous_stats = previous_stats or {}

  timestamp = datetime.now(timezone.utc).isoformat()

  metrics = [
    ("👥 Active Players", "active_players"),
    ("👣 Total Visits", "total_visits"),
    ("❤️ Favorites", "favorites"),
    ("👍 Likes", "likes"),
    ("🌐 Public Servers", "public_servers")
  ]

  embed_fields = []

  for label, key in metrics:
    current = stats[key]
    previous = previous_stats.get(key)

    value = format_number(current)
    change = calculate_change(current, previous)

    embed_fields.append({
      "name": label,
      "value": f"**{value}**\n{change}",
      "inline": True
    })

  embed_fields.extend([
    {
      "name": "📊 Players in Listed Servers",
      "value": format_number(
        stats["players_in_listed_servers"]
      ),
      "inline": True
    },
    {
      "name": "🎮 Maximum Players per Server",
      "value": format_number(
        stats["max_players_per_server"]
      ),
      "inline": True
    },
    {
      "name": "📋 Server Listing",
      "value": (
        "Complete"
        if stats["pagination_complete"]
        else "Partial (page limit reached)"
      ),
      "inline": True
    }
  ])

  return {
    "title": f"📊 {stats['game_name']} - Live Statistics",
    "url": (
      f"https://www.roblox.com/games/"
      f"{stats['place_id']}"
    ),
    "color": 0x5865F2,
    "fields": embed_fields,
    "footer": {
      "text": "Valoria Statistics Monitor"
    },
    "timestamp": timestamp
  }


def create_server_embeds(stats):
  server_list = sorted(
    stats["server_list"],
    key=lambda server: server["players"],
    reverse=True
  )

  embeds = []

  # Discord allows up to 25 fields per embed.
  # Use 20 to leave room for future additions.
  chunk_size = 20

  for start in range(0, len(server_list), chunk_size):
    chunk = server_list[start:start + chunk_size]

    fields = []

    for index, server in enumerate(chunk, start + 1):
      occupancy = server["occupancy"]
      emoji = get_occupancy_emoji(occupancy)

      fields.append({
        "name": f"Server #{index}",
        "value": (
          f"{emoji} **{server['players']}/"
          f"{server['max_players']} players**\n"
          f"Occupancy: {occupancy}%"
        ),
        "inline": True
      })

    embeds.append({
      "title": (
        f"🖥️ Server Breakdown "
        f"({start + 1}-{start + len(chunk)})"
      ),
      "color": 0x2B2D31,
      "fields": fields,
      "footer": {
        "text": (
          f"Total public servers: "
          f"{stats['public_servers']}"
        )
      }
    })

  return embeds


def send_discord_webhook(stats, previous_stats=None):
  if not DISCORD_WEBHOOK_URL:
    raise ValueError("Discord webhook URL is missing!")

  embeds = [
    create_summary_embed(stats, previous_stats)
  ]

  embeds.extend(create_server_embeds(stats))

  # Discord allows a maximum of 10 embeds per message.
  for start in range(0, len(embeds), 10):
    embed_batch = embeds[start:start + 10]

    payload = {
      "username": "Valoria Monitor",
      "allowed_mentions": {
        "parse": []
      },
      "embeds": embed_batch
    }

    response = requests.post(
      DISCORD_WEBHOOK_URL,
      json=payload,
      timeout=30
    )

    response.raise_for_status()

  print("[Discord] Webhook sent successfully!")
