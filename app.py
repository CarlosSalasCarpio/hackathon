import streamlit as st
import cv2
import json
import os
import shutil
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Video Shopper | Visa Hackathon", layout="wide")
load_dotenv()

# --- MODERN UI STYLING (English) ---
st.markdown("""
    <style>
    /* Main background */
    .main { background-color: #f4f7f6; }
    
    /* Product Card Design */
    .product-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e1e4e8;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }
    
    /* Text Colors (Ensuring visibility) */
    .product-title { color: #1a1a1a; font-weight: bold; margin-bottom: 8px; }
    .product-desc { color: #4a4a4a; font-size: 0.9em; line-height: 1.4; margin-bottom: 12px; }
    .price-tag { color: #007bff; font-weight: 700; font-size: 1.15em; }
    
    /* Buy Button */
    .buy-button {
        display: inline-block;
        padding: 8px 20px;
        background-color: #1a1a1a;
        color: #ffffff !important;
        text-decoration: none;
        border-radius: 6px;
        font-weight: 500;
        text-align: center;
        margin-top: 10px;
        width: 100%;
    }
    .buy-button:hover { background-color: #333333; }
    </style>
    """, unsafe_allow_html=True)

# --- INITIALIZATION ---
# Using the model that proved successful in previous tests
MODEL_ID = "gemini-3-flash-preview"

if "GEMINI_API_KEY" not in os.environ:
    st.error("Missing GEMINI_API_KEY. Please check your .env file.")
    st.stop()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def extract_frames(video_path, num_frames=3):
    """Efficiently extracts equidistant frames for AI processing."""
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []
    if total_frames <= 0: return []
    
    for i in range(num_frames):
        pos = int((total_frames / (num_frames + 1)) * (i + 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(Image.fromarray(frame))
    cap.release()
    return frames

# --- MAIN INTERFACE ---
st.title("🛍️ AI Video Shopper")
st.markdown("##### Transform your video viewing experience into an instant shopping opportunity.")

col_video, col_products = st.columns([2, 1])

with col_video:
    # Video Upload Section
    uploaded_file = st.file_uploader("Upload video file (MP4)", type=["mp4"])
    
    if uploaded_file:
        # Temporary save for OpenCV processing
        with open("temp_video.mp4", "wb") as f:
            f.write(uploaded_file.read())
        
        st.video("temp_video.mp4")
        
        if st.button("🔍 Start AI Analysis", use_container_width=True):
            with st.spinner("AI is analyzing the video and identifying products..."):
                frames = extract_frames("temp_video.mp4")
                
                if not frames:
                    st.error("Error: Could not extract frames from the video.")
                else:
                    # STEP 1: Computer Vision Phase
                    vision_prompt = """
                    Analyze these video frames and identify the 3 most relevant commercial products.
                    Return strictly a JSON object with this structure:
                    {"items": [{"brand": "Brand Name", "model": "Model/Name", "category": "Category"}]}
                    """
                    
                    try:
                        vision_res = client.models.generate_content(
                            model=MODEL_ID,
                            contents=[vision_prompt, *frames],
                            config=types.GenerateContentConfig(response_mime_type="application/json")
                        )
                        detected_items = json.loads(vision_res.text).get('items', [])
                        
                        # STEP 2: Search & Enrichment Phase (Real-time prices and links)
                        search_tool = types.Tool(google_search=types.GoogleSearch())
                        final_results = []

                        for item in detected_items:
                            search_prompt = f"Find the official retail price and purchase link for: {item['brand']} {item['model']}. Return JSON with fields: name, description, price, link."
                            
                            search_res = client.models.generate_content(
                                model=MODEL_ID,
                                contents=search_prompt,
                                config=types.GenerateContentConfig(
                                    tools=[search_tool],
                                    response_mime_type="application/json"
                                )
                            )
                            # Handle potential list responses from the model
                            data = json.loads(search_res.text)
                            product_data = data[0] if isinstance(data, list) else data
                            final_results.append(product_data)
                        
                        st.session_state.results = final_results
                    except Exception as e:
                        st.error(f"Analysis Failed: {str(e)}")

with col_products:
    st.subheader("🛒 Detected Products")
    
    if "results" in st.session_state:
        for p in st.session_state.results:
            # Rendering Product Cards with high-contrast text
            st.markdown(f"""
                <div class="product-card">
                    <div class="product-title">{p.get('name', 'Product')}</div>
                    <div class="product-desc">{p.get('description', 'No description available.')}</div>
                    <div class="price-tag">{p.get('price', 'Price on request')}</div>
                    <a href="{p.get('link', '#')}" target="_blank" class="buy-button">Buy Now</a>
                </div>
                """, unsafe_allow_html=True)
    else:
        # Guidance for the user
        st.info("Upload a video and click 'Start AI Analysis' to discover products.")

# --- FOOTER ---
st.divider()
st.caption("Powered by Gemini 3 Flash & Google Search Technology | Hackathon 2026")