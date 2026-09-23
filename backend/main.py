from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from math_engine.parser import parse
from math_engine.solver import solve
from math_engine.validator import validate

app = FastAPI(title="Math Video Agent", version="0.7.0")

class SolveRequest(BaseModel):
    problem: str

class GenerateRequest(SolveRequest):
    output_dir: str = "output"

@app.get("/health")
def health():
    return {"status": "ok", "version": "0.7.0", "local_only": True}

@app.post("/api/v1/parse")
def parse_problem(request: SolveRequest):
    try:
        return parse(request.problem)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/v1/solve")
def solve_problem(request: SolveRequest):
    try:
        return solve(request.problem)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/v1/validate")
def validate_problem(request: SolveRequest):
    try:
        spec = parse(request.problem)
        solution = solve(request.problem)
        return {"verified": validate(spec, solution), "answer": solution.answer}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

@app.post("/api/v1/generate")
def generate_video(request: GenerateRequest):
    try:
        from scripts.generate_video import generate_video
        return generate_video(request.problem, request.output_dir)
    except (ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
