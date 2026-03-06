"""
Azure Computer Vision v3.2 API simulator.

Covered endpoints
-----------------
POST   /vision/v3.2/analyze                          – Analyze Image
POST   /vision/v3.2/describe                         – Describe Image
POST   /vision/v3.2/detect                           – Detect Objects
POST   /vision/v3.2/tag                              – Tag Image
POST   /vision/v3.2/ocr                              – OCR (legacy)
POST   /vision/v3.2/read/analyze                     – Read (submit async job)
GET    /vision/v3.2/read/analyzeResults/{operationId} – Read (poll result)
DELETE /vision/v3.2/read/analyzeResults/{operationId} – Read (delete result)
POST   /vision/v3.2/generateThumbnail                – Generate Thumbnail
POST   /vision/v3.2/areaOfInterest                  – Get Area of Interest
"""
from __future__ import annotations

import io
import uuid
from typing import Annotated, Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse

import mock_data

router = APIRouter(prefix="/vision/v3.2", tags=["Computer Vision v3.2"])

# In-memory store for async Read operations  {operation_id: result_dict}
_read_store: dict[str, dict] = {}

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
# POST /vision/v3.2/analyze
# ---------------------------------------------------------------------------

VALID_VISUAL_FEATURES = {
    "Categories", "Tags", "Description", "Faces", "ImageType",
    "Color", "Adult", "Objects", "Brands",
}

VALID_DETAILS = {"Celebrities", "Landmarks"}

VALID_LANGUAGES = {"en", "es", "ja", "pt", "zh"}


@router.post("/analyze", summary="Analyze Image")
async def analyze_image(
    request: Request,
    visualFeatures: Annotated[
        Optional[str], Query(description="Comma-separated visual features")
    ] = None,
    details: Annotated[
        Optional[str], Query(description="Comma-separated domain-specific details")
    ] = None,
    language: Annotated[str, Query()] = "en",
    model_version: Annotated[str, Query(alias="model-version")] = "latest",
    Ocp_Apim_Subscription_Key: Annotated[Optional[str], Header(alias="Ocp-Apim-Subscription-Key")] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)

    features: list[str] | None = None
    if visualFeatures:
        features = [f.strip() for f in visualFeatures.split(",")]
        invalid = set(features) - VALID_VISUAL_FEATURES
        if invalid:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "BadArgument",
                    "message": f"Invalid visual feature(s): {', '.join(invalid)}",
                },
            )

    if language not in VALID_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail={"code": "BadArgument", "message": f"Language '{language}' is not supported."},
        )

    return mock_data.build_analyze_response(features)


# ---------------------------------------------------------------------------
# POST /vision/v3.2/describe
# ---------------------------------------------------------------------------

@router.post("/describe", summary="Describe Image")
async def describe_image(
    request: Request,
    maxCandidates: Annotated[int, Query(ge=1, le=10)] = 1,
    language: Annotated[str, Query()] = "en",
    model_version: Annotated[str, Query(alias="model-version")] = "latest",
    Ocp_Apim_Subscription_Key: Annotated[Optional[str], Header(alias="Ocp-Apim-Subscription-Key")] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)
    return mock_data.build_describe_response(maxCandidates)


# ---------------------------------------------------------------------------
# POST /vision/v3.2/detect
# ---------------------------------------------------------------------------

@router.post("/detect", summary="Detect Objects")
async def detect_objects(
    request: Request,
    model_version: Annotated[str, Query(alias="model-version")] = "latest",
    Ocp_Apim_Subscription_Key: Annotated[Optional[str], Header(alias="Ocp-Apim-Subscription-Key")] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)
    return mock_data.build_detect_response()


# ---------------------------------------------------------------------------
# POST /vision/v3.2/tag
# ---------------------------------------------------------------------------

@router.post("/tag", summary="Tag Image")
async def tag_image(
    request: Request,
    language: Annotated[str, Query()] = "en",
    model_version: Annotated[str, Query(alias="model-version")] = "latest",
    Ocp_Apim_Subscription_Key: Annotated[Optional[str], Header(alias="Ocp-Apim-Subscription-Key")] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)
    return mock_data.build_tag_response()


# ---------------------------------------------------------------------------
# POST /vision/v3.2/ocr
# ---------------------------------------------------------------------------

VALID_OCR_LANGUAGES = {
    "unk", "zh-Hans", "zh-Hant", "cs", "da", "nl", "en", "fi", "fr",
    "de", "el", "hu", "it", "ja", "ko", "nb", "pl", "pt", "ru", "es",
    "sv", "tr", "ar", "ro", "sr-Cyrl", "sr-Latn", "sk",
}


@router.post("/ocr", summary="Recognize Text (OCR)")
async def ocr(
    request: Request,
    language: Annotated[str, Query()] = "unk",
    detectOrientation: Annotated[bool, Query()] = True,
    model_version: Annotated[str, Query(alias="model-version")] = "latest",
    Ocp_Apim_Subscription_Key: Annotated[Optional[str], Header(alias="Ocp-Apim-Subscription-Key")] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)
    return mock_data.build_ocr_response()


# ---------------------------------------------------------------------------
# POST /vision/v3.2/read/analyze  – submit async job
# ---------------------------------------------------------------------------

VALID_READ_LANGUAGES = {
    "af", "ast", "bi", "br", "bs", "ca", "ceb", "ch", "co", "crh", "cs",
    "cy", "da", "de", "en", "es", "et", "eu", "fi", "fil", "fj", "fr",
    "ga", "gl", "gu", "hr", "ht", "hu", "id", "ik", "is", "it", "ja",
    "ka", "kaa", "kac", "kha", "km", "ko", "ku", "la", "lkt", "lt", "lv",
    "mi", "mk", "mn", "ms", "mt", "mww", "my", "nb", "ne", "oc", "or",
    "pa", "pl", "ps", "pt", "quc", "ro", "ru", "sk", "sl", "sq", "sr",
    "sv", "sw", "tet", "tg", "th", "tr", "tt", "ug", "uk", "ur", "uz",
    "vi", "wls", "yi", "yua", "yue", "zh-Hans", "zh-Hant",
}


@router.post("/read/analyze", summary="Read – Submit Async Job", status_code=202)
async def read_analyze(
    request: Request,
    language: Annotated[Optional[str], Query()] = None,
    pages: Annotated[Optional[str], Query()] = None,
    readingOrder: Annotated[str, Query()] = "basic",
    model_version: Annotated[str, Query(alias="model-version")] = "latest",
    Ocp_Apim_Subscription_Key: Annotated[Optional[str], Header(alias="Ocp-Apim-Subscription-Key")] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)

    operation_id = str(uuid.uuid4())
    # Pre-build and store the result so the GET poll always returns "succeeded"
    _read_store[operation_id] = mock_data.build_read_result(operation_id, "succeeded")

    operation_location = (
        f"{request.base_url}vision/v3.2/read/analyzeResults/{operation_id}"
    )
    return Response(
        status_code=202,
        headers={"Operation-Location": operation_location},
    )


# ---------------------------------------------------------------------------
# GET /vision/v3.2/read/analyzeResults/{operationId}
# ---------------------------------------------------------------------------

@router.get(
    "/read/analyzeResults/{operation_id}",
    summary="Read – Get Result",
)
async def read_get_result(
    operation_id: str,
    Ocp_Apim_Subscription_Key: Annotated[Optional[str], Header(alias="Ocp-Apim-Subscription-Key")] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)

    if operation_id not in _read_store:
        raise HTTPException(
            status_code=404,
            detail=mock_data.error_not_found(operation_id)["error"],
        )
    return _read_store[operation_id]


# ---------------------------------------------------------------------------
# DELETE /vision/v3.2/read/analyzeResults/{operationId}
# ---------------------------------------------------------------------------

@router.delete(
    "/read/analyzeResults/{operation_id}",
    summary="Read – Delete Result",
    status_code=200,
)
async def read_delete_result(
    operation_id: str,
    Ocp_Apim_Subscription_Key: Annotated[Optional[str], Header(alias="Ocp-Apim-Subscription-Key")] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)

    if operation_id not in _read_store:
        raise HTTPException(
            status_code=404,
            detail=mock_data.error_not_found(operation_id)["error"],
        )
    del _read_store[operation_id]
    return {}


# ---------------------------------------------------------------------------
# POST /vision/v3.2/generateThumbnail
# ---------------------------------------------------------------------------

@router.post("/generateThumbnail", summary="Generate Thumbnail")
async def generate_thumbnail(
    request: Request,
    width: Annotated[int, Query(ge=1, le=1024)] = 100,
    height: Annotated[int, Query(ge=1, le=1024)] = 100,
    smartCropping: Annotated[bool, Query()] = False,
    model_version: Annotated[str, Query(alias="model-version")] = "latest",
    Ocp_Apim_Subscription_Key: Annotated[Optional[str], Header(alias="Ocp-Apim-Subscription-Key")] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)

    # Return a minimal valid PNG (1x1 grey pixel) resized conceptually to requested dims.
    # A real thumbnail would require decoding the source image; here we return a blank PNG.
    try:
        from PIL import Image

        img = Image.new("RGB", (width, height), color=(128, 128, 128))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return Response(content=buf.read(), media_type="image/png")
    except ImportError:
        # Pillow not installed – return a 1×1 white PNG (hard-coded bytes)
        png_1x1 = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc"
            b"\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        return Response(content=png_1x1, media_type="image/png")


# ---------------------------------------------------------------------------
# POST /vision/v3.2/areaOfInterest
# ---------------------------------------------------------------------------

@router.post("/areaOfInterest", summary="Get Area of Interest")
async def area_of_interest(
    request: Request,
    model_version: Annotated[str, Query(alias="model-version")] = "latest",
    Ocp_Apim_Subscription_Key: Annotated[Optional[str], Header(alias="Ocp-Apim-Subscription-Key")] = None,
):
    _check_auth(Ocp_Apim_Subscription_Key)
    return mock_data.build_area_of_interest_response()
