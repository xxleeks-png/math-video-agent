from pydantic import BaseModel, Field
from typing import Dict


class ProblemSpec(BaseModel):
    grade: str = "小学"
    problem_type: str
    sub_type: str
    known: Dict[str, float] = Field(default_factory=dict)
    question: Dict[str, str] = Field(default_factory=dict)
    raw_text: str
    confidence: float = 1.0
