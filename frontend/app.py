import streamlit as st
from api import generate_comic, check_job_status, get_comic_image, get_panel_image
import time
import base64
from io import BytesIO

st.set_page_config(page_title="Prompt-to-Comic", page_icon="🎨", layout="centered")

st.title("🎨 Prompt-to-Comic")
st.caption("Turn your wildest ideas into illustrated comic strips using AI!")

# Input panel
with st.container():
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt = st.text_area("Describe your scene or idea", height=120, 
                             placeholder="e.g., A robot and a cat having a tea party in a garden")
    
    with col2:
        style = st.selectbox("Art Style", ["Manga", "Graphic Novel", "Pixar", "Noir"])
        panels = st.slider("Panels", 2, 6, 3)

# Generate button
if st.button("🎨 Generate Comic", type="primary", use_container_width=True) and prompt:
    # Create a placeholder for progress
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    result_placeholder = st.empty()
    
    try:
        # Step 1: Send generation request
        progress_placeholder.progress(0, text="Sending request to backend...")
        result = generate_comic(prompt, style, panels)
        
        if "error" in result:
            st.error(f"❌ Generation failed: {result['error']}")
            st.stop()
        
        job_id = result["job_id"]
        st.success(f"✅ Job created! ID: {job_id[:8]}...")
        
        # Step 2: Poll for completion
        progress_placeholder.progress(25, text="Processing your comic...")
        status = check_job_status(job_id)
        
        while status.get("state") not in ["done", "failed"]:
            status_placeholder.info(f"🔄 {status.get('message', 'Processing...')}")
            time.sleep(2)
            status = check_job_status(job_id)
            
            if "error" in status:
                st.error(f"❌ Status check failed: {status['error']}")
                st.stop()
        
        if status.get("state") == "failed":
            st.error(f"❌ Comic generation failed: {status.get('message', 'Unknown error')}")
            st.stop()
        
        # Step 3: Display results
        progress_placeholder.progress(100, text="Comic ready!")
        status_placeholder.success("🎉 Your comic is ready!")
        
        # Display the final comic
        if status.get("comic_data"):
            try:
                # Decode base64 comic data
                comic_data = base64.b64decode(status["comic_data"])
                
                # Display comic
                st.subheader("🎨 Your Generated Comic")
                st.image(comic_data, caption=f"'{prompt[:50]}...' in {style} style", use_column_width=True)
                
                # Download button
                st.download_button(
                    label="📥 Download Comic",
                    data=comic_data,
                    file_name=f"comic_{job_id[:8]}.png",
                    mime="image/png"
                )
                
            except Exception as e:
                st.error(f"❌ Failed to display comic: {e}")
        
        # Display individual panels
        if status.get("panel_images"):
            st.subheader("🖼️ Individual Panels")
            
            # Create columns for panels
            cols = st.columns(min(len(status["panel_images"]), 3))
            
            for i, panel_b64 in enumerate(status["panel_images"]):
                try:
                    panel_data = base64.b64decode(panel_b64)
                    col_idx = i % 3
                    
                    with cols[col_idx]:
                        st.image(panel_data, caption=f"Panel {i+1}", use_column_width=True)
                        
                        # Download individual panel
                        st.download_button(
                            label=f"📥 Panel {i+1}",
                            data=panel_data,
                            file_name=f"panel_{i+1}_{job_id[:8]}.png",
                            mime="image/png",
                            key=f"panel_{i}"
                        )
                        
                except Exception as e:
                    st.error(f"❌ Failed to display panel {i+1}: {e}")
        
        # Show metadata
        with st.expander("📊 Generation Details"):
            st.json({
                "Job ID": job_id,
                "Prompt": prompt,
                "Style": style,
                "Panels": panels,
                "Status": status.get("state"),
                "Message": status.get("message")
            })
    
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        st.exception(e)

# Add some helpful info
with st.sidebar:
    st.header("ℹ️ How it works")
    st.markdown("""
    1. **Describe your scene** - Be creative and detailed!
    2. **Choose a style** - Manga, Graphic Novel, Pixar, or Noir
    3. **Set panel count** - 2-6 panels for your story
    4. **Generate** - AI creates your comic strip
    
    **Tips:**
    - Include characters, setting, and actions
    - Be specific about what happens in each panel
    - Try different styles for different moods
    """)
    
    st.header("🎨 Style Guide")
    st.markdown("""
    - **Manga**: Anime-inspired, expressive characters
    - **Graphic Novel**: Bold lines, dramatic lighting
    - **Pixar**: 3D-style, warm and friendly
    - **Noir**: Dark, moody, high contrast
    """)

# Footer
st.markdown("---")
st.caption("Powered by LangGraph, OpenAI, and Streamlit 🚀") 