"""
Generates realistic-looking mock responses for Azure Computer Vision endpoints.
All values are randomised on each call so repeated requests return varied data.
"""
from __future__ import annotations

import random
import string
import uuid
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _uuid() -> str:
    return str(uuid.uuid4())


def _confidence(lo: float = 0.70, hi: float = 0.99) -> float:
    return round(random.uniform(lo, hi), 8)


def _bbox(max_x: int = 1200, max_y: int = 900) -> dict:
    x = random.randint(0, max_x - 100)
    y = random.randint(0, max_y - 100)
    w = random.randint(50, min(300, max_x - x))
    h = random.randint(50, min(300, max_y - y))
    return {"x": x, "y": y, "w": w, "h": h}


def _bounding_box_v4() -> dict:
    x = random.randint(0, 900)
    y = random.randint(0, 600)
    return {
        "x": x,
        "y": y,
        "w": random.randint(50, 300),
        "h": random.randint(50, 300),
    }


def _bbox_str(max_x: int = 1200, max_y: int = 900) -> str:
    b = _bbox(max_x, max_y)
    return f"{b['x']},{b['y']},{b['w']},{b['h']}"


def _poly_bbox(x: int, y: int, w: int, h: int) -> list[int]:
    """Quadrilateral bounding polygon as flat 8-int list."""
    return [x, y, x + w, y, x + w, y + h, x, y + h]


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Corpus pools
# ---------------------------------------------------------------------------

OBJECT_LABELS = [
    "person", "car", "dog", "cat", "chair", "table", "laptop", "bottle",
    "cup", "book", "bicycle", "bus", "truck", "traffic light", "stop sign",
    "bird", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "skateboard",
    "surfboard", "tennis racket", "potted plant", "tv", "keyboard", "mouse",
    "remote", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush", "bench", "couch",
]

TAG_POOL = [
    "outdoor", "sky", "building", "tree", "road", "grass", "water", "person",
    "car", "food", "animal", "nature", "city", "architecture", "blue",
    "green", "white", "black", "red", "yellow", "night", "day", "cloudy",
    "sunny", "street", "indoor", "sport", "technology", "fashion", "art",
]

CATEGORY_NAMES = [
    "abstract_", "animal_", "building_", "dark_", "food_", "indoor_",
    "landscape_", "others_", "outdoor_", "people_", "plant_", "sky_",
    "sport_", "trans_", "water_",
]

CAPTION_TEMPLATES = [
    "a group of people standing in a park",
    "a busy city street with cars and pedestrians",
    "a dog sitting on a grassy lawn",
    "a kitchen with modern appliances",
    "a laptop computer on a wooden desk",
    "a cat sleeping on a couch",
    "a mountain landscape with snow-capped peaks",
    "a beach with clear blue water",
    "people dining at an outdoor restaurant",
    "a child playing with a toy",
    "a close-up of colourful flowers",
    "an aerial view of a dense forest",
    "a sports event with a large crowd",
    "a man riding a bicycle on a path",
    "a woman reading a book in a library",
]

BRAND_NAMES = [
    "Microsoft", "Apple", "Google", "Amazon", "Samsung", "Sony", "Nike",
    "Adidas", "Coca-Cola", "Pepsi", "Ford", "Toyota", "BMW", "Starbucks",
]

DOMINANT_COLORS = [
    "White", "Black", "Grey", "Red", "Orange", "Yellow", "Green",
    "Teal", "Blue", "Purple", "Brown", "Pink",
]

ACCENT_HEX = [
    "0E6CA8", "CF2D2D", "3D8C40", "E8A020", "7B3D9E",
    "1A7ABC", "D9534F", "5CB85C", "F0AD4E", "5BC0DE",
]

LANGUAGES = ["en", "fr", "de", "es", "it", "pt", "zh", "ja", "ko", "ar"]

ORIENTATIONS = ["Up", "Down", "Left", "Right"]

OCR_WORDS_POOL = [
    "Hello", "World", "Invoice", "Total", "Date", "Name", "Address",
    "Phone", "Email", "Company", "Product", "Quantity", "Price",
    "Lorem", "Ipsum", "Dolor", "Sit", "Amet", "Consectetur",
    "2024", "2025", "$", "100.00", "USD", "Receipt", "Order",
]

READ_SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "Lorem ipsum dolor sit amet consectetur adipiscing elit.",
    "Invoice number 12345 dated January 1 2025.",
    "Total amount due: $1,234.56",
    "Please contact support@example.com for assistance.",
    "Page 1 of 3",
    "CONFIDENTIAL - Do not distribute",
    "All rights reserved 2025",
]

# ---------------------------------------------------------------------------
# Shared sub-builders
# ---------------------------------------------------------------------------

def build_metadata() -> dict:
    return {
        "width": random.choice([640, 800, 1024, 1280, 1920]),
        "height": random.choice([480, 600, 768, 720, 1080]),
        "format": random.choice(["Jpeg", "Png", "Gif", "Bmp", "Webp"]),
    }


def build_tags(n: int = 8) -> list[dict]:
    chosen = random.sample(TAG_POOL, min(n, len(TAG_POOL)))
    return [{"name": t, "confidence": _confidence()} for t in chosen]


def build_categories(n: int = 3) -> list[dict]:
    chosen = random.sample(CATEGORY_NAMES, min(n, len(CATEGORY_NAMES)))
    return [
        {
            "name": c + random.choice(["", "text", "sign", "face", "body"]),
            "score": _confidence(0.50, 0.98),
            "detail": None,
        }
        for c in chosen
    ]


def build_description() -> dict:
    return {
        "tags": random.sample(TAG_POOL, 6),
        "captions": [
            {"text": random.choice(CAPTION_TEMPLATES), "confidence": _confidence()},
            {"text": random.choice(CAPTION_TEMPLATES), "confidence": _confidence(0.5, 0.75)},
        ],
    }


def build_color() -> dict:
    fg = random.choice(DOMINANT_COLORS)
    bg = random.choice(DOMINANT_COLORS)
    return {
        "dominantColorForeground": fg,
        "dominantColorBackground": bg,
        "dominantColors": random.sample(DOMINANT_COLORS, random.randint(1, 4)),
        "accentColor": random.choice(ACCENT_HEX),
        "isBWImg": random.random() < 0.1,
        "isBwImg": random.random() < 0.1,
    }


def build_adult() -> dict:
    is_adult = random.random() < 0.02
    is_racy = random.random() < 0.03
    is_gory = random.random() < 0.01
    return {
        "isAdultContent": is_adult,
        "isRacyContent": is_racy,
        "isGoryContent": is_gory,
        "adultScore": _confidence(0.001, 0.05) if not is_adult else _confidence(0.85, 0.99),
        "racyScore": _confidence(0.001, 0.06) if not is_racy else _confidence(0.80, 0.99),
        "goreScore": _confidence(0.001, 0.03) if not is_gory else _confidence(0.85, 0.99),
    }


def build_image_type() -> dict:
    return {
        "clipArtType": random.randint(0, 3),
        "lineDrawingType": random.randint(0, 1),
    }


def build_faces(n: int | None = None) -> list[dict]:
    count = n if n is not None else random.randint(0, 3)
    genders = ["Male", "Female"]
    return [
        {
            "age": random.randint(18, 75),
            "gender": random.choice(genders),
            "faceRectangle": {
                "left": random.randint(50, 400),
                "top": random.randint(50, 300),
                "width": random.randint(60, 150),
                "height": random.randint(60, 150),
            },
        }
        for _ in range(count)
    ]


def build_objects(n: int | None = None) -> list[dict]:
    count = n if n is not None else random.randint(1, 5)
    return [
        {
            "rectangle": _bbox(),
            "object": random.choice(OBJECT_LABELS),
            "confidence": _confidence(),
            "parent": None,
        }
        for _ in range(count)
    ]


def build_brands(n: int | None = None) -> list[dict]:
    count = n if n is not None else random.randint(0, 2)
    chosen = random.sample(BRAND_NAMES, min(count, len(BRAND_NAMES)))
    return [
        {
            "name": b,
            "confidence": _confidence(),
            "rectangle": _bbox(),
        }
        for b in chosen
    ]


# ---------------------------------------------------------------------------
# v3.2 full response builders
# ---------------------------------------------------------------------------

def build_analyze_response(visual_features: list[str] | None = None) -> dict:
    return {
        "categories": build_categories(),
        "adult": build_adult(),
        "color": build_color(),
        "imageType": build_image_type(),
        "tags": build_tags(),
        "description": build_description(),
        "faces": build_faces(),
        "objects": build_objects(),
        "brands": build_brands(),
        "requestId": _uuid(),
        "metadata": build_metadata(),
        "modelVersion": "2023-10-01",
    }


def build_describe_response(max_candidates: int = 3) -> dict:
    captions = [
        {"text": random.choice(CAPTION_TEMPLATES), "confidence": _confidence()}
        for _ in range(min(max_candidates, random.randint(1, 3)))
    ]
    return {
        "description": {
            "tags": random.sample(TAG_POOL, 6),
            "captions": sorted(captions, key=lambda c: c["confidence"], reverse=True),
        },
        "requestId": _uuid(),
        "metadata": build_metadata(),
        "modelVersion": "2023-10-01",
    }


def build_detect_response() -> dict:
    return {
        "objects": build_objects(random.randint(1, 6)),
        "requestId": _uuid(),
        "metadata": build_metadata(),
        "modelVersion": "2023-10-01",
    }


def build_tag_response() -> dict:
    return {
        "tags": build_tags(random.randint(5, 12)),
        "requestId": _uuid(),
        "metadata": build_metadata(),
        "modelVersion": "2023-10-01",
    }


def build_ocr_response() -> dict:
    def _word():
        text = random.choice(OCR_WORDS_POOL)
        return {
            "boundingBox": _bbox_str(800, 600),
            "text": text,
            "confidence": _confidence(),
        }

    def _line():
        words = [_word() for _ in range(random.randint(2, 6))]
        return {
            "boundingBox": _bbox_str(800, 600),
            "words": words,
        }

    def _region():
        lines = [_line() for _ in range(random.randint(2, 5))]
        return {
            "boundingBox": _bbox_str(800, 600),
            "lines": lines,
        }

    return {
        "language": "en",
        "textAngle": round(random.uniform(-1.5, 1.5), 4),
        "orientation": random.choice(ORIENTATIONS),
        "regions": [_region() for _ in range(random.randint(1, 3))],
        "modelVersion": "2023-10-01",
    }


def build_read_result(operation_id: str, status: str = "succeeded") -> dict:
    def _word(x: int, y: int):
        text = random.choice(OCR_WORDS_POOL)
        w = random.randint(30, 100)
        h = random.randint(15, 30)
        return {
            "boundingBox": _poly_bbox(x, y, w, h),
            "text": text,
            "confidence": _confidence(),
        }

    def _line():
        sentence = random.choice(READ_SENTENCES)
        x, y = random.randint(10, 200), random.randint(10, 700)
        words_raw = sentence.split()
        words = []
        cx = x
        for w_text in words_raw:
            ww = len(w_text) * 9
            words.append({
                "boundingBox": _poly_bbox(cx, y, ww, 20),
                "text": w_text,
                "confidence": _confidence(),
            })
            cx += ww + 5
        return {
            "boundingBox": _poly_bbox(x, y, cx - x, 22),
            "text": sentence,
            "words": words,
            "appearance": {
                "style": {"name": "other", "confidence": _confidence()},
            },
        }

    def _page():
        return {
            "page": 1,
            "angle": round(random.uniform(-0.5, 0.5), 4),
            "width": 1700.0,
            "height": 2200.0,
            "unit": "pixel",
            "lines": [_line() for _ in range(random.randint(3, 8))],
        }

    result: dict = {
        "status": status,
        "createdDateTime": _now_iso(),
        "lastUpdatedDateTime": _now_iso(),
    }

    if status == "succeeded":
        result["analyzeResult"] = {
            "version": "3.2.0",
            "modelVersion": "2022-04-30",
            "readResults": [_page()],
        }
    elif status == "failed":
        result["analyzeResult"] = None

    return result


def build_area_of_interest_response() -> dict:
    return {
        "areaOfInterest": _bbox(),
        "requestId": _uuid(),
        "metadata": build_metadata(),
        "modelVersion": "2023-10-01",
    }


# ---------------------------------------------------------------------------
# v4.0 response builder
# ---------------------------------------------------------------------------

def build_v4_response(features: list[str] | None = None) -> dict:
    all_features = features or [
        "caption", "denseCaptions", "tags", "objects", "read", "people", "smartCrops",
    ]

    def _v4_bbox():
        x = random.randint(0, 900)
        y = random.randint(0, 600)
        return {"x": x, "y": y, "w": random.randint(50, 300), "h": random.randint(50, 300)}

    def _poly(x, y, w, h):
        return [
            {"x": x, "y": y},
            {"x": x + w, "y": y},
            {"x": x + w, "y": y + h},
            {"x": x, "y": y + h},
        ]

    def _v4_word(text, x, y):
        ww = len(text) * 9
        return {
            "text": text,
            "boundingPolygon": _poly(x, y, ww, 20),
            "confidence": _confidence(),
        }

    response: dict = {
        "modelVersion": "2024-02-01",
        "metadata": build_metadata(),
    }

    if "caption" in all_features:
        response["captionResult"] = {
            "text": random.choice(CAPTION_TEMPLATES),
            "confidence": _confidence(),
        }

    if "denseCaptions" in all_features:
        response["denseCaptionsResult"] = {
            "values": [
                {
                    "text": random.choice(CAPTION_TEMPLATES),
                    "confidence": _confidence(),
                    "boundingBox": _v4_bbox(),
                }
                for _ in range(random.randint(2, 6))
            ]
        }

    if "tags" in all_features:
        response["tagsResult"] = {
            "values": [
                {"name": t, "confidence": _confidence()}
                for t in random.sample(TAG_POOL, random.randint(5, 10))
            ]
        }

    if "objects" in all_features:
        response["objectsResult"] = {
            "values": [
                {
                    "id": _uuid(),
                    "boundingBox": _v4_bbox(),
                    "tags": [
                        {"name": random.choice(OBJECT_LABELS), "confidence": _confidence()}
                    ],
                }
                for _ in range(random.randint(1, 5))
            ]
        }

    if "read" in all_features:
        lines = []
        for _ in range(random.randint(2, 5)):
            sentence = random.choice(READ_SENTENCES)
            x, y = random.randint(10, 200), random.randint(10, 700)
            words_raw = sentence.split()
            words = []
            cx = x
            for w_text in words_raw:
                ww = len(w_text) * 9
                words.append(_v4_word(w_text, cx, y))
                cx += ww + 5
            lines.append({
                "text": sentence,
                "boundingPolygon": _poly(x, y, cx - x, 22),
                "words": words,
            })
        response["readResult"] = {"blocks": [{"lines": lines}]}

    if "people" in all_features:
        response["peopleResult"] = {
            "values": [
                {
                    "id": _uuid(),
                    "boundingBox": _v4_bbox(),
                    "confidence": _confidence(),
                }
                for _ in range(random.randint(0, 4))
            ]
        }

    if "smartCrops" in all_features:
        ratios = ["0.9", "1.33", "1.78", "0.5"]
        response["smartCropsResult"] = {
            "values": [
                {
                    "aspectRatio": float(r),
                    "boundingBox": _v4_bbox(),
                }
                for r in random.sample(ratios, random.randint(1, len(ratios)))
            ]
        }

    return response


# ---------------------------------------------------------------------------
# Error helpers
# ---------------------------------------------------------------------------

def error_missing_key() -> dict:
    return {
        "error": {
            "code": "401",
            "message": "Access denied due to invalid subscription key or wrong API endpoint. "
                       "Make sure to provide a valid key for an active subscription and use "
                       "a correct regional API endpoint for your resource.",
        }
    }


def error_invalid_image() -> dict:
    return {
        "error": {
            "code": "InvalidImageFormat",
            "message": "Input data is not a valid image.",
            "innererror": {
                "code": "InvalidImageFormat",
                "message": "Image format is not supported.",
            },
        }
    }


def error_image_too_small() -> dict:
    return {
        "error": {
            "code": "InvalidImageSize",
            "message": "Image size is too small. The minimum image dimension is 50x50 pixels.",
            "innererror": {
                "code": "ImageTooSmall",
                "message": "Image is smaller than the minimum required size.",
            },
        }
    }


def error_not_found(operation_id: str) -> dict:
    return {
        "error": {
            "code": "NotFound",
            "message": f"Resource not found: {operation_id}",
        }
    }
