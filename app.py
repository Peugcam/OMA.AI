"""
OMA Video Generator - Universal Entry Point
============================================

Entry point for cloud platforms (Hugging Face Spaces, Railway, Render, Heroku).
"""

import os

# Get port from environment (Cloud Run, Railway, Render, Heroku assign dynamic ports)
# Cloud Run uses 8080 by default, Hugging Face uses 7860
PORT = int(os.environ.get("PORT", 8080))

# Set Gradio environment variables
os.environ.setdefault("GRADIO_SERVER_NAME", "0.0.0.0")
os.environ.setdefault("GRADIO_SERVER_PORT", str(PORT))

# Create required directories
for dir_path in ["outputs/videos", "outputs/temp", "outputs/images", "logs"]:
    os.makedirs(dir_path, exist_ok=True)

# Import dashboard
from video_dashboard_complete import create_video_dashboard

demo = create_video_dashboard()

if __name__ == "__main__":
    print(f"🚀 Starting OMA Video Generator on port {PORT}")
    demo.launch(
        server_name="0.0.0.0",
        server_port=PORT,
        share=False,
        show_error=False
    )
