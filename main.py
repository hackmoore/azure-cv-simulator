"""
Azure Computer Vision API Simulator
====================================
A FastAPI application that simulates the Azure Computer Vision REST API.
Useful for local development and testing without a live Azure subscription.

Supported API surface
---------------------
v3.2
  POST   /vision/v3.2/analyze
  POST   /vision/v3.2/describe
  POST   /vision/v3.2/detect
  POST   /vision/v3.2/tag
  POST   /vision/v3.2/ocr
  POST   /vision/v3.2/read/analyze
  GET    /vision/v3.2/read/analyzeResults/{operationId}
  DELETE /vision/v3.2/read/analyzeResults/{operationId}
  POST   /vision/v3.2/generateThumbnail
  POST   /vision/v3.2/areaOfInterest

v4.0
  POST   /computervision/imageanalysis:analyze
  POST   /computervision/imageanalysis:segment
  POST   /computervision/retrieval:vectorizeImage
  POST   /computervision/retrieval:vectorizeText

Usage
-----
  pip install -r requirements.txt
  uvicorn main:app --reload --port 5000

Then set your SDK / client to point at http://localhost:5000
and use any non-empty string as the subscription key.

Interactive docs: http://localhost:5000/docs
"""
from __future__ import annotations

import sys
import os

# Allow imports from the project root when running from any directory
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routers import v32, v40

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Azure Computer Vision API Simulator",
    description=(
        "A local simulator of the Azure Computer Vision REST API (v3.2 and v4.0). "
        "Returns realistic mock data for every covered endpoint. "
        "Authentication is enforced via the `Ocp-Apim-Subscription-Key` header "
        "(any non-empty value is accepted)."
    ),
    version="1.0.0",
    contact={
        "name": "Azure Computer Vision Docs",
        "url": "https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/",
    },
    openapi_tags=[
        {
            "name": "Computer Vision v3.2",
            "description": "Azure Computer Vision REST API v3.2 endpoints.",
        },
        {
            "name": "Computer Vision v4.0",
            "description": "Azure Computer Vision Florence / v4.0 endpoints.",
        },
        {
            "name": "Health",
            "description": "Simulator health and info.",
        },
    ],
)

# Allow all origins so browser-based tools (Swagger, Postman web) can reach the simulator
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(v32.router)
app.include_router(v40.router)

# ---------------------------------------------------------------------------
# Global exception handler – mirror Azure error envelope
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "InternalServerError",
                "message": str(exc),
            }
        },
    )


# ---------------------------------------------------------------------------
# Health / info endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"], summary="Root")
async def root():
    return {
        "service": "Azure Computer Vision API Simulator",
        "status": "running",
        "docs": "/docs",
        "supported_versions": ["v3.2", "v4.0"],
    }


@app.get("/health", tags=["Health"], summary="Health check")
async def health():
    return {"status": "healthy"}


@app.get("/endpoints", tags=["Health"], summary="List all simulated endpoints")
async def list_endpoints():
    """Returns a structured list of every simulated endpoint."""
    return {
        "v3.2": {
            "base": "/vision/v3.2",
            "endpoints": [
                {"method": "POST", "path": "/analyze",                          "description": "Analyze Image"},
                {"method": "POST", "path": "/describe",                         "description": "Describe Image"},
                {"method": "POST", "path": "/detect",                           "description": "Detect Objects"},
                {"method": "POST", "path": "/tag",                              "description": "Tag Image"},
                {"method": "POST", "path": "/ocr",                              "description": "OCR (legacy)"},
                {"method": "POST", "path": "/read/analyze",                     "description": "Read – Submit Async Job"},
                {"method": "GET",  "path": "/read/analyzeResults/{operationId}","description": "Read – Poll Result"},
                {"method": "DELETE","path": "/read/analyzeResults/{operationId}","description": "Read – Delete Result"},
                {"method": "POST", "path": "/generateThumbnail",                "description": "Generate Thumbnail (returns PNG)"},
                {"method": "POST", "path": "/areaOfInterest",                   "description": "Get Area of Interest"},
            ],
        },
        "v4.0": {
            "base": "/computervision",
            "endpoints": [
                {"method": "POST", "path": "/imageanalysis:analyze",            "description": "Image Analysis v4.0"},
                {"method": "POST", "path": "/imageanalysis:segment",            "description": "Image Segmentation (returns PNG)"},
                {"method": "POST", "path": "/retrieval:vectorizeImage",         "description": "Vectorize Image (1024-dim embedding)"},
                {"method": "POST", "path": "/retrieval:vectorizeText",          "description": "Vectorize Text (1024-dim embedding)"},
            ],
        },
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
