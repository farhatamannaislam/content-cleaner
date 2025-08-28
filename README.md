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

---

## Typische Fragen & Antworten (FAQ)

**Unicode-Handling**  
*Sollen auch Control-Chars < U+001F entfernt werden?*  
Ja – sämtliche Steuerzeichen unterhalb von U+001F werden konsequent verworfen, um saubere, ausschließlich druckbare Ausgaben sicherzustellen.  

**HTML-Stripping**  
*Was tun mit erlaubten Tags wie `<p>` oder `<a>` – whitelisten oder alles strippen?*  
Es wird ein striktes Whitelisting angewandt: nur `<p>` und `<a href>` bleiben erhalten. Alles andere (z. B. `<div>`, leere `<p>`, `<span style>`) wird entfernt.  

**Kopiertests mit Word-HTML**  
*Wie verhält sich der Cleaner mit „Müll“-Markup aus Microsoft Word?*  
Divs, Inline-Styles und andere Word-spezifische Tags werden entfernt, sodass nur sauberer Text und die definierte Whitelist übrigbleiben.  

**Gedankenstriche**  
*Durch einfachen Bindestrich ersetzen oder komplett löschen?*  
Alle Varianten von Gedankenstrichen (–, —, ―, ⸻, usw.) werden einheitlich auf den normalen Bindestrich `-` reduziert.

---

## Code-Qualität & Validierung

Zur Sicherstellung einer sauberen Codebasis wurden Linter und Validatoren verwendet:

### Python Linter
- Überprüfung mit dem **CI Python Linter** (PEP8-Konformität)  
- Ergebnis: ✅ Keine Fehler mehr (z. B. E231/E304 behoben)

### HTML-Validierung
- `static/index.html` wurde mit dem [W3C HTML Validator](https://validator.w3.org/) überprüft  
- Ergebnis: ✅ Keine Fehler oder Warnungen

---

Damit ist sowohl der Python-Backend-Code als auch das optionale HTML-Frontend **validiert und standardkonform**.


---

## Docker & Compose

### Prereqs

- Docker Desktop (Mac/Win) or Docker Engine (Linux)
- A `.env` file at repo root `(see .env.example)``

```
API_TOKEN=devtoken123
```

### Option A — Docker (single container)
```
# build image
docker build -t content-cleaner:latest .

# run container (reads .env)
docker run -p 8000:8000 --env-file .env content-cleaner:latest
```

Open: http://localhost:8000/docs
Swagger → Authorize → enter only your token `(e.g. devtoken123)`.

### Option B — Docker Compose (one command)

```
docker compose up --build
# stop later:
# docker compose down
```
#### Health & sample request

```
curl -s http://localhost:8000/healthz
curl -s -X POST http://localhost:8000/clean \
  -H "Authorization: Bearer devtoken123" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hi\u200b — world<br><br>"}'
```

#### OpenAPI docs (static export)

```
# generate spec
python3 -m scripts.generate_openapi
# serve static docs (ReDoc)
python3 -m http.server 5500 --directory docs
# view:
# http://localhost:5500/redoc.html
```

#### Optional: GUI (Vanilla TS)
```
# build the small TS frontend
npx tsc
# then open static/index.html and use your token
```

#### Troubleshooting

- Compose warns `version is obsolete` → remove the `version:` line from `docker-compose.yml.``
- **401 in Swagger** → in **Authorize**, enter **only the token**, Swagger adds Bearer automatically.
- `.env not found` → create `.env` (copy from `.env.example`).
- **ReDoc red screen when opening file directly** → serve via `http.server` as shown above.









