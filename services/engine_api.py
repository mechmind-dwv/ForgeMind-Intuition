"""Local HTTP adapter for the ForgeMind Python engine.

Run from the repository root with:
    uvicorn services.engine_api:app --host 127.0.0.1 --port 8787
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from forgemind.advisor import advise
from forgemind.project import ForgeMindProject, ProjectValidationError


class EvaluateRequest(BaseModel):
    project: dict[str, Any]


class EvaluateResponse(BaseModel):
    project: str
    candidate_count: int
    results: list[dict[str, Any]]
    engine: str = "forgemind-python"


app = FastAPI(title="ForgeMind Engine API", version="0.16")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "engine": "forgemind-python", "version": "0.16"}


@app.post("/v1/evaluate", response_model=EvaluateResponse)
def evaluate(request: EvaluateRequest) -> EvaluateResponse:
    try:
        project = ForgeMindProject.from_dict(request.project)
        knowledge = project.knowledge_base()
        results = [item.as_dict() for item in advise(project.candidates, knowledge_base=knowledge)]
    except (ProjectValidationError, ValueError, KeyError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    return EvaluateResponse(project=project.name, candidate_count=len(project.candidates), results=results)
