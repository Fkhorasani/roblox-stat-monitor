
import requests

from config import (
  PLACE_ID,
  ROBLOX_BASE_URL,
  ROBLOX_HEADERS,
  MAX_SERVER_PAGES
)


def get_json(url, params=None):
  response = requests.get(
    url,
    params=params,
    headers=ROBLOX_HEADERS,
    timeout=30
  )

  if response.status_code == 429:
    raise requests.HTTPError(
      "Roblox API rate limit reached",
      response=response
    )

  response.raise_for_status()
  return response.json()


def get_universe_id():
  url = (
    "https://apis.roblox.com/universes/v1/"
    f"places/{PLACE_ID}/universe"
  )

  data = get_json(url)
  return data["universeId"]


def get_game_stats(universe_id):
  data = get_json(
    f"{ROBLOX_BASE_URL}/v1/games",
    {"universeIds": universe_id}
  )

  if not data.get("data"):
    raise ValueError("Roblox game information not found")

  return data["data"][0]


def get_votes(universe_id):
  data = get_json(
    f"{ROBLOX_BASE_URL}/v1/games/votes",
    {"universeIds": universe_id}
  )

  if not data.get("data"):
    raise ValueError("Roblox vote information not found")

  return data["data"][0]


def get_server_stats(place_id):
  cursor = None
  server_list = []
  pages = 0

  while True:
    params = {
      "limit": 100
    }

    if cursor:
      params["cursor"] = cursor

    data = get_json(
      f"{ROBLOX_BASE_URL}/v1/games/"
      f"{place_id}/servers/Public",
      params
    )

    servers = data.get("data", [])

    for server in servers:
      playing = server.get("playing", 0)
      max_players = server.get("maxPlayers", 0)

      server_list.append({
        "server_id": server.get("id"),
        "players": playing,
        "max_players": max_players,
        "occupancy": round(
          playing / max_players * 100, 2
        ) if max_players else 0
      })

    pages += 1
    cursor = data.get("nextPageCursor")

    if not cursor or pages >= MAX_SERVER_PAGES:
      break

  return {
    "public_servers": len(server_list),
    "players_in_listed_servers": sum(
      server["players"] for server in server_list
    ),
    "pages_checked": pages,
    "pagination_complete": cursor is None,
    "server_list": server_list
  }


def fetch_all_stats():
  print("[Roblox] Resolving Universe ID...")

  universe_id = get_universe_id()

  print("[Roblox] Fetching game information...")

  game = get_game_stats(universe_id)

  print("[Roblox] Fetching likes...")

  votes = get_votes(universe_id)

  print("[Roblox] Fetching public servers...")

  servers = get_server_stats(PLACE_ID)

  stats = {
    "game_name": game["name"],
    "place_id": PLACE_ID,
    "universe_id": universe_id,
    "active_players": game["playing"],
    "total_visits": game["visits"],
    "favorites": game["favoritedCount"],
    "max_players_per_server": game["maxPlayers"],
    "likes": votes["upVotes"],
    **servers
  }

  return stats
