from __future__ import annotations
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
from typing import Annotated
import logging
import uvicorn

from app.factorial_utils import factorial


app = FastAPI(
    title="Factorial API",
    version="1.0.0",
    description=(
        "Tiny, well-documented API that computes n! with proper validation and "
        "helpful errors. Accepts a single non-negative integer and returns the "
        "factorial as a string (to avoid client-side integer overflow)."
    ),
    contact={"name": "API Maintainer", "email": "maintainer@example.com"},
    license_info={"name": "MIT"},
)

logger = logging.getLogger("factorial_api")
if not logger.handlers:
    handler = logging.StreamHandler()
    fmt = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

MAX_N = 2000


class FactorialIn(BaseModel):
    number: Annotated[
        int,
        Field(
            ge=0,
            le=MAX_N,
            description=f"Non-negative integer (0 ≤ n ≤ {MAX_N})."
        ),
    ]


class FactorialOut(BaseModel):
    input: Annotated[int, Field(description="Echo of the validated input.")]
    result: Annotated[
        str,
        Field(
            description=(
                "Factorial of the input (stringified to be JSON-safe for very large numbers)."
            )
        ),
    ]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    messages = []
    for err in exc.errors():
        loc = " -> ".join(map(str, err.get("loc", [])))
        msg = err.get("msg", "Invalid input")
        messages.append(f"{loc}: {msg}")
    detail = "; ".join(messages) if messages else "Invalid request body."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "ValidationError", "detail": detail},
    )


@app.post(
    "/factorial",
    response_model=FactorialOut,
    status_code=status.HTTP_200_OK,
    tags=["math"],
    summary="Compute factorial (n!)",
    description=(
        "Compute the factorial of a single non-negative integer `n`.\n\n"
        f"Limits: `0 ≤ n ≤ {MAX_N}` to keep response times predictable.\n"
        "The result is returned as a **string** to avoid precision loss in JSON."
    ),
    responses={
        200: {
            "description": "Successful factorial computation.",
            "content": {
                "application/json": {
                    "examples": {
                        "small": {
                            "summary": "n = 5",
                            "value": {"input": 5, "result": "120"},
                        },
                        "edge_case_zero": {
                            "summary": "n = 0",
                            "value": {"input": 0, "result": "1"},
                        },
                    }
                }
            },
        },
        422: {
            "description": "Validation error: missing/invalid number or out of bounds.",
            "content": {
                "application/json": {
                    "example": {
                        "error": "ValidationError",
                        "detail": "body -> number: Input should be greater than or equal to 0",
                    }
                }
            },
        },
        400: {
            "description": "Bad request for logically invalid inputs (not expected here due to validation).",
            "content": {
                "application/json": {
                    "example": {
                        "error": "BadRequest",
                        "detail": "Invalid input.",
                    }
                }
            },
        },
    },
)
async def compute_factorial(payload: FactorialIn) -> FactorialOut:
    n = payload.number

    if n < 0 or n > MAX_N:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Number must be between 0 and {MAX_N}.",
        )

    logger.info("Computing factorial for n=%d", n)

    value = factorial(n)

    return FactorialOut(input=n, result=str(value))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
