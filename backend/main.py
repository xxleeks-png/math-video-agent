from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from math_engine.solver import solve

app = FastAPI(title="Math Video Agent", version="0.1.0")

class SolveRequest(BaseModel):
    problem: str

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}

@app.post("/api/v1/solve")
def solve_problem(request: SolveRequest):
    try:
        return solve(request.problem)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
