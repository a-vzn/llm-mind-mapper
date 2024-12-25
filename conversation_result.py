from typing import List, Tuple, Dict
from pydantic import BaseModel

class ConversationResult(BaseModel):
    concepts: Dict[str, str]
    relationships: List[Tuple[str, str]]