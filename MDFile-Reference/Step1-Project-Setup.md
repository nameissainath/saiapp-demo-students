# Step 1 — Project Setup (Python + uv)

Reference for what was created and the commands used to set up the SaiApp demo locally.

---

## Goal

Create a small Python API that fetches sample data, ready for later ACR/AKS deployment.

---

## Files Created

| File / Folder | What it is |
|---------------|------------|
| `main.py` | Simple FastAPI app with 2 endpoints |
| `pyproject.toml` | Project name, Python version, and package list |
| `uv.lock` | Exact package versions (auto-created by uv) |
| `.venv/` | Virtual environment folder (auto-created by uv) |
| `.gitignore` | Keeps `.venv` and cache files out of git |

---

## What `main.py` Does

| Endpoint | Purpose |
|----------|---------|
| `GET /` | Health check — returns `{"status": "ok"}` |
| `GET /data` | Fetches sample JSON from a public API and returns it |

Packages used in the app:

- **fastapi** — web framework (API routes)
- **httpx** — HTTP client (fetch data from URL)
- **uvicorn** — runs the web server on port 8000

---

## Commands Used (Step 1)

Run these from the project folder:

```powershell
cd c:\Users\saina\OneDrive\Desktop\SaiApp
```

### 1. `uv venv`

Creates a virtual environment in the `.venv` folder.

- Isolates project packages from your system Python
- Same idea as `python -m venv .venv`, but uv is faster

### 2. `uv sync`

Reads `pyproject.toml`, installs all dependencies into `.venv`, and creates/updates `uv.lock`.

- Uses **uv**, not pip
- `uv.lock` locks exact versions so installs are repeatable

---

## Run the App Locally

**Option A — recommended (no manual activate):**

```powershell
uv run python main.py
```

**Option B — activate venv first:**

```powershell
.venv\Scripts\activate
python main.py
```

Then open in browser:

- http://localhost:8000 — health check
- http://localhost:8000/data — sample fetched data

Stop the server with `Ctrl + C`.

---

## Quick Command Reference

| Command | Meaning |
|---------|---------|
| `uv venv` | Create virtual environment (`.venv/`) |
| `uv sync` | Install packages from `pyproject.toml` |
| `uv run python main.py` | Run app using the venv (no activate needed) |
| `.venv\Scripts\activate` | Manually activate venv (Windows) |

---

## What's Next (not done yet)

- Step 2: Dockerfile
- Step 3: Push image to Azure Container Registry (ACR)
- Step 4: Deploy to Azure Kubernetes Service (AKS)

#SAI