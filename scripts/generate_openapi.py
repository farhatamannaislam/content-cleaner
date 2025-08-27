# scripts/generate_openapi.py
"""
Generate openapi.json from the FastAPI app without running the server.
Outputs to docs/openapi.json
"""
import json
from pathlib import Path

from fastapi.openapi.utils import get_openapi

# Adjust import if your app is not in main.py
from main import app

def main():
    Path("docs").mkdir(exist_ok=True)
    openapi_schema = get_openapi(
        title=app.title or "content-cleaner",
        version="1.0.0",
        description=app.description or "OpenAPI specification for content-cleaner",
        routes=app.routes,
    )
    out = Path("docs/openapi.json")
    out.write_text(json.dumps(openapi_schema, indent=2), encoding="utf-8")
    print(f"✅ Wrote {out}")

if __name__ == "__main__":
    main()
