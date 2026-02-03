# Deploy to Streamlit Community Cloud

Steps to run the Heineken QA Compliance app on **Streamlit Community Cloud** (free hosting).

---

## 1. Prepare the repo (GitHub)

### 1.1 Create a `.gitignore` (already in the project)

Do **not** commit:
- `credentials.json`
- `.streamlit/secrets.toml`

The project already has a `.gitignore` that excludes these.

### 1.2 Create a GitHub repository

1. Go to [github.com](https://github.com) and sign in.
2. Click **New repository** (or **+** → **New repository**).
3. Name it (e.g. `heineken-qa-compliance`).
4. Choose **Public** (or Private if you have a paid Streamlit Cloud plan).
5. Do **not** initialize with README if you already have local files.
6. Click **Create repository**.

### 1.3 Push your code from your machine

In a terminal, from the project folder:

```bash
cd "/Users/mediamonks/Projects/Heineken/IM QA Influencers"

# Initialize Git (if not already)
git init

# Add files (credentials and secrets are ignored)
git add .
git commit -m "Initial commit - Heineken QA Compliance app"

# Add GitHub as remote (replace YOUR_USERNAME and YOUR_REPO with yours)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push (main branch)
git branch -M main
git push -u origin main
```

Use your GitHub username and repo name in the `git remote add` and `git push` commands.

---

## 2. Deploy on Streamlit Community Cloud

### 2.1 Open Streamlit Community Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**.
2. Sign in with **GitHub** (authorize Streamlit if asked).

### 2.2 New app

1. Click **"New app"**.
2. Fill in:
   - **Repository:** `YOUR_USERNAME/YOUR_REPO` (e.g. `mediamonks/heineken-qa-compliance`).
   - **Branch:** `main`.
   - **Main file path:** `app.py`.
   - **App URL:** optional; leave default if you want (e.g. `your-app-name.streamlit.app`).

### 2.3 Secrets (required for AI and optional for Drive/Sheets)

Before or after the first deploy, open your app → **Settings** (⚙️) → **Secrets**.

Paste your secrets in **TOML** format. Example:

```toml
# Required for AI analysis (Gemini)
GEMINI_API_KEY = "your-gemini-api-key-here"

# Optional – Google Drive folder where files are saved
GOOGLE_DRIVE_FOLDER_ID = "your-folder-id"

# Optional – Google Sheet for records
GOOGLE_SHEET_ID = "your-sheet-id"

# Optional – for domain-wide delegation (Drive with a user account)
GOOGLE_DRIVE_USER_EMAIL = "user@yourdomain.com"
```

- **GEMINI_API_KEY** is required for the app to run the analysis.
- The rest are optional; without them, Drive/Sheets features will show errors or be skipped, but the analysis flow will work.

Save. The app will redeploy and use the new secrets.

### 2.4 Deploy

1. Click **"Deploy!"**.
2. Wait a few minutes. When it’s ready, you’ll see **"Your app is live!"** and a link like `https://your-app-name.streamlit.app`.

---

## 3. Using Google Drive/Sheets on Cloud

The app expects a `credentials.json` file for Drive and Sheets. On Streamlit Cloud you don’t upload files; you use **Secrets**.

**Option A – Only Gemini (simplest)**  
- Set only **GEMINI_API_KEY** in Secrets.  
- Use the app for script/video analysis and copy results manually.  
- No Drive/Sheets.

**Option B – Drive/Sheets on Cloud (advanced)**  
- You’d need to add code that reads service account JSON from a secret (e.g. `GOOGLE_CREDENTIALS_JSON`) and uses it instead of `credentials.json`.  
- This is not in the current steps; if you want it, we can add it in a follow-up.

For a first deploy, **Option A** is enough to have the app live and analyzing content.

---

## 4. Summary checklist

- [ ] `.gitignore` in place (no `credentials.json`, no `secrets.toml` in the repo).
- [ ] Repo on GitHub with `app.py`, `requirements.txt`, `HNKN logo.png`, etc.
- [ ] App created on [share.streamlit.io](https://share.streamlit.io) pointing to that repo and `app.py`.
- [ ] **GEMINI_API_KEY** set in **Secrets**.
- [ ] Deploy finished and app URL opened in the browser.

---

## 5. Useful links

- [Streamlit Community Cloud – Get started](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [Secrets management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Gemini API key](https://aistudio.google.com/apikey) (to create `GEMINI_API_KEY`)
