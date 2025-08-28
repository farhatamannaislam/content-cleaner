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
```bash
# build image
docker build -t content-cleaner:latest .

# run container (reads .env)
docker run -p 8000:8000 --env-file .env content-cleaner:latest
```

Open: http://localhost:8000/docs
Swagger → Authorize → enter only your token `(e.g. devtoken123)`.

### Option B — Docker Compose (one command)

```bash
docker compose up --build
# stop later:
# docker compose down
```
#### Health & sample request

```bash
curl -s http://localhost:8000/healthz
curl -s -X POST http://localhost:8000/clean \
  -H "Authorization: Bearer devtoken123" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hi\u200b — world<br><br>"}'
```

#### OpenAPI docs (static export)

```bash
# generate spec
python3 -m scripts.generate_openapi
# serve static docs (ReDoc)
python3 -m http.server 5500 --directory docs
# view:
# http://localhost:5500/redoc.html
```

#### Optional: GUI (Vanilla TS)
```bash
# build the small TS frontend
npx tsc
# then open static/index.html and use your token
```

#### Troubleshooting

- Compose warns `version is obsolete` → remove the `version:` line from `docker-compose.yml.``
- **401 in Swagger** → in **Authorize**, enter **only the token**, Swagger adds Bearer automatically.
- `.env not found` → create `.env` (copy from `.env.example`).
- **ReDoc red screen when opening file directly** → serve via `http.server` as shown above.

---

## Manueller Testplan

### 1) Service starten (Docker Compose)

```bash
docker compose up --build
# App läuft auf http://localhost:8000
```

### 2) Health-Check

```bash
curl -s http://localhost:8000/healthz
# => {"ok": true}
```

### 3) Swagger UI (Login + Anfrage + ohne Auth)

- Öffne http://localhost:8000/docs
- Klicke Authorize (oben rechts) → gib nur deinen Token ein (z. B. devtoken123) → Authorize → Close
- Öffne POST /clean → Try it out → benutze:

```json
{
  "text": "Hello<br><br>World"
}
```
**Execute** → Antwort: `{"clean":"Hello World"}``

- Klicke **Authorize** erneut → *Logout* → **Close**
Teste **POST /clean** nochmal → sollte **401** zurückgeben mit `{"detail":"Missing bearer token"}``

### 4) cURL Happy Path (mit Token)

```bash
curl -s -X POST "http://localhost:8000/clean" \
  -H "Authorization: Bearer devtoken123" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hi\u200b — world<br><br>"}'
# => {"clean":"Hi - world"}
```

### 5) cURL Fehlerfälle (Auth)
_ Ohne Token:

```bash
curl -s -X POST "http://localhost:8000/clean" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello"}'
# => 401 {"detail":"Missing bearer token"}
```

- Falscher Token:

```bash
curl -s -X POST "http://localhost:8000/clean" \
  -H "Authorization: Bearer wrongtoken" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello"}'
# => 401 {"detail":"Invalid token"}
```

### 6) Idempotenz-Test (zweimaliges Reinigen ändert nichts mehr)

```bash
# Erstes Reinigen
C1=$(curl -s -X POST "http://localhost:8000/clean" \
  -H "Authorization: Bearer devtoken123" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello<br><br>World"}' | jq -r .clean)

# Zweites Reinigen mit bereits bereinigtem Ergebnis
C2=$(curl -s -X POST "http://localhost:8000/clean" \
  -H "Authorization: Bearer devtoken123" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"$C1\"}" | jq -r .clean)

echo "C1=$C1"
echo "C2=$C2"
# Erwartung: C1 == C2
```

### 7) GUI (Vanilla TypeScript)

```bash
# Frontend bauen (nach static/dist/)
npx tsc
```
- `static/index.html` im Browser öffnen

- Token (z. B. `devtoken123`) eingeben

- Text mit `<br>` o. Ä. links einfügen → **Bereinigen** klicken

- Erwartung: Bereinigter Text rechts + grüner Status „Bereinigung erfolgreich“

### 8) Statische OpenAPI-Doku (ReDoc)

```bash
# Spezifikation erzeugen
python3 -m scripts.generate_openapi
# Statische Doku bereitstellen
python3 -m http.server 5500 --directory docs
# Im Browser öffnen: http://localhost:5500/redoc.html
```

### 9) Service stoppen

```bash
# Im Compose-Terminal mit Ctrl+C
docker compose down
````

**Hinweis**: In Swagger **Authorize** bitte nur den reinen Token-Wert eingeben (z. B. `devtoken123`). Swagger setzt automatisch `Bearer` davor.





