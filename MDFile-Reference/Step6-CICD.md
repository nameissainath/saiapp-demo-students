# Step 6 — CI/CD with GitHub Actions

Auto deploy to AKS on every **git push to `main`**. This is how teams do it in production — you push code, the pipeline builds and deploys.

---

## Remember this

```text
git push  →  GitHub Actions  →  build image  →  push ACR  →  apply k8s YAML  →  AKS updated
```

| You do | Pipeline does |
|--------|----------------|
| Change code locally | — |
| `git push` | Checkout code |
| — | Login Azure + ACR |
| — | `docker build` + `docker push` |
| — | `kubectl apply -f k8s/` |
| — | Restart pods → app live |

**No manual `docker build` or `kubectl` on your laptop after setup.**

---

## Goal

```text
Step 5 YAML in repo  →  GitHub repo  →  deploy.yml  →  auto deploy on push
```

---

## Prerequisites (Steps 1–5 done)

| Done | What |
|------|------|
| ✅ | App, Docker, ACR, AKS working |
| ✅ | `k8s/deployment.yaml` + `k8s/service.yaml` |
| ✅ | GitHub repo created and code pushed |

**Your repo:** https://github.com/nameissainath/saiapp-demo-students

---

## Part A — GitHub repo (already done)

### Create repo (reference)

| Field | Value |
|-------|-------|
| Name | `saiapp-demo-students` |
| Description | Teaching deployment application — Python, Docker, ACR, AKS demo for students |
| Visibility | Public (or Private) |
| README / .gitignore on GitHub | **Off** — use local files |

---

## Part B — Push code to GitHub

### What to push

```powershell
cd c:\Users\saina\OneDrive\Desktop\SaiApp
git init
git add .
git status
git commit -m "Initial commit: SaiApp demo with k8s YAML deploy"
git branch -M main
git remote add origin https://github.com/nameissainath/saiapp-demo-students.git
git push -u origin main
```

### What NOT to push (`.gitignore` handles this)

| Do NOT push | Why |
|-------------|-----|
| `.venv/` | Local virtual env |
| `__pycache__/` | Python cache |
| `.env` | Secrets |

### DO push

| Push | Why |
|------|-----|
| `main.py`, `Dockerfile`, `k8s/` | App + deploy config |
| `.gitignore`, `.dockerignore` | Git + Docker ignore rules |
| `.github/worflows/deploy.yml` | CI/CD pipeline |
| `MDFile-Reference/` | Step docs for students |

> **`.dockerignore`** is pushed — CI/CD needs it for `docker build`.  
> **`.gitignore`** is pushed — tells git what to skip.

---

## Part C — Workflow file (how prod does it)

### Where it lives

```text
.github/
  workflows/
    deploy.yml    ← GitHub Actions reads this automatically
```

Create **locally**, then push — GitHub does not auto-create it.

### What `deploy.yml` does (each step)

| Step | Action |
|------|--------|
| Trigger | Push to `main` (or manual **Run workflow**) |
| Checkout | Clone your repo on GitHub runner |
| Azure login | Use `AZURE_CREDENTIALS` secret |
| ACR login | `az acr login` |
| Build | `docker build` → `saiapp-demo:latest` |
| Push | Image to `sainathreddycontainer.azurecr.io` |
| AKS connect | `az aks get-credentials` |
| Deploy | `kubectl apply -f k8s/deployment.yaml` + `service.yaml` |
| Restart | `kubectl rollout restart deployment/saiapp` |
| Verify | Wait until rollout succeeds |

---

## Part D — Azure service principal (one-time)

GitHub needs permission to access Azure. Create a **service principal** scoped to your resource group.

### 1. Get subscription ID

```powershell
az account show --query id -o tsv
```

### 2. Create service principal

```powershell
az ad sp create-for-rbac --name "github-saiapp-deploy" `
  --role contributor `
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/sai-app-rg `
  --sdk-auth
```

Copy the **full JSON output** — you need it for GitHub secret `AZURE_CREDENTIALS`.

Example output shape:

```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "...",
  "tenantId": "...",
  ...
}
```

> Store this safely. You won't see `clientSecret` again.

---

## Part E — GitHub secrets

**Repo → Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|-------------|-------|
| `AZURE_CREDENTIALS` | Full JSON from `az ad sp create-for-rbac` |
| `ACR_NAME` | `sainathreddycontainer` |
| `ACR_LOGIN_SERVER` | `sainathreddycontainer.azurecr.io` |
| `AKS_RESOURCE_GROUP` | `sai-app-rg` |
| `AKS_CLUSTER_NAME` | `sai-app-aks` |

Names must match **exactly** — workflow uses `${{ secrets.ACR_NAME }}` etc.

---

## Part F — Push workflow and run pipeline

### Push workflow file

```powershell
cd c:\Users\saina\OneDrive\Desktop\SaiApp
git add .github/
git commit -m "Add CI/CD GitHub Actions workflow"
git push
```

### Watch it run

1. GitHub repo → **Actions** tab
2. Click **Build and Deploy to AKS**
3. Green check = success

### Verify app

```powershell
kubectl get svc
```

Open:

```text
http://<EXTERNAL-IP>/
http://<EXTERNAL-IP>/data
```

---

## Part G — Daily workflow (after setup)

```powershell
# 1. Edit code (e.g. main.py)
# 2. Commit and push
git add .
git commit -m "Update app message"
git push

# 3. GitHub Actions deploys automatically
# 4. Check Actions tab + test URL
```

---

## Manual vs CI/CD

| Task | Before (Steps 1–5) | After (Step 6) |
|------|-------------------|----------------|
| Build image | You run `docker build` | GitHub Actions |
| Push ACR | You run `docker push` | GitHub Actions |
| Deploy AKS | You run `kubectl apply` | GitHub Actions |
| Your job | Many commands | **`git push` only** |

---

## How production differs (same pattern, more rules)

| Demo (you) | Production teams |
|------------|------------------|
| Push to `main` deploys | Often: PR → review → merge → deploy |
| Image tag `:latest` | Tags like `:v1.2.3` or git SHA |
| 1 replica | Multiple replicas + autoscale |
| Secrets in GitHub | Same + Key Vault, managed identity |
| Free AKS tier | Paid tier, staging + prod clusters |

**Same core flow:** code in git → pipeline → ACR → AKS.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Workflow not listed | Push `.github/worflows/deploy.yml` to `main` |
| Azure login failed | Check `AZURE_CREDENTIALS` JSON is complete |
| ACR push denied | Service principal needs **Contributor** on `sai-app-rg` |
| kubectl failed | Check `AKS_*` secret names and values |
| ImagePullBackOff on AKS | ACR attached to AKS or use image pull secret (Step 4) |
| Actions disabled | Repo **Settings → Actions → General** → allow actions |

---

## File structure (full project)

```text
saiapp-demo-students/
  .github/
    workflows/
      deploy.yml          ← Step 6 CI/CD
  k8s/
    deployment.yaml       ← Step 5 deploy
    service.yaml          ← Step 5 expose
  main.py
  Dockerfile
  pyproject.toml
  uv.lock
  .gitignore
  .dockerignore
  MDFile-Reference/
    Step1-Project-Setup.md
    Step2-Docker.md
    Step3-ACR.md
    Step4-AKS.md
    Step5-YAML-Deploy.md
    Step6-CICD.md         ← CI/CD overview
    Step7-CICD-Setup.md  ← service principal + secrets + first run
    Step8-GitHub-Secrets-Push.md  ← secrets copy-paste + push
```

---

## Full setup checklist

| # | Task | Done? |
|---|------|-------|
| 1 | GitHub repo `saiapp-demo-students` | ☐ |
| 2 | Initial code pushed | ☐ |
| 3 | Azure service principal created | ☐ |
| 4 | 5 GitHub secrets added | ☐ |
| 5 | `.github/worflows/deploy.yml` pushed | ☐ |
| 6 | Actions run green | ☐ |
| 7 | App URL works | ☐ |

---

## Command reference

| Command | When |
|---------|------|
| `git add . && git commit && git push` | Every code change |
| `az ad sp create-for-rbac ...` | One-time setup |
| Check **Actions** tab | After every push |

---

## What's next

- **Step 7:** Hands-on setup — service principal, GitHub secrets, first deploy — see **`Step7-CICD-Setup.md`**
- **Step 8:** Secrets copy-paste + push checklist — see **`Step8-GitHub-Secrets-Push.md`**
- Delete `sai-app-rg` when demo finished to save Azure credits
