import json
from pathlib import Path
from threading import Lock

from scrapler.types import RawEntry

class Writer:
  """
  JSONL thread-safe writer with deduplication, appends entries to
  `raw.jsonl` and skips duplicates 
  """
  def __init__(self, path: Path) -> None:
    self.path = path
    self.path.parent.mkdir(parents=True, exist_ok=True)
    self._lock = Lock()
    self._seen: set[str] = set()

    if self.path.exists():
      with open(file=self.path, encoding="utf-8") as file:
        for line in file:
          line = line.strip()
          if line:
            try:
              obj = json.loads(line)
              self._seen.add(obj.get("text", "").strip())
            except json.JSONDecodeError:
              continue

  def write(self, entry: RawEntry) -> bool:
    text = entry.text.strip()
    if not entry.is_valid():
      return False

    with self._lock:
      if text in self._seen:
        return False

      self._seen.add(text)
      with open(file=self.path, mode="a", encoding="utf-8") as file:
        file.write(json.dumps(entry.model_dump(), ensure_ascii=False) + "\n")

      return True


  @property
  def count(self) -> int:
    return len(self._seen)