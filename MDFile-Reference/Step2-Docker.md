# Step 2 — Docker Image

Reference for building and running the SaiApp demo as a Docker container locally (before ACR).

---

## Goal

Package the Python app into a Docker image so it can run the same way on your machine and later on AKS.

---

## Files Created

| File | What it is |
|------|------------|
| `Dockerfile` | Instructions to build the app image |
| `.dockerignore` | Files/folders excluded from the image (keeps build small) |

---

## What the Dockerfile Does

1. Starts from `python:3.13-slim` (lightweight Python base image)
2. Copies `uv` into the image (same tool used in Step 1)
3. Copies `pyproject.toml`, `uv.lock`, and `main.py`
4. Runs `uv sync --frozen --no-dev` to install packages
5. Exposes port **8000**
6. Starts the app with **uvicorn** (no reload — for container use)

---

## Commands — Build the Image

From the project folder:

```powershell
cd c:\Users\saina\OneDrive\Desktop\SaiApp
```

Build:

```powershell
docker build -t saiapp-demo .
```

- `-t saiapp-demo` — names the image `saiapp-demo`
- `.` — build using the Dockerfile in the current folder

Check the image was created:

```powershell
docker images
```

Expected:

```text
REPOSITORY     TAG       ...
saiapp-demo    latest    ...
```

---

## Commands — Run the Container Locally

```powershell
docker run -p 8000:8000 saiapp-demo
```

- `-p 8000:8000` — maps your machine port 8000 to the container port 8000

Open in browser:

- http://localhost:8000 — health check
- http://localhost:8000/data — sample data

Stop with `Ctrl + C`.

**Run in background (optional):**

```powershell
docker run -d -p 8000:8000 --name saiapp saiapp-demo
```

Stop and remove:

```powershell
docker stop saiapp
docker rm saiapp
```

---

## Quick Command Reference

| Command | Meaning |
|---------|---------|
| `docker build -t saiapp-demo .` | Build image from Dockerfile |
| `docker images` | List local images |
| `docker run -p 8000:8000 saiapp-demo` | Run container, expose port 8000 |
| `docker ps` | List running containers |
| `docker stop <name>` | Stop a container |

docker ps              # running containers
docker ps -a           # all containers
docker images          # images only
docker stop saiapp     # stop your one container
docker start saiapp    # start same container again
docker rm saiapp       # delete container (image stays)

---

## What's Next (not done yet)

- Step 3: Push image to **Azure Container Registry (ACR)**
- Step 4: Deploy to **Azure Kubernetes Service (AKS)**
