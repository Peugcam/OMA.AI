"""
API Server Launcher
==================

Production-ready launcher for the OMA API.
"""

import sys
import io
import os
import uvicorn
from pathlib import Path

# Fix Windows encoding for emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def main():
    """Launch API server"""
    from api.config import settings

    # Get port from environment (Railway, Render, Heroku assign dynamic ports)
    port = int(os.environ.get("PORT", settings.API_PORT))
    host = os.environ.get("HOST", settings.API_HOST)

    print(f"\n🚀 Starting {settings.APP_NAME}")
    print(f"📊 Version: {settings.APP_VERSION}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 URL: http://{host}:{port}{settings.API_PREFIX}")
    print(f"📚 Docs: http://{host}:{port}{settings.API_PREFIX}/docs")
    print()

    # Run server
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=settings.DEBUG and settings.ENVIRONMENT != "production",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()
