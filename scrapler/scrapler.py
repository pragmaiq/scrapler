"""

Pragma IQ Data Scraper Tool

Our internal tool used to scrape/harvest data from various platforms.
Used within a CLI command `spy [COMMAND] [OPTIONS]`

- Commands:
  - spy reddit [OPTIONS]        # scrape Iraqi subreddits (posts and comments)
  - spy youtube|yt [OPTIONS]    # scrape Iraqi YouTube comments
  - spy hf [OPTIONS]            # pulls from HuggingFace datasets
  - spy deep [OPTIONS]          # runs all the sources at once
  - spy db [OPTIONS]            # exports data to the database
  - spy stats                   # shows current data stats
"""

import json
import typer
import asyncio

from pathlib import Path
from collections import Counter

from rich.table import Table
from dotenv import load_dotenv
from rich.console import Console

from scrapler.writer import Writer

load_dotenv()

# path to the default output
DEFAULT_OUTPUT = Path("data/raw.jsonl")

app = typer.Typer(
  name="spy",
  help="Pragma IQ data scraper — Iraqi Arabic dialect harvester",
  no_args_is_help=True,
)

console = Console()

def _print_summary(source: str, written: int, total: int) -> None:
  console.print(f"\n[bold green]✅ {source} complete[/bold green]")
  console.print(f"   New entries : {written}")
  console.print(f"   Total in file: {total}")

def _make_writer(output: Path) -> Writer:
  """
  inits a writer
  """
  writer = Writer(output)
  console.print(f"[dim]output: {output}[/dim]")
  console.print(f"[dim]existing: {writer.count} entries[/dim]\n")
  return writer

@app.command()
def reddit(
  output: Path = typer.Option(DEFAULT_OUTPUT, "--output", "-o"),
  max_per_sub: int = typer.Option(500, "--max", "-m", help="max entries per subreddit")
) -> None:
  """
  scrapes different subreddit's
  """
  from scrapler.sources.reddit import reddit

  console.print("[bold] ======= Reddit Scraper =======[/bold]")
  writer = _make_writer(output=output)
  written = asyncio.run(reddit(writer=writer, max_per_subreddit=max_per_sub))
  _print_summary("Reddit", written, writer.count)