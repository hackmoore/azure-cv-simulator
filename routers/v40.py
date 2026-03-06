"""
Azure Computer Vision v4.0 (Florence) API simulator.

Covered endpoints
-----------------
POST /computervision/imageanalysis:analyze   – Image Analysis v4.0
POST /computervision/imageanalysis:segment   – Image Segmentation (background removal / foreground matting)
POST /computervision/retrieval:vectorizeImage – Vectorize Image (multimodal embeddings)
POST /computervision/retrieval:vectorizeText  – Vectorize Text  (multimodal embeddings)
"""
from __future__ import annotations

import io
import random
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request, Response

import mock_data

router = APIRouter(prefix="/computervision", tags=["Computer Vision v4.0"])

# ---------------------------------------------------------------------------
# Auth helper
# ---------------------------------------------------------------------------

def _check_auth(api_key: str | None) -> None:
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail=mock_data.error_missing_key()["error"],
        )


# ---------------------------------------------------------------------------
# POST /computervision/imageanalysis:analyze
# ---------------------------------------------------------------------------

VALID_V4_FEATURES = {
    "tags", "caption", "denseCaptions", "objects",
    "read", "smartCrops", "people",
}

VALID_V4_LANGUAGES = {
    "en", "es", "ja", "pt", "zh", "fr", "de", "it", "ko", "nl", "pl",
    "ru", "sv", "ar", "tr",
}


@router.post("/imageanalysis:analyze", summary="Image Analysis v4.0")
async def analyze_image_v4(
    request: Request,
    features: Annotated[
        Optional[str],
        Query(description="Comma-separated feature list"),
    ] = None,
    language: Annotated[str, Query()] = "en",
    smartcrops_aspect_ratios: Annotated[
        Optional[str],
        Query(alias="smartcrops-aspect-ratios"),
    ] = None,
    gender_neutral_caption: Annotated[
        Optional[str],
        Query(alias="gender-neutral-caption"),
    ] = None,
    model_version: Annotated[str, Query(alias="model-version")] = "latest",
    api_version: Annotated[str, Query(alias="api-version")] = "2024-02-01",
    Ocp_Apim_Subscription_Key: Annotated[
        Optional[str], Header(alias="Ocp-Apim-Subscription-Key")
    ] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)

    feature_list: list[str] | None = None
    if features:
        feature_list = [f.strip() for f in features.split(",")]
        invalid = set(feature_list) - VALID_V4_FEATURES
        if invalid:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "InvalidRequest",
                    "message": f"Invalid feature(s): {', '.join(invalid)}. "
                               f"Valid values are: {', '.join(sorted(VALID_V4_FEATURES))}",
                },
            )

    if language not in VALID_V4_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "InvalidRequest",
                "message": f"Language '{language}' is not supported.",
            },
        )

    return mock_data.build_v4_response(feature_list)


# ---------------------------------------------------------------------------
# POST /computervision/imageanalysis:segment
# ---------------------------------------------------------------------------

VALID_SEGMENT_MODES = {"backgroundRemoval", "foregroundMatting"}


@router.post("/imageanalysis:segment", summary="Image Segmentation v4.0")
async def segment_image(
    request: Request,
    mode: Annotated[
        str,
        Query(description="'backgroundRemoval' or 'foregroundMatting'"),
    ] = "backgroundRemoval",
    api_version: Annotated[str, Query(alias="api-version")] = "2024-02-01",
    Ocp_Apim_Subscription_Key: Annotated[
        Optional[str], Header(alias="Ocp-Apim-Subscription-Key")
    ] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)

    if mode not in VALID_SEGMENT_MODES:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "InvalidRequest",
                "message": f"Invalid mode '{mode}'. Must be one of: {', '.join(VALID_SEGMENT_MODES)}",
            },
        )

    # Return a small greyscale PNG as a stand-in for the alpha matte / segmented image.
    try:
        from PIL import Image

        width, height = 640, 480
        img = Image.new("RGBA" if mode == "foregroundMatting" else "RGB", (width, height), (180, 180, 180, 200))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return Response(content=buf.read(), media_type="image/png")
    except ImportError:
        png_1x1 = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc"
            b"\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return Response(content=png_1x1, media_type="image/png")


# ---------------------------------------------------------------------------
# POST /computervision/retrieval:vectorizeImage
# ---------------------------------------------------------------------------

def _random_embedding(dims: int = 1024) -> list[float]:
    """Generate a normalised random unit vector to simulate a real embedding."""
    vec = [random.gauss(0, 1) for _ in range(dims)]
    magnitude = sum(v ** 2 for v in vec) ** 0.5
    return [round(v / magnitude, 8) for v in vec]


@router.post("/retrieval:vectorizeImage", summary="Vectorize Image v4.0")
async def vectorize_image(
    request: Request,
    api_version: Annotated[str, Query(alias="api-version")] = "2024-02-01",
    model_version: Annotated[str, Query(alias="model-version")] = "latest",
    Ocp_Apim_Subscription_Key: Annotated[
        Optional[str], Header(alias="Ocp-Apim-Subscription-Key")
    ] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)

    return {
        "modelVersion": "2023-04-15",
        "vector": _random_embedding(1024),
    }


# ---------------------------------------------------------------------------
# POST /computervision/retrieval:vectorizeText
# ---------------------------------------------------------------------------

@router.post("/retrieval:vectorizeText", summary="Vectorize Text v4.0")
async def vectorize_text(
    request: Request,
    api_version: Annotated[str, Query(alias="api-version")] = "2024-02-01",
    model_version: Annotated[str, Query(alias="model-version")] = "latest",
    Ocp_Apim_Subscription_Key: Annotated[
        Optional[str], Header(alias="Ocp-Apim-Subscription-Key")
    ] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)

    body = await request.json()
    text = body.get("text", "")
    if not text:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "InvalidRequest",
                "message": "The 'text' field is required.",
            },
        )
    if len(text) > 70:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "InvalidRequest",
                "message": "Text is too long. Maximum length is 70 tokens.",
            },
        )

    return {
        "modelVersion": "2023-04-15",
        "vector": _random_embedding(1024),
    }
