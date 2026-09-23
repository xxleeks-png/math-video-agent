from typing import Callable, Dict
from .problem import ProblemSpec
from .models import MathSolution

Solver = Callable[[ProblemSpec], MathSolution]


class SolverRegistry:
    def __init__(self):
        self._solvers: Dict[str, Solver] = {}

    def register(self, sub_type: str, solver: Solver):
        self._solvers[sub_type] = solver

    def get(self, sub_type: str) -> Solver:
        if sub_type not in self._solvers:
            raise ValueError(f"暂不支持题型：{sub_type}")
        return self._solvers[sub_type]


registry = SolverRegistry()
