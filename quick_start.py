#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick start script for OMA Dashboard"""

import os
import sys
import webbrowser
from threading import Timer

# Fix encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("OMA VIDEO GENERATOR - Starting Dashboard")
print("="*60)

# Create required directories
for dir_path in ["outputs/videos", "outputs/temp", "outputs/images", "logs"]:
    os.makedirs(dir_path, exist_ok=True)
    print(f"[OK] Directory: {dir_path}")

# Import and create dashboard
print("\n[LOADING] Importing dashboard module...")
try:
    from video_dashboard_complete import create_video_dashboard
    print("[OK] Dashboard module loaded")
except Exception as e:
    print(f"[ERROR] Failed to import: {e}")
    sys.exit(1)

print("[CREATING] Building dashboard interface...")
try:
    demo = create_video_dashboard()
    print("[OK] Dashboard created")
except Exception as e:
    print(f"[ERROR] Failed to create dashboard: {e}")
    sys.exit(1)

# Open browser after 2 seconds
def open_browser():
    print("[BROWSER] Opening http://localhost:7860")
    webbrowser.open('http://localhost:7860')

Timer(2.0, open_browser).start()

# Launch server
print("\n" + "="*60)
print("DASHBOARD STARTING ON: http://localhost:7860")
print("="*60)
print("\nPress CTRL+C to stop the server")
print()

try:
    from pathlib import Path
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False,
        allowed_paths=[
            str(Path("outputs/videos").absolute()),
            str(Path("outputs/temp").absolute()),
            str(Path("outputs/images").absolute()),
            str(Path(".").absolute())
        ]
    )
except KeyboardInterrupt:
    print("\n\n[SHUTDOWN] Server stopped by user")
except Exception as e:
    print(f"\n[ERROR] Server error: {e}")
    import traceback
    traceback.print_exc()
