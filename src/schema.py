from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# --- Entity Schema ---

class EntitySummary(BaseModel):
    text: str
    source: Literal["human", "llm", "web_ai"]


class SourceRange(BaseModel):
    start_line: int
    start_column: int
    end_line: int
    end_column: int
    start_byte: int
    end_byte: int


class CodeEntity(BaseModel):
    id: str
    type: Literal[
        "function",
        "method",
        "class",
        "interface",
        "enum",
        "type_alias",
        "file",
    ]
    path: str
    symbol: str

    # Structural facts extracted from source code.
    language: Optional[str] = None
    ast_kind: Optional[str] = None
    qualified_name: Optional[str] = None
    parent_id: Optional[str] = None
    parent_symbol: Optional[str] = None
    source_range: Optional[SourceRange] = None

    # Semantic enrichment.
    summary: Optional[EntitySummary] = None
    responsibility: Optional[str] = None
    side_effects: List[str] = Field(default_factory=list)

    # Graph fields. These are populated by later analysis stages.
    calls: List[str] = Field(default_factory=list)
    called_by: List[str] = Field(default_factory=list)

    # Human -> high, AI -> medium, raw structural entity -> low.
    confidence: Literal["low", "medium", "high"] = "low"

    def update_confidence(self) -> None:
        if self.summary and self.summary.source == "human":
            self.confidence = "high"
        elif self.summary and self.summary.source in {"llm", "web_ai"}:
            self.confidence = "medium"
        else:
            self.confidence = "low"


# --- Intent Schema ---

class Intent(BaseModel):
    id: str
    description: str
    responsibilities: List[str] = Field(default_factory=list)
    non_responsibilities: List[str] = Field(default_factory=list)
    mapped_entities: List[str] = Field(default_factory=list)
    source: Literal["human", "llm", "web_ai"] = "human"
