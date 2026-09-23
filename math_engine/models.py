from pydantic import BaseModel
from typing import List

class MathSolution(BaseModel):
    problem: str
    known_conditions: List[str]
    goal: str
    steps: List[str]
    answer: str
    verified: bool
    knowledge_point: str
