from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Shared primitives
# ---------------------------------------------------------------------------

class BoundingRect(BaseModel):
    x: int
    y: int
    w: int
    h: int


class BoundingBox(BaseModel):
    left: int
    top: int
    width: int
    height: int


class Polygon(BaseModel):
    # List of {"x": int, "y": int}
    points: list[dict[str, int]]


class ImageMetadata(BaseModel):
    width: int
    height: int
    format: str


# ---------------------------------------------------------------------------
# Analyze Image (v3.2) response
# ---------------------------------------------------------------------------

class Category(BaseModel):
    name: str
    score: float
    detail: Optional[dict[str, Any]] = None


class Tag(BaseModel):
    name: str
    confidence: float
    hint: Optional[str] = None


class Caption(BaseModel):
    text: str
    confidence: float


class ImageDescription(BaseModel):
    tags: list[str]
    captions: list[Caption]


class Color(BaseModel):
    dominantColorForeground: str
    dominantColorBackground: str
    dominantColors: list[str]
    accentColor: str
    isBWImg: bool
    isBwImg: bool  # duplicate field azure returns both casings


class FaceRectangle(BaseModel):
    left: int
    top: int
    width: int
    height: int


class DetectedFace(BaseModel):
    age: int
    gender: str
    faceRectangle: FaceRectangle


class ImageType(BaseModel):
    clipArtType: int
    lineDrawingType: int


class Adult(BaseModel):
    isAdultContent: bool
    isRacyContent: bool
    isGoryContent: bool
    adultScore: float
    racyScore: float
    goreScore: float


class Brand(BaseModel):
    name: str
    confidence: float
    rectangle: BoundingRect


class DetectedObject(BaseModel):
    rectangle: BoundingRect
    object: str = Field(alias="object")
    confidence: float
    parent: Optional["DetectedObject"] = None

    model_config = {"populate_by_name": True}


class AnalyzeImageResponse(BaseModel):
    categories: list[Category]
    adult: Adult
    color: Color
    imageType: ImageType
    tags: list[Tag]
    description: ImageDescription
    faces: list[DetectedFace]
    objects: list[DetectedObject]
    brands: list[Brand]
    requestId: str
    metadata: ImageMetadata
    modelVersion: str


# ---------------------------------------------------------------------------
# Describe Image (v3.2) response
# ---------------------------------------------------------------------------

class DescribeImageResponse(BaseModel):
    description: ImageDescription
    requestId: str
    metadata: ImageMetadata
    modelVersion: str


# ---------------------------------------------------------------------------
# Detect Objects (v3.2) response
# ---------------------------------------------------------------------------

class DetectObjectsResponse(BaseModel):
    objects: list[DetectedObject]
    requestId: str
    metadata: ImageMetadata
    modelVersion: str


# ---------------------------------------------------------------------------
# Tag Image (v3.2) response
# ---------------------------------------------------------------------------

class TagImageResponse(BaseModel):
    tags: list[Tag]
    requestId: str
    metadata: ImageMetadata
    modelVersion: str


# ---------------------------------------------------------------------------
# OCR (v3.2) response
# ---------------------------------------------------------------------------

class OcrWord(BaseModel):
    boundingBox: str  # "x,y,w,h" comma-separated string as Azure returns
    text: str
    confidence: float


class OcrLine(BaseModel):
    boundingBox: str
    words: list[OcrWord]


class OcrRegion(BaseModel):
    boundingBox: str
    lines: list[OcrLine]


class OcrResponse(BaseModel):
    language: str
    textAngle: float
    orientation: str
    regions: list[OcrRegion]
    modelVersion: str


# ---------------------------------------------------------------------------
# Read (async) – v3.2
# ---------------------------------------------------------------------------

class ReadOperationResponse(BaseModel):
    # Only the Operation-Location header matters; body is empty on 202
    pass


class ReadWord(BaseModel):
    boundingBox: list[int]  # [x1,y1,x2,y2,x3,y3,x4,y4]
    text: str
    confidence: float


class ReadLine(BaseModel):
    boundingBox: list[int]
    text: str
    words: list[ReadWord]
    appearance: dict[str, Any]


class ReadPage(BaseModel):
    page: int
    angle: float
    width: float
    height: float
    unit: str
    lines: list[ReadLine]


class ReadAnalyzeResult(BaseModel):
    version: str
    modelVersion: str
    readResults: list[ReadPage]


class ReadResultResponse(BaseModel):
    status: str  # "notStarted" | "running" | "succeeded" | "failed"
    createdDateTime: str
    lastUpdatedDateTime: str
    analyzeResult: Optional[ReadAnalyzeResult] = None


# ---------------------------------------------------------------------------
# Area of Interest (v3.2) response
# ---------------------------------------------------------------------------

class AreaOfInterestResponse(BaseModel):
    areaOfInterest: BoundingRect
    requestId: str
    metadata: ImageMetadata
    modelVersion: str


# ---------------------------------------------------------------------------
# Image Analysis v4.0 response
# ---------------------------------------------------------------------------

class V4Caption(BaseModel):
    text: str
    confidence: float


class V4CaptionResult(BaseModel):
    captionResult: V4Caption


class V4DenseCaption(BaseModel):
    text: str
    confidence: float
    boundingBox: BoundingBox


class V4DenseCaptionsResult(BaseModel):
    values: list[V4DenseCaption]


class V4Tag(BaseModel):
    name: str
    confidence: float


class V4TagsResult(BaseModel):
    values: list[V4Tag]


class V4DetectedObject(BaseModel):
    id: str
    boundingBox: BoundingBox
    tags: list[V4Tag]


class V4ObjectsResult(BaseModel):
    values: list[V4DetectedObject]


class V4ReadLine(BaseModel):
    text: str
    boundingPolygon: list[dict[str, int]]
    words: list[dict[str, Any]]


class V4ReadBlock(BaseModel):
    lines: list[V4ReadLine]


class V4ReadResult(BaseModel):
    blocks: list[V4ReadBlock]


class V4Person(BaseModel):
    id: str
    boundingBox: BoundingBox
    confidence: float


class V4PeopleResult(BaseModel):
    values: list[V4Person]


class V4SmartCropsResult(BaseModel):
    values: list[dict[str, Any]]


class V4ImageAnalysisResponse(BaseModel):
    modelVersion: str
    captionResult: Optional[V4Caption] = None
    denseCaptionsResult: Optional[V4DenseCaptionsResult] = None
    metadata: ImageMetadata
    tagsResult: Optional[V4TagsResult] = None
    objectsResult: Optional[V4ObjectsResult] = None
    readResult: Optional[V4ReadResult] = None
    peopleResult: Optional[V4PeopleResult] = None
    smartCropsResult: Optional[V4SmartCropsResult] = None


# ---------------------------------------------------------------------------
# Error response (matches Azure error envelope)
# ---------------------------------------------------------------------------

class InnerError(BaseModel):
    code: str
    message: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    innererror: Optional[InnerError] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
