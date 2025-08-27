from fastapi import FastAPI
import re
import html
import bleach

app = FastAPI()

@app.get("/healthz")
def health():
    return {"ok": True}

# -------- Cleaning functions --------

ALLOWED_TAGS = ["p", "a"]          # no <br>
ALLOWED_ATTRS = {"a": ["href"]}

def strip_html(raw: str) -> str:
    # 1) Unescape HTML entities (&nbsp; -> \u00A0, etc.)
    raw = html.unescape(raw)
    # 2) Normalize NBSP to a normal space so it doesn't glue words
    raw = raw.replace("\u00A0", " ")
    # 3) Convert <br> to a space *before* stripping
    raw = re.sub(r"(?i)<br\s*/?>", " ", raw)

    cleaned = bleach.clean(
        raw,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        strip=True
    )
    # remove empty <p>
    cleaned = re.sub(r"(?i)<p>\s*</p>", "", cleaned)
    return cleaned


# List of invisible/special Unicode chars to remove
INVISIBLE = [
    # "\u2014",  # — EM DASH  (handled by normalize_dashes)
    "\u2003",
    # "\u2013",  # – EN DASH  (handled by normalize_dashes)
    "\u2018","\u2019","\u201C","\u201D",
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



DASH_PATTERN = re.compile(r"(?:--+|[\u2013\u2014\u2015\u2E3B\u2011\u2212]+)")

MULTISPACE = re.compile(r"\s+")

def normalize_dashes(s: str) -> str:
    """Normalize different dash types into a single -."""
    return DASH_PATTERN.sub("-", s)

def collapse_spaces(s: str) -> str:
    """Replace multiple spaces with a single space."""
    return MULTISPACE.sub(" ", s).strip()

import re
import bleach  # make sure bleach is installed in your venv



def clean_pipeline(raw: str) -> str:
    """
    Full pipeline:
      1) remove control chars (< U+001F)
      2) remove invisible Unicode list
      3) normalize dashes to '-'
      4) strip HTML (allow minimal whitelist)
      5) collapse whitespace to single spaces
    """
    text = remove_control_chars(raw)
    text = remove_invisible(text)
    text = normalize_dashes(text)
    text = strip_html(text)
    text = collapse_spaces(text)
    return text
