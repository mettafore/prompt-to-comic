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

        # Polling job status (dummy loop)
        status = check_job_status(job_id)
        while status["state"] != "done":
            st.info(status.get("message", "Processing..."))
            time.sleep(1)
            status = check_job_status(job_id)

        comic_url = status["comic_url"]
        st.image(comic_url, caption="Your Comic Strip", use_column_width=True)
        st.download_button("📅 Download PDF", comic_url.replace(".png", ".pdf")) 