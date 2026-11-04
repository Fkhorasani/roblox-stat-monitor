import os
from dotenv import load_dotenv

load_dotenv()

PLACE_ID = int(os.getenv("ROBLOX_PLACE_ID", "0"))
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

INTERVAL_MINUTES = 15
ROBLOX_BASE_URL = "https://games.roblox.com"
ROBLOX_HEADERS = {
  "User-Agent": "Mozilla/5.0"
}

MAX_SERVER_PAGES = 100

DATA_DIRECTORY = "data"
PREVIOUS_STATS_FILE = f"{DATA_DIRECTORY}/previous_stats.json"