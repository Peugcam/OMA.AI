"""Quick test to start the dashboard"""
import sys
import os

# Fix Windows encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.stdout.reconfigure(encoding='utf-8')

print("Python version:", sys.version)
print("Starting import test...")

try:
    import gradio as gr
    print("[OK] Gradio imported successfully")
    print("     Version:", gr.__version__)
except Exception as e:
    print("[ERROR] Failed to import Gradio:", e)
    sys.exit(1)

try:
    from video_dashboard_complete import create_video_dashboard
    print("[OK] Dashboard module imported successfully")
except Exception as e:
    print("[ERROR] Failed to import dashboard:", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[STARTING] Creating dashboard...")
try:
    demo = create_video_dashboard()
    print("[OK] Dashboard created successfully")
except Exception as e:
    print("[ERROR] Failed to create dashboard:", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[SERVER] Starting server on http://localhost:7860...")
try:
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
except Exception as e:
    print("[ERROR] Failed to launch:", e)
    import traceback
    traceback.print_exc()
    sys.exit(1)
