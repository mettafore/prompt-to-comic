# Prompt-to-Comic – Frontend Specification

## 🌟 Goal
Create a one-screen Streamlit interface where users:
- Enter a creative prompt or scene
- Select an art style and number of panels
- Click "Generate Comic"
- View and download the resulting comic strip

---

## 💻 UI Flow

### 1. Title Section
- App title: **Prompt-to-Comic**
- Subtitle: “Turn your imagination into illustrated comic strips”
- Optional: preview GIF or sample comic banner

---

### 2. Input Panel
| UI Element       | Type         | Details                                   |
|------------------|--------------|-------------------------------------------|
| Prompt Input     | `st.text_area` | Multiline user input                     |
| Art Style        | `st.selectbox` | Options: Graphic Novel, Manga, Pixar, Noir |
| Panel Count      | `st.slider`    | Range: 2–6 panels                        |
| Submit Button    | `st.button`    | Label: "🎨 Generate Comic"               |

---

### 3. Status / Feedback Panel
- Show `st.spinner` during comic generation
- Optional: quotes like “Summoning space goats…”
- Poll `/status/{job_id}` every 3 seconds
- Display progress bar or stage updates

---

### 4. Result Panel
| Feature           | Component        | Details |
|-------------------|------------------|---------|
| Comic Viewer      | `st.image()` or `st.pyplot()` | Display comic |
| Download PDF      | `st.download_button()` | One-click PDF |
| Try Another       | `st.button()` | Clears state |

---

### 5. Footer (Optional)
- About the project
- Link to GitHub repo
- License / Contact info

---

## 📦 Directory Structure
```
frontend/
├── app.py
├── api.py
├── components/
│   ├── loader.py
│   └── comic_display.py
├── static/
│   ├── placeholder.png
│   └── styles.css
└── .env
```

---

## 🔌 API Integration (`api.py`)
```python
import httpx

BASE_URL = "http://localhost:8000"

def generate_comic(prompt: str, style: str, panels: int):
    response = httpx.post(f"{BASE_URL}/generate", json={
        "text": prompt,
        "style": style,
        "panels": panels
    }, timeout=300)
    return response.json()

def check_job_status(job_id: str):
    return httpx.get(f"{BASE_URL}/status/{job_id}").json()
```

---

## 🎨 Design & UX Guidelines

| Area        | Design Choice |
|-------------|---------------|
| Layout      | Centered, single column |
| Font        | Comic Neue or clean sans-serif |
| Colors      | White background, light gray cards, comic-color accents |
| Images      | Max width: 800px |
| Mobile UX   | Inputs stack vertically |
| Errors      | Use `st.error()` with messages from backend |

Optional:
- Add dark mode toggle
- Display panel thumbnails one by one
- Add image zoom on click

---

## 🧪 Streamlit Code Sketch (`app.py`)
```python
import streamlit as st
from api import generate_comic, check_job_status
import time

st.set_page_config(page_title="Prompt-to-Comic", page_icon="🎨", layout="centered")

st.title("🎨 Prompt-to-Comic")
st.caption("Turn your wildest ideas into illustrated comic strips.")

# Input panel
prompt = st.text_area("Describe your scene or idea", height=160)
style = st.selectbox("Choose an art style", ["Graphic Novel", "Manga", "Pixar", "Noir"])
panels = st.slider("Number of panels", 2, 6, 3)

if st.button("🎨 Generate Comic") and prompt:
    with st.spinner("Drawing your comic..."):
        result = generate_comic(prompt, style, panels)
        job_id = result["job_id"]

        # Polling job status
        status = check_job_status(job_id)
        while status["state"] != "done":
            st.info(status.get("message", "Processing..."))
            time.sleep(3)
            status = check_job_status(job_id)

        comic_url = status["comic_url"]
        st.image(comic_url, caption="Your Comic Strip", use_column_width=True)
        st.download_button("📅 Download PDF", comic_url.replace(".png", ".pdf"))
```

---

## 🌍 Deployment Checklist

- ✅ Add `streamlit`, `httpx`, `python-dotenv` to `requirements.txt`
- ✅ Set `.env` with backend URL if needed
- ✅ `Dockerfile`:
  ```Dockerfile
  FROM python:3.11-slim
  COPY . /app
  WORKDIR /app
  RUN pip install -r requirements.txt
  CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
  ```
- ✅ Deploy to:
  - [ ] Streamlit Community Cloud
  - [ ] Hugging Face Spaces
  - [ ] Fly.io / Render / EC2

---

## 🔮 Future Enhancements

- Speech bubble text overlays (from panel dialogue)
- Speech-to-prompt mode using Whisper
- Style preview thumbnails
- Panel drag-and-drop editing (custom order)
- User login + comic gallery
