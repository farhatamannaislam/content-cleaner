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
```

## API
### Authentifizierung


Alle Requests an `/clean` benötigen den Header:

```
Authorization: Bearer <API_TOKEN>
```

### `GET /healthz`


Liveness-Check. Antwort:

```json
{"ok": true}
```

### `POST /clean`

**Request**
```json
{ "text": "<raw-content>" }
```
**Response**
```json
{ "clean": "<bereinigter-Content>" }
```
**Beispiel**

```bash
curl -X POST http://127.0.0.1:8000/clean \
  -H "Authorization: Bearer supersecrettoken" \
  -H "Content-Type: application/json" \
  -d '{"text":"foo--bar – baz — qux <span style=\"color:red\">bad</span><br>ok"}'

# -> {"clean":"foo-bar - baz - qux bad ok"}
```
### Fehlercodes
- `401` Missing/Invalid token  
- `429` Too Many Requests (Rate-Limit 60/min)  
- `400` Cleaning failed

## Optionale GUI

Zusätzlich zur API gibt es eine einfache grafische Oberfläche:  
Datei: `static/index.html`

### Nutzung
1. `uvicorn main:app --reload` starten  
2. `static/index.html` im Browser öffnen (Doppelklick) oder mit Python-HTTP-Server:
   ```bash
   python3 -m http.server 5500
   # http://127.0.0.1:5500/static/index.html
   ```
3. API-Token eintragen (z. B. `supersecrettoken`)
4. Roh-Text ins erste Feld einfügen → **Bereinigen** klicken → Ergebnis erscheint im zweiten Feld


### Hinweis
- In Dev-Umgebungen ggf. CORS im Backend aktivieren, falls Aufruf von anderer Portnummer.
- Die GUI ist optional – alle Funktionen stehen auch per REST-API zur Verfügung.