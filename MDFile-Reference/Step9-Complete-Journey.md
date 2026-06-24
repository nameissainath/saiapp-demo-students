# Step 9 — Complete Journey & Daily Workflow

Everything built so far — end-to-end recap and **how to work from here**.

---

## Remember this (big picture)

```text
Code (main.py)  →  git push  →  GitHub Actions  →  ACR  →  AKS  →  public URL
```

**You only `git push` now.** Pipeline builds, pushes ACR, and updates AKS.

---

## What we completed (Steps 1–9)

| Step | Doc | What we did |
|------|-----|-------------|
| 1 | `Step1-Project-Setup.md` | Python app + `uv venv` + `uv sync` |
| 2 | `Step2-Docker.md` | `Dockerfile` + local `docker build` / `docker run` |
| 3 | `Step3-ACR.md` | Resource group + ACR + push image to Azure |
| 4 | `Step4-AKS.md` | AKS cluster + manual deploy + Load Balancer + public IP |
| 5 | `Step5-YAML-Deploy.md` | `k8s/deployment.yaml` + `service.yaml` |
| 6 | `Step6-CICD.md` | CI/CD concept + `.github/worflows/deploy.yml` |
| 7 | `Step7-CICD-Setup.md` | Service principal `github-saiapp-deploy` |
| 8 | `Step8-GitHub-Secrets-Push.md` | 5 GitHub secrets + push + first pipeline |
| 9 | **This file** | CI/CD working + daily workflow recap |
| 10 | `Step10-Versioned-Deploy-and-Troubleshooting.md` | Versioned ACR tags, rollback, troubleshooting |

---

## Azure resources (your project)

| Resource | Name |
|----------|------|
| Resource group | `sai-app-rg` |
| Container registry | `sainathreddycontainer` |
| ACR login server | `sainathreddycontainer.azurecr.io` |
| Image | `saiapp-demo:latest` |
| AKS cluster | `sai-app-aks` |
| Deployment | `saiapp` |
| Service | `saiapp` (LoadBalancer) |

---

## GitHub

| Item | Value |
|------|-------|
| Repo | `nameissainath/saiapp-demo-students` |
| URL | https://github.com/nameissainath/saiapp-demo-students |
| Branch | `main` |
| Workflow | `.github/worflows/deploy.yml` — **Build and Deploy to AKS** |
| Status | ✅ Run #2 succeeded (after fixing `AZURE_CREDENTIALS`) |

---

## API endpoints (current `main.py`)

| URL | Description |
|-----|-------------|
| `GET /` | Health check |
| `GET /data` | Sample post from JSONPlaceholder |
| `GET /games` | Sample games list (mock — for demo) |
| `GET /users` | Sample user from JSONPlaceholder |

Test after deploy:

```text
http://<EXTERNAL-IP>/
http://<EXTERNAL-IP>/data
http://<EXTERNAL-IP>/games
http://<EXTERNAL-IP>/users
```

Get IP:

```powershell
kubectl get svc
```

---

## CI/CD — what runs on every `git push`

```text
1. Checkout code from GitHub
2. Azure login (AZURE_CREDENTIALS)
3. az acr login
4. docker build → saiapp-demo:latest
5. docker push → sainathreddycontainer.azurecr.io
6. az aks get-credentials
7. kubectl apply -f k8s/deployment.yaml
8. kubectl apply -f k8s/service.yaml
9. kubectl rollout restart deployment/saiapp
10. Verify rollout success
```

Watch: GitHub → **Actions** tab → green checkmark (~1–3 min).

---

## Update app now (daily workflow)

### You do

```powershell
# 1. Edit code (e.g. main.py)
# 2. Commit and push
git add .
git commit -m "Describe your change"
git push
```

### You do NOT need anymore

```text
docker build
docker push
kubectl create deployment
kubectl expose
az acr login (for deploy)
```

Pipeline and AKS are updated **automatically** by GitHub Actions.

---

## ACR — new build vs new tag

When you push code, pipeline pushes again to:

```text
sainathreddycontainer.azurecr.io/saiapp-demo:latest
```

| Question | Answer |
|----------|--------|
| New image built? | ✅ Yes, every push |
| New ACR repository? | ❌ No — still `saiapp-demo` |
| New tag name (v2, v3)? | ❌ No — still **`latest`** |
| What happens to `latest`? | **Overridden** — points to new digest |
| Manifest count in portal | Goes up (4, 5, 6…) — old builds kept as manifests |
| Tag count | Stays **1** (`latest` only) |

**Demo uses `:latest`.** Production often adds tags like `:v1.0.0` or git SHA.

---

## Manual vs automated (summary)

| Task | Before CI/CD | Now |
|------|--------------|-----|
| Build image | Your laptop | GitHub Actions |
| Push ACR | Your laptop | GitHub Actions |
| Deploy AKS | `kubectl` manual | GitHub Actions |
| Your step | Many commands | **`git push`** |

---

## GitHub secrets (reference — do not commit)

| Secret | Purpose |
|--------|---------|
| `AZURE_CREDENTIALS` | Service principal JSON |
| `ACR_NAME` | `sainathreddycontainer` |
| `ACR_LOGIN_SERVER` | `sainathreddycontainer.azurecr.io` |
| `AKS_RESOURCE_GROUP` | `sai-app-rg` |
| `AKS_CLUSTER_NAME` | `sai-app-aks` |

ACR **admin password** is **not** in GitHub — only for local `docker login` if needed.

---

## Useful commands (still handy)

```powershell
# Connect to AKS
az aks get-credentials --resource-group sai-app-rg --name sai-app-aks --overwrite-existing

# Check app
kubectl get pods
kubectl get svc
kubectl logs <pod-name>

# List images in ACR
az acr repository list --name sainathreddycontainer --output table
az acr repository show-tags --name sainathreddycontainer --repository saiapp-demo --output table

# Re-run pipeline without code change
# GitHub → Actions → Run workflow (or Re-run all jobs)
```

---

## Project file structure

```text
saiapp-demo-students/
  main.py
  Dockerfile
  pyproject.toml
  uv.lock
  k8s/
    deployment.yaml
    service.yaml
  .github/
    workflows/
      deploy.yml
  MDFile-Reference/
    Step1 … Step9
```

---

## Troubleshooting CI/CD

| Problem | Fix |
|---------|-----|
| First run failed, second succeeded | Fix `AZURE_CREDENTIALS` JSON — re-run |
| `nothing to commit` | Already pushed — use Actions **Run workflow** |
| New API not showing | Wait for green Actions → hard refresh browser |
| 404 on new route | Pipeline not finished or old pods — check Actions + `kubectl get pods` |
| **Pod `1/2` CrashLoopBackOff** | Two containers from manual `create` + YAML apply — see below |
| **Site timeout, Actions green** | Pod not healthy — `kubectl get pods` must show **`1/1 Running`** |

### Fix duplicate containers (one-time)

If you used **`kubectl create deployment`** then **`kubectl apply`**, the pod may have **2 containers** (`saiapp` + `saiapp-demo`). One crashes → site down.

**Normal deploy:** only `kubectl apply -f k8s/`  
**One-time fix:**

```powershell
kubectl delete deployment saiapp
kubectl apply -f k8s/
kubectl get pods
```

Wait for **`1/1 Running`**. Service / Load Balancer IP stays the same.

---

## When demo is finished (save credits)

```powershell
az group delete --name sai-app-rg --yes --no-wait
```

Optional: rotate/delete GitHub secrets and service principal if credentials were exposed.

---

## Full pipeline diagram

```text
┌─────────────┐
│  main.py    │  Local dev / uv run
└──────┬──────┘
       │ git push
       ▼
┌─────────────┐
│   GitHub    │  saiapp-demo-students
└──────┬──────┘
       │ Actions (deploy.yml)
       ▼
┌─────────────┐
│    ACR     │  sainathreddycontainer.azurecr.io/saiapp-demo:latest
└──────┬──────┘
       │ kubectl apply + rollout
       ▼
┌─────────────┐
│    AKS     │  Pod → LoadBalancer → http://<EXTERNAL-IP>
└─────────────┘
```

---

## Checklist — everything done?

| # | Item | Done? |
|---|------|-------|
| 1 | Local app + Docker | ☐ |
| 2 | ACR + image pushed | ☐ |
| 3 | AKS + public URL | ☐ |
| 4 | k8s YAML | ☐ |
| 5 | GitHub repo | ☐ |
| 6 | CI/CD secrets + workflow | ☐ |
| 7 | Actions run green | ☐ |
| 8 | `/`, `/data`, `/games`, `/users` work | ☐ |
| 9 | Understand: push code only, pipeline deploys | ☐ |

---

## What's next

- **Step 10:** Versioned ACR tags, rollback, duplicate workflow fix, all troubleshooting — see **`Step10-Versioned-Deploy-and-Troubleshooting.md`**

---

## Step docs index

| File | Topic |
|------|-------|
| `Step1-Project-Setup.md` | Python + uv |
| `Step2-Docker.md` | Docker image |
| `Step3-ACR.md` | Azure Container Registry |
| `Step4-AKS.md` | AKS + manual deploy |
| `Step5-YAML-Deploy.md` | Kubernetes YAML |
| `Step6-CICD.md` | CI/CD overview |
| `Step7-CICD-Setup.md` | Service principal |
| `Step8-GitHub-Secrets-Push.md` | Secrets + push |
| `Step9-Complete-Journey.md` | Full recap + daily workflow |
| `Step10-Versioned-Deploy-and-Troubleshooting.md` | Version tags, rollback, troubleshooting |
