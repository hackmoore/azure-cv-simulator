# Azure Computer Vision API Simulator

A local Python/FastAPI simulator of the [Azure Computer Vision REST API](https://learn.microsoft.com/en-us/azure/ai-services/computer-vision/) (v3.2 and v4.0). Returns realistic randomised mock responses for every covered endpoint — no Azure subscription required.

Useful for local development, integration testing, and CI pipelines.

## Endpoints

### v3.2 (`/vision/v3.2/...`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/vision/v3.2/analyze` | Analyze Image |
| `POST` | `/vision/v3.2/describe` | Describe Image |
| `POST` | `/vision/v3.2/detect` | Detect Objects |
| `POST` | `/vision/v3.2/tag` | Tag Image |
| `POST` | `/vision/v3.2/ocr` | OCR (legacy) |
| `POST` | `/vision/v3.2/read/analyze` | Read – Submit Async Job |
| `GET` | `/vision/v3.2/read/analyzeResults/{operationId}` | Read – Poll Result |
| `DELETE` | `/vision/v3.2/read/analyzeResults/{operationId}` | Read – Delete Result |
| `POST` | `/vision/v3.2/generateThumbnail` | Generate Thumbnail (returns PNG) |
| `POST` | `/vision/v3.2/areaOfInterest` | Get Area of Interest |

### v4.0 (`/computervision/...`)

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/computervision/imageanalysis:analyze` | Image Analysis (caption, denseCaptions, tags, objects, read, people, smartCrops) |
| `POST` | `/computervision/imageanalysis:segment` | Image Segmentation / Background Removal (returns PNG) |
| `POST` | `/computervision/retrieval:vectorizeImage` | Vectorize Image (1024-dim embedding) |
| `POST` | `/computervision/retrieval:vectorizeText` | Vectorize Text (1024-dim embedding) |

## Running Locally

### Docker (recommended)

```bash
docker pull ghcr.io/hackmoore/azure-cv-simulator:latest
docker run -p 7001:8000 ghcr.io/hackmoore/azure-cv-simulator:latest
```

### Docker Compose

```bash
docker compose up -d
```

The simulator will be available at `http://localhost:7001`.

### Python

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 7001
```

## Authentication

All endpoints require the `Ocp-Apim-Subscription-Key` header. Any non-empty string is accepted:

```bash
curl -X POST http://localhost:7001/vision/v3.2/analyze \
  -H "Ocp-Apim-Subscription-Key: any-value" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/image.jpg"}'
```

## Interactive Docs

Swagger UI is available at `http://localhost:7001/docs` once the server is running.

## Project Structure

```
├── main.py              # FastAPI app entry point
├── mock_data.py         # Randomised response generators
├── models.py            # Pydantic models matching Azure response shapes
├── routers/
│   ├── v32.py           # v3.2 endpoint handlers
│   └── v40.py           # v4.0 endpoint handlers
├── Dockerfile
└── docker-compose.yml
```
