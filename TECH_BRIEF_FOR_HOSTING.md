# Technical Brief: Heineken QA Compliance App (for hosting recommendations)

Brief for an engineer to evaluate alternative hosting options.

---

## 1. What the app does

- **Internal tool** for Heineken: QA compliance review of influencer content (scripts and videos).
- **Flow:** User uploads a script (PDF/DOCX/TXT) or video (MP4/MOV) → AI (Gemini) analyzes for regulatory risks → User reviews findings, edits recommendations, drafts email → Optionally saves to Google Drive + Google Sheets and creates a Google Doc report.
- **UI:** Single-page Streamlit app, 3 steps (Configuration → Review & Edit → Confirm & Submit). No auth layer in the app itself.

---

## 2. Tech stack

| Layer | Technology |
|-------|------------|
| **Runtime** | Python 3.9+ (tested on 3.9; 3.10+ recommended) |
| **Framework** | Streamlit (single `app.py`, ~1.6k lines) |
| **AI** | Google Gemini API (`google-generativeai`), model `gemini-2.5-flash` |
| **Google APIs** | Drive API (upload files, create folders), Docs API (create report), Sheets API (append rows) via service account |
| **File parsing** | pypdf (PDF), python-docx (DOCX), in-memory for TXT |
| **State** | Streamlit session state only (no DB; no Redis, etc.) |

**Dependencies (requirements.txt):**
```
streamlit
google-generativeai
pandas
gspread
oauth2client
pypdf
python-docx
google-api-python-client
```

---

## 3. Architecture (high level)

```
User browser
    ↓
Streamlit server (app.py)
    ├── Step 1: Form (brand, campaign, influencer, version, phase) + file upload
    ├── Step 2: Call Gemini (script or video) → show risks/recommendations → user edits
    └── Step 3: Optional: save to Drive (files + Google Doc) + append row to Sheets
```

- **No database:** All “state” is in-memory (Streamlit `st.session_state`) for the duration of the session.
- **No background jobs:** Everything is request-driven; long operations (e.g. video processing with Gemini) run in the same request (can be 30s–2+ min for video).
- **File handling:** Uploaded files are in memory (Streamlit `UploadedFile`) until Step 3, where they are written to Drive (and optionally to local disk under `archivos_guardados/`). One temp file is used: `temp_vid.mp4` for video upload before sending to Gemini.

---

## 4. External services and secrets

| Secret / config | Required? | Used for |
|-----------------|-----------|----------|
| **GEMINI_API_KEY** | Yes (for analysis) | Gemini API; without it, analysis fails |
| **credentials.json** (file) | No (optional) | Google Drive + Sheets + Docs via service account. If missing, Drive/Sheets features show errors but app still runs |
| **GOOGLE_DRIVE_FOLDER_ID** | If using Drive | Root folder ID (Drive or Shared Drive) |
| **GOOGLE_SHEET_ID** | If using Sheets | Spreadsheet ID for appending review records |
| **GOOGLE_DRIVE_USER_EMAIL** | Optional | Domain-wide delegation (act as a user for Drive quota) |

- **Streamlit** reads secrets via `st.secrets.get("KEY")` (e.g. in Cloud: Secrets UI; locally: `.streamlit/secrets.toml`).
- **Google** is used via a **service account** JSON (`credentials.json`). The app expects this file on disk; it is not read from env/secrets today. For serverless/Cloud, you’d typically inject the JSON via env (e.g. `GOOGLE_APPLICATION_CREDENTIALS_JSON`) and write to a temp file or use `google.oauth2.service_account.Credentials.from_service_account_info()`.

---

## 5. File system and assets

- **Read at runtime:**
  - `credentials.json` (if present) — service account for Drive/Sheets/Docs.
  - `HNKN logo.png` — optional; if missing, a placeholder is shown.
- **Written at runtime:**
  - `temp_vid.mp4` — temporary video file for Gemini upload; can be ephemeral.
  - `archivos_guardados/` — optional local backup of uploaded files (path built from campaign, influencer, version, filename).
- **No DB files, no SQLite, no persistent volume strictly required** for the app to run; persistence is Drive/Sheets.

---

## 6. Constraints relevant for hosting

1. **Long-running requests:** Video analysis can take 1–2+ minutes (upload to Gemini + processing). Host must allow long HTTP timeouts / execution time (e.g. 120–300 s).
2. **Memory:** Uploaded videos and PDFs held in memory; plus Gemini client. Recommend at least 512 MB–1 GB RAM per instance.
3. **Stateless:** No built-in auth; no sticky sessions. Suitable for single-tenant / internal use behind VPN or IdP if needed.
4. **Google credentials:** For Drive/Sheets, the app expects `credentials.json` on disk. For Cloud, either mount a secret volume or pass JSON via env and load with `from_service_account_info()`.
5. **Streamlit:** Default port 8501. Most platforms use `streamlit run app.py --server.port $PORT` and set `PORT` (e.g. 8080).

---

## 7. Current deployment

- **Streamlit Community Cloud** (free tier): repo `ederrodriguez22/heineken-qa-compliance`, branch `main`, main file `app.py`. Secrets (e.g. `GEMINI_API_KEY`) in Cloud Secrets. No `credentials.json` on Cloud today, so Drive/Sheets are not used there.

---

## 8. What we’re asking for

- **Recommendations for alternative hosting** (e.g. Google Cloud Run, AWS, Render, Railway, Fly.io, self-hosted Docker, etc.) considering:
  - Cost (prefer low or free tier for internal/beta).
  - Ease of deploy (CI/CD from same GitHub repo).
  - Support for long-running requests and ~512 MB–1 GB memory.
  - How to inject `GEMINI_API_KEY` and, if needed, Google service account JSON (e.g. env vars, secret manager).
- If the recommendation involves **no `credentials.json` file** (e.g. serverless), we can adapt the app to read service account JSON from an env var and use `from_service_account_info()` so Drive/Sheets work in that environment.

---

## 9. Repo and entrypoint

- **Repo:** `ederrodriguez22/heineken-qa-compliance` (GitHub).
- **Entrypoint:** `streamlit run app.py --server.port $PORT` (with `PORT` set by the host, e.g. 8080).
- **Root file:** `app.py`. No separate worker or API server; Streamlit is the only process.
