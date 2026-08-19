from pydantic import BaseModel
from typing import Literal
 
Source = Literal["reddit", "youtube", "huggingface"]
 
Topic = Literal[
    "general", "politics", "food", "sports", "religion",
    "humor", "family", "news", "questions", "discussions",
    "venting", "jobs_education", "commerce", "tech_gaming",
    "relationships", "health", "other"
]
 
 
class RawEntry(BaseModel):
    source: Source
    topic: Topic
    text: str
 
    def is_valid(self) -> bool:
        return len(self.text.strip()) >= 30