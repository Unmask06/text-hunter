"""Allow running texthunter as a module: python -m texthunter"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "texthunter.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
