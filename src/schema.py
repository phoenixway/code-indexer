from typing import List, Optional, Literal
from pydantic import BaseModel, Field

# --- Entity Schema ---

class EntitySummary(BaseModel):
    text: str
    source: Literal["human", "llm"]

class CodeEntity(BaseModel):
    id: str                # path:symbol
    type: Literal["function", "class", "file"]
    path: str
    symbol: str
    
    # Optional fields (nullable in JSON)
    summary: Optional[EntitySummary] = None
    responsibility: Optional[str] = None
    side_effects: Optional[List[str]] = Field(default_factory=list)
    calls: Optional[List[str]] = Field(default_factory=list)
    called_by: Optional[List[str]] = Field(default_factory=list)
    
    # Confidence is mandatory
    confidence: Literal["low", "medium", "high"]

    def update_confidence(self):
        """Logic: Human -> High, LLM -> Medium, None -> Low"""
        if self.summary and self.summary.source == "human":
            self.confidence = "high"
        elif self.summary and self.summary.source == "llm":
            self.confidence = "medium"
        else:
            self.confidence = "low"

# --- Intent Schema ---

class Intent(BaseModel):
    id: str                # intent.name
    description: str
    responsibilities: Optional[List[str]] = []
    non_responsibilities: Optional[List[str]] = []
    mapped_entities: List[str] # List of entity IDs
