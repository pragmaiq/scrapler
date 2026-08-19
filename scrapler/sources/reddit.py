import asyncio
import httpx

from rich.console import Console

from scrapler.types import Topic, RawEntry
from scrapler import filters
from scrapler import writer

# initialize `Console` interface
console = Console()

# a list of subreddits to scrape
SUBS = [
  "iraq",
  "iraqi", 
  "baghdad", 
  "iraq_developers", 
  "iqtech", 
  "iraqigamers", 
  "sixthgrade", 
  "iraqistudents", 
  "iraqletterboxed"
]

# a list of listings (new, hot, and top)
LISTINGS = ["new", "hot", "top"]

# HTTP headers
HEADERS = {
  "User-Agent": "scrapler/1.0 (Salfa Iraqi Model - NLP Research)"
}

async def _resolve_topic(text: str, title: str = "") -> Topic:
  """
  uses `filters.textray` to detect topics, maps to the Topic literal
  """
  topics = filters.textray(text, title)
  primary = topics[0] if topics else "general"
  valid: set[Topic] = {
    "general", "politics", "food", "sports", "religion",
    "humor", "family", "news", "questions", "discussions",
    "venting", "jobs_education", "commerce", "tech_gaming",
    "relationships", "health", "other"
  }

  return primary if primary in valid else "general"

async def _fetch_listing(
    client: httpx.AsyncClient,
    subreddit: str,
    listing: str,
    limit: int = 100,
) -> list[dict]:
  url = "https://www.reddit.com/r/{subreddit}/{listing}.json"
  try:
    response = await client.get(url=url, params={"limit": limit, "raw_json": 1}, headers=HEADERS)
    response.raise_for_status()
    return response.json()["data"]["children"]
  except Exception:
    return []

async def _fetch_comments(
    client: httpx.AsyncClient,
    subreddit: str,
    post_id: str,
) -> list[dict]:
  url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
  try:
    response = await client.get(url=url, params={"raw_json": 1, "limit": 200}, headers=HEADERS)
    response.raise_for_status()

    data = response.json()
    if len(data) < 2:
      return []

    return [
      c["data"]["body"].strip()
      for c in data[1]["data"]["children"]
      if c["kind"] == "t1"
      and c["data"].get("body", "") not in ("", "[deleted]", "[removed]")
    ]

  except Exception:
    return []

async def reddit(
    writer: writer.Writer,
    max_per_subreddit: int = 500
) -> 500:
  written = 0

  async with httpx.AsyncClient(timeout=30.0) as client:
    for sub in SUBS:
      console.print("[blue] r/{sub} [/cyan]")
      sub_count = 0

      for listing in LISTINGS:
        if sub_count >= max_per_subreddit:
          break

        posts = await _fetch_listing(client=client, subreddit=sub, listing=listing)
        for post in posts:
          if sub_count >= max_per_subreddit:
            break

          data = post["data"]
          selftext = data.get("selftext", "").strip()
          title = data.get("title", "").strip()
          post_id = data.get("id", "")

          if selftext and filters.filter(selftext):
            topic = _resolve_topic(text=selftext, title=title)
            if writer.write(RawEntry(source="reddit", topic=topic, text=selftext)):
              written += 1
              sub_count +=1

          if post_id:
            await asyncio.sleep(1.0)
            for comment in await _fetch_comments(client=client, subreddit=sub, post_id=post_id):
              if sub_count >= max_per_subreddit:
                break

              if filters.filter(comment):
                topic = _resolve_topic(comment)
                if writer.write(RawEntry(source="reddit", topic=topic, text=comment)):
                  written += 1
                  sub_count += 1

          await asyncio.sleep(.5)

      console.print(f"      [green]DONE[/green] {sub_count} entries ")
    return written