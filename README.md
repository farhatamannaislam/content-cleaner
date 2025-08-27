# Content-Cleaner

Ein kleiner Service zum Bereinigen von Texten. Fokus: **verlässliche Normalisierung** für Inhalte aus Office/HTML/Copy-Paste.

---

## Features
- Entfernt **unsichtbare Unicode-Zeichen** (Zero-Width, FEFF, NBSP, usw.) und **Steuerzeichen < U+001F**
- Vereinheitlicht **Gedankenstriche** und Strichfolgen  
  (`--`, `–`, `—`, `―――`, `⸻`, Non-Breaking Hyphen `U+2011`, Minus `U+2212`) → `-`
- Entfernt **Word/Inline-HTML-Müll** (z. B. `<span style>`, leere `<p>`), Text bleibt erhalten
- **Doppelte `<br>`** → Leerzeichen
- **Mehrfache Leerzeichen** → ein Space
- **Bearer-Auth** und **Rate-Limit 60 req/min** (429 bei Überschreitung)

---

## Installation & Start

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-dotenv slowapi bleach

# Token setzen
cp .env.example .env    # API_TOKEN eintragen, z. B. supersecrettoken

# Starten
uvicorn main:app --reload
# Health-Check: http://127.0.0.1:8000/healthz

