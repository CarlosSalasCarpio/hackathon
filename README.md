# AI Video Shopper

AI Video Shopper converts a short MP4 video into an instant shopping experience. The app extracts representative frames, uses Google Gemini to identify commercial products, and enriches results with real-time retail pricing and purchase links.

## Features
- Upload MP4 videos via a Streamlit UI
- Extract equidistant frames for analysis
- Use Google Gemini (Gemini 3 Flash) to detect products from frames
- Enrich detected products with official prices and purchase links
- Clean, modern product card UI for quick browsing

## Requirements
- Python 3.10+
- A Google Gemini API key with access to the model used
- OS with read/write permissions for temporary files

## Python Dependencies
- streamlit
- opencv-python
- pillow
- google-genai
- python-dotenv

Install with:
pip install -r requirements.txt
(or) pip install streamlit opencv-python pillow google-genai python-dotenv

## Configuration
1. Create a `.env` file in the project root.
2. Add your Gemini API key:
GEMINI_API_KEY=your_api_key_here

## Usage
1. Run the app:
streamlit run app.py
2. Upload an MP4 video in the UI.
3. Click "Start AI Analysis" to begin detection and enrichment.
4. View detected products in the right-hand panel and follow purchase links.

## How it works (brief)
1. The app saves the uploaded MP4 as `temp_video.mp4`.
2. It extracts a small number of equidistant frames using OpenCV.
3. Frames and a structured prompt are sent to Google Gemini to identify up to 3 relevant commercial items (JSON output).
4. For each item, the app queries Gemini with a search tool to obtain price, description, and purchase link.
5. Results are rendered as product cards in Streamlit.

## Notes & Troubleshooting
- Ensure `GEMINI_API_KEY` is set and valid; the app will stop with an error if missing.
- If no frames are extracted, confirm OpenCV can read the uploaded file and that the video contains frames.
- Temporary files (e.g., `temp_video.mp4`) are written to the working directory. Remove them as needed.
- Model ID used in the app: `gemini-3-flash-preview`. Adjust as required by your access.

## Security & Privacy
- Do not commit your `.env` file or API key to source control.
- Uploaded videos are processed locally by the app and temporarily saved; handle sensitive content accordingly.

## License
For hackathon/demo use. Review and apply a license of your choice for production use.