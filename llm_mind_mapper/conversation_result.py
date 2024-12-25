from typing import List, Tuple, Dict
from pydantic import BaseModel, Field

class ConversationResult(BaseModel):
    """Model for storing conversation analysis results."""
    concepts: Dict[str, str] = Field(
        description="A dictionary mapping concept names to their descriptions"
    )
    relationships: List[Tuple[str, str]] = Field(
        description="A list of tuples representing relationships between concepts"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "concepts": {
                    "Mobile App Development": "The main project involving development of a mobile application",
                    "User Authentication": "Security feature for user login and verification"
                },
                "relationships": [
                    ["Mobile App Development", "User Authentication"]
                ]
            }
        }