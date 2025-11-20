"""
API Server Launcher
==================

Production-ready launcher for the OMA API.
"""

import sys
import io
import uvicorn
from pathlib import Path

# Fix Windows encoding for emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def main():
    """Launch API server"""
    from api.config import settings

    print(f"\n🚀 Starting {settings.APP_NAME}")
    print(f"📊 Version: {settings.APP_VERSION}")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 URL: http://{settings.API_HOST}:{settings.API_PORT}{settings.API_PREFIX}")
    print(f"📚 Docs: http://{settings.API_HOST}:{settings.API_PORT}{settings.API_PREFIX}/docs")
    print()

    # Run server
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )


if __name__ == "__main__":
    main()
