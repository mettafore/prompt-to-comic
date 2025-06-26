# Prompt-to-Comic – Backend Specification

## 🔍 Overview
This backend powers the **Prompt-to-Comic** app. It uses a LangGraph-based architecture to transform a user prompt into a multi-panel comic strip. It parses the prompt, breaks it into visual beats, generates image prompts, synthesizes artwork using an image API, and assembles the final comic strip into a PNG and optional PDF.

---

## 📊 Architecture Summary

**LangGraph Nodes**:
- `SceneParser` → Extract characters, setting, actions
- `PanelPlanner` → Break into 2–6 visual panels
- `PromptGenerator` → Text-to-image prompt per panel
- `ImageGenerator` → Calls DALL·E/SDXL
- `ComicLayout` → Lays out panels, generates PNG & PDF

All nodes are composable, stateless, and tested independently.

**FastAPI Endpoints**:
- `POST /generate` → Accepts prompt, style, panel count
- `GET /status/{job_id}` → Returns progress and output links
- `GET /health` → Returns "OK" for health check

---

## 📂 Folder Structure
```
backend/
├── app/
│   ├── main.py              # FastAPI app entrypoint
│   ├── config.py            # Pydantic settings
│   ├── schemas.py           # Input/output dataclasses
│   ├── graphs/
│   │   ├── comic_graph.py  # LangGraph flow logic
│   │   └── nodes/
│   │       ├── scene_parser.py
│   │       ├── panel_planner.py
│   │       ├── prompt_generator.py
│   │       ├── image_generator.py
│   │       └── comic_layout.py
│   ├── utils/
│   │   ├── storage.py
│   │   └── pdf.py
├── .env
├── Dockerfile
├── requirements.txt
└── tests/
```

---

## ⚖️ Dependencies
```txt
fastapi
langchain
langgraph
openai
pydantic
httpx
pillow
reportlab
python-multipart
python-dotenv
uvicorn
```

---

## 🔌 Node Definitions (LangGraph)

### 1. `SceneParser`
- **Input**: Raw text
- **Output**: `SceneComponents` (characters, setting, actions)
- **LLM Prompt**:
  > Extract characters, setting, tone, and key actions from the following prompt. Return a structured JSON.

### 2. `PanelPlanner`
- **Input**: `SceneComponents`, panel count (default: 3)
- **Output**: List[`PanelSpec`] (panel-by-panel description)
- **LLM Prompt**:
  > Break this scene into {panel_count} visually distinct comic panels. Each panel must have setting, visible characters, and action.

### 3. `PromptGenerator`
- **Input**: `PanelSpec`, art style
- **Output**: `ImagePrompt`
- **LLM Prompt**:
  > Convert this panel spec into a DALL·E prompt using the "{style}" art style. Include environment, character mood, lighting, and framing.

### 4. `ImageGenerator`
- **Input**: `ImagePrompt`
- **Output**: `ImageFile` (path)
- **Logic**: Calls OpenAI DALL·E or Replicate API and saves result.

### 5. `ComicLayout`
- **Input**: List of `ImageFile`s
- **Output**: `comic.png`, `comic.pdf`
- **Logic**: 
  - Arrange 2 or 3-panel grid
  - Optional speech bubble stubs
  - Use Pillow for layout and ReportLab for PDF

---

## 🚨 FastAPI Endpoints

### `POST /generate`
**Body**:
```json
{
  "text": "Two kids in a spaceship arguing about pizza",
  "style": "Graphic Novel",
  "panels": 3
}
```
**Response**:
```json
{ "job_id": "abc123" }
```

### `GET /status/{job_id}`
**Response**:
```json
{
  "state": "done",
  "comic_url": "/comics/abc123/comic.png",
  "pdf_url": "/comics/abc123/comic.pdf"
}
```

### `GET /health`
**Response**:
```json
{ "status": "ok" }
```

---

## 🌐 Environment Config (.env)
```env
OPENAI_API_KEY=sk-...
IMAGE_API_URL=https://...
STORAGE_DIR=./output
```

---

## 🔧 Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🏋️ Testing Strategy

### Unit Tests
- Each LangGraph node has tests using mocked LLMs and image API
- Validate schema compliance (e.g., `PanelSpec` has all required fields)

### Integration Test
- End-to-end test from `/generate` to image + PDF output
- Use mock prompts + snapshot testing for comic layout

---

## ✅ MVP Milestones
- [x] Build LangGraph node pipeline
- [x] Wrap pipeline in FastAPI app
- [x] Connect to image model (OpenAI / SDXL)
- [x] Streamlit frontend integration
- [x] Dockerized deployment

---

## 🚀 Future Upgrades
- Add multilingual prompt handling
- Enable speech-to-prompt with Whisper
- Switch to local image model (Stable Diffusion XL)
- Add speech bubble generator
- Build comic episode flow (multi-prompt support)

---

## 💌 Contribution Guide
- PRs should include tests
- Follow [black](https://github.com/psf/black) for code formatting
- Use typed dataclasses (`@dataclass`) for all internal schemas
- Describe your LangGraph node’s contract in its docstring

---

Ready to hand off to an AI coding agent or build manually.
