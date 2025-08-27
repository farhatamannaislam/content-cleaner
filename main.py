from fastapi import FastAPI

app = FastAPI()

@app.get("/healthz")
def health():
    return {"ok": True}

# -------- Step 2: Cleaning functions (part 1) --------

# List of invisible/special Unicode chars to remove
INVISIBLE = [
    "\u2014","\u2003","\u2013","\u2018","\u2019","\u201C","\u201D",
    "\u200B","\u2002","\u00A0","\u202F","\u2060","\u200C","\u200D",
    "\u200E","\u200F","\uFEFF","\u2061","\u2062","\u2063","\u2064",
    "\u180E","\u2001","\u2008","\u2009","\u200A","\u3164","\u2E3B",
    "\u00AD","\u202E","\u2800","\u2011","\u2212","\u02BC"
]

def remove_control_chars(s: str) -> str:
    """Remove control characters (< U+001F)."""
    return "".join(ch for ch in s if ord(ch) >= 32)

def remove_invisible(s: str) -> str:
    """Remove invisible Unicode chars from list."""
    for ch in INVISIBLE:
        s = s.replace(ch, "")
    return s

import re

# -------- Step 2: Cleaning functions (part 2) --------

DASH_PATTERN = re.compile(r"(?:--+|[–—―⸻]+)")   # all dash variants
MULTISPACE = re.compile(r"\s+")

def normalize_dashes(s: str) -> str:
    """Normalize different dash types into a single -."""
    return DASH_PATTERN.sub("-", s)

def collapse_spaces(s: str) -> str:
    """Replace multiple spaces with a single space."""
    return MULTISPACE.sub(" ", s).strip()
