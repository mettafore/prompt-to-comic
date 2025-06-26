# 🎨 Prompt-to-Comic

**Prompt-to-Comic** is an AI-powered app that turns a creative scene or idea into a visual comic strip. Built with LangGraph, GPT-4o, FastAPI, and DALL·E/SDXL, the system parses your prompt, breaks it into panels, generates art for each scene, and assembles it into a polished, downloadable comic.

---

## 🚀 Quick Start (One Command!)

```bash
# Clone and run with Docker (easiest way)
git clone https://github.com/yourusername/prompt-to-comic
cd prompt-to-comic
docker-compose up --build
```

Then visit: **http://localhost:8501** 🎉

---

## 📸 Demo
![demo-preview](static/demo.gif)  
👉 Try it with a prompt like:

> "Two kids in a spaceship arguing about pineapple pizza while a robot watches."

---

## 🧠 How It Works

| Stage | What Happens |
|-------|---------------|
| 🧾 Scene Parsing | Break down prompt into characters, setting, actions |
| 🎞️ Panel Planning | Split the scene into 2–6 visual panels |
| 🖋️ Prompt Generation | Turn each panel into a DALL·E/SDXL prompt |
| 🧠 AI Image Gen | Generate images via API |
| 🖼️ Comic Layout | Arrange into a comic strip and export to PNG/PDF |

Built using **LangGraph**, each stage is a reusable, testable node in a directed graph.

---

## ⚙️ Tech Stack

| Layer        | Tech                                |
|--------------|-------------------------------------|
| Backend      | **FastAPI**, LangGraph, OpenAI API |
| Frontend     | **Streamlit**                       |
| Image Models | DALL·E 3 / Replicate SDXL           |
| Layout       | Pillow, ReportLab (PDFs)            |
| Infra        | Docker, uv, HTTPX                   |

---

## 🛠️ Setup Options

### Option 1: Docker Compose (Recommended)
```bash
git clone https://github.com/yourusername/prompt-to-comic
cd prompt-to-comic
docker-compose up --build
```

### Option 2: Local Development
```bash
# Backend
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend  
uv sync
uv run streamlit run app.py
```

### Option 3: Live Demo
Visit: [your-railway-app.railway.app](https://your-railway-app.railway.app)

---

## 🔧 Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-your-key-here
   ```

3. Restart the services:
   ```bash
   docker-compose down && docker-compose up --build
   ```

---

## 🌐 API Endpoints

### `POST /generate`
Generate comic from prompt.
```json
{
  "text": "pirate vs ninja showdown at a sushi bar",
  "style": "Manga",
  "panels": 3
}
```

### `GET /status/{job_id}`
Poll job status and result URL.

### `GET /health`
Returns `{ "status": "ok" }`

---

## 📦 Project Structure
```
prompt-to-comic/
├── app/               # FastAPI backend
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   ├── graphs/
│   │   ├── comic_graph.py
│   │   └── nodes/
│   └── utils/
├── frontend/          # Streamlit frontend
│   ├── app.py
│   ├── api.py
│   └── components/
├── static/
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🛣️ Roadmap
- [ ] Webtoon-style vertical layout
- [ ] Whisper-based voice prompt entry
- [ ] Speech bubble overlays from GPT
- [ ] Comic series creation support
- [ ] User login and gallery

---

## 👨‍💻 Contributing
We love contributors! You can:
- Build new LangGraph nodes
- Add new art styles or models
- Improve layout engine
- Help translate prompts

Please follow our style guide:
- Use `@dataclass` for all schemas
- Format code with `black`
- Write clear node-level docstrings

---

## 📜 License
MIT License

---

## 🙏 Acknowledgements
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [OpenAI](https://openai.com)
- [Replicate](https://replicate.com)
- [Streamlit](https://streamlit.io)
- Everyone building creative tools with AI 💛

> Prompt-to-Comic was built to empower storytellers. Whether you're a dreamer, writer, or just messing around — we can't wait to see what you create!
