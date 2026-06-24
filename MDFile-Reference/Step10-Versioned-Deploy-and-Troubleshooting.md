# Step 10 — Versioned ACR Tags, Rollback & Troubleshooting

Everything we learned **after Step 9** — versioned images, prod-style deploy, common bugs, and backup-file gotchas.

---

## What changed in Step 10

| Area | Before (Step 9) | After (Step 10) |
|------|-----------------|-----------------|
| ACR tag | Only `:latest` (overwritten each push) | **Git commit SHA** (e.g. `:69c425c`) + optional `:latest` |
| `deploy.yml` | build/push `:latest` + `rollout restart` | build/push SHA tag + `sed` patch + `kubectl apply` |
| `deployment.yaml` | `imagePullPolicy: Always` | `IfNotPresent` (unique tags = new images) |
| `main.py` | v0.1.0 | v0.2.0 + **`GET /version`** endpoint |
| Rollback | Hard (old `:latest` gone) | Easy — redeploy any old SHA still in ACR |

---

## Why version tags? (not only `:latest`)

With **only `:latest`**:

```text
Push 1 → saiapp-demo:latest  (digest A)
Push 2 → saiapp-demo:latest  (digest B — overwrites tag)
Push 3 → saiapp-demo:latest  (digest C — overwrites tag)
```

- Tag **name** never changes → need `kubectl rollout restart` to force pull
- Hard to know **which build** is running
- **Rollback** is messy

With **git SHA tags**:

```text
Push 1 → saiapp-demo:abe4a37
Push 2 → saiapp-demo:11ac0e7
Push 3 → saiapp-demo:69c425c
         saiapp-demo:latest   ← optional pointer to newest
```

- Each push = **new tag** in ACR (kept until you delete)
- Kubernetes sees tag change → **rolling update** automatically
- **Rollback** = deploy old tag again (no rebuild)

---

## How versioning works in our pipeline

### 1. `deploy.yml` — set tag from git commit

```yaml
- name: Set image tag from git commit
  run: echo "IMAGE_TAG=${GITHUB_SHA::7}" >> $GITHUB_ENV
```

Uses first **7 characters** of commit SHA (e.g. `69c425c`).

### 2. Build & push two tags

```yaml
docker build -t .../saiapp-demo:${{ env.IMAGE_TAG }} .
docker tag  .../saiapp-demo:${{ env.IMAGE_TAG }} .../saiapp-demo:latest
docker push .../saiapp-demo:${{ env.IMAGE_TAG }}
docker push .../saiapp-demo:latest
```

Old `:latest`-only lines are **commented** in the file — compare OLD vs NEW.

### 3. Patch `deployment.yaml` before apply

```yaml
sed -i "s|saiapp-demo:.*|saiapp-demo:${{ env.IMAGE_TAG }}|" k8s/deployment.yaml
kubectl apply -f k8s/deployment.yaml
```

CI runner patches the file **only for that run** — your git repo still shows `:latest` as the default for local manual deploy.

### 4. No more `rollout restart` (commented out)

With unique tags, Kubernetes detects the image change and rolls out new pods.  
`rollout restart` was needed with `:latest` because the **tag name** did not change.

---

## `k8s/deployment.yaml` changes

```yaml
# OLD (commented in file):
# image: .../saiapp-demo:latest
# imagePullPolicy: Always

# NEW (active):
image: sainathreddycontainer.azurecr.io/saiapp-demo:latest
imagePullPolicy: IfNotPresent
```

- Repo keeps `:latest` for **local** `kubectl apply -f k8s/`
- **CI/CD** replaces tag with SHA via `sed` before apply

---

## `main.py` changes (v0.2.0)

| Endpoint | What it returns |
|----------|-----------------|
| `GET /` | Health + `"version": "0.2.0"` |
| `GET /version` | App version — **use after deploy** to confirm new image is live |
| `GET /games` | 4 games (added **Version Vault**) |
| `GET /data` | JSONPlaceholder post (URL fixed: `jsonplaceholder.typicode.com`) |
| `GET /users` | JSONPlaceholder user |

Test after green Actions run:

```text
http://<EXTERNAL-IP>/version
http://<EXTERNAL-IP>/games
```

If `/version` shows `0.2.0` and `/games` has 4 items → new image is live.

---

## Verify versions in ACR

```powershell
az acr repository show-tags --name sainathreddycontainer --repository saiapp-demo --output table
```

You should see multiple tags:

```text
TAG        ...
69c425c
abe4a37
latest
```

| Question | Answer |
|----------|--------|
| New tag every push? | ✅ Yes — git SHA |
| `:latest` still updated? | ✅ Yes — points to newest build |
| Old versions kept? | ✅ Yes — until you delete in ACR |

---

## Rollback to a previous version

If deploy `69c425c` is bad, roll back to `abe4a37`:

```powershell
az aks get-credentials --resource-group sai-app-rg --name sai-app-aks --overwrite-existing

kubectl set image deployment/saiapp \
  saiapp=sainathreddycontainer.azurecr.io/saiapp-demo:abe4a37

kubectl rollout status deployment/saiapp
```

No rebuild needed — old image is still in ACR.

Check which image a pod runs:

```powershell
kubectl get pods
kubectl describe pod <pod-name> | findstr Image
```

---

## Issue 1 — Site timeout (`1/2` CrashLoopBackOff)

**Not caused by:** low CPU, 1 node, or JSON URL typo.

**Caused by:** mixing Step 4 manual deploy + Step 5 YAML apply → **two containers** in one pod.

| Container | Source | Status |
|-----------|--------|--------|
| `saiapp-demo` | `kubectl create deployment` (Step 4) | CrashLoopBackOff |
| `saiapp` | `kubectl apply -f k8s/` (Step 5) | Running |

Pod shows **`1/2`** → not Ready → Load Balancer has no healthy backend → **timeout**.

### One-time fix (not for daily CI/CD)

```powershell
kubectl delete deployment saiapp
kubectl apply -f k8s/
kubectl get pods   # expect 1/1 Running
```

**Normal prod / daily deploy:** only `kubectl apply` + version tag change — **never** delete deployment in pipeline.

Service EXTERNAL-IP stays the same.

---

## Issue 2 — JSON URL typo (`/data`, `/users` only)

Wrong: `https://json.typicode.com/...`  
Correct: `https://jsonplaceholder.typicode.com/...`

| Symptom | Scope |
|---------|-------|
| Whole site timeout | Dual-container pod (Issue 1) |
| `/data` or `/users` → 500 | URL typo only |
| `/`, `/games`, `/version` OK | App container is fine |

---

## Issue 3 — Duplicate workflow runs (2 Actions on 1 push)

### What happened

Two files in `.github/workflows/`:

```text
.github/workflows/deploy.yml        ← Workflow 1 (e.g. run #5)
.github/workflows/deploy copy.yml   ← Workflow 2 (e.g. run #1)
```

Both had:

```yaml
on:
  push:
    branches:
      - main
```

**One `git push` → two pipeline runs** (same commit, two builds, two ACR pushes).

GitHub treats **every `.yml` / `.yaml` file** under `.github/workflows/` as a separate workflow. Filename does not matter — even `deploy copy.yml` counts.

### Fix

```powershell
# Remove duplicate from repo (keep local backup outside .github/workflows/)
git rm ".github/workflows/deploy copy.yml"
git commit -m "Remove duplicate workflow file"
git push
```

After fix: **one push = one Actions run**.

### Safe vs unsafe backup locations

| File location | Triggers GitHub Actions? | Triggers Kubernetes? |
|---------------|--------------------------|----------------------|
| `.github/workflows/deploy copy.yml` | ✅ **YES — avoid!** | ❌ No |
| `k8s/deployment copy.yaml` | ❌ No | ❌ **No** — kubectl only reads files **you apply** |
| `backups/deploy.yml` (outside `.github`) | ❌ No | ❌ No |

**You are correct:** `k8s/deployment copy.yaml` is **NOT** used automatically. Kubernetes only applies files you explicitly run:

```powershell
kubectl apply -f k8s/deployment.yaml   # uses deployment.yaml only
kubectl apply -f k8s/                    # applies all yaml in folder EXCEPT if copy has wrong extension
```

⚠️ If `deployment copy.yaml` is inside `k8s/` and you run `kubectl apply -f k8s/`, Kubernetes **will** try to apply it too (creates a second deployment if metadata name differs). Safer to keep copies **outside** `k8s/` or rename to `.bak` / `.txt`.

| Backup in `k8s/` | `kubectl apply -f k8s/deployment.yaml` | `kubectl apply -f k8s/` |
|------------------|----------------------------------------|-------------------------|
| `deployment copy.yaml` | ❌ Not applied | ⚠️ **May be applied** |

---

## `:latest` vs versioned — when to use what

| Approach | Good for | Daily prod? |
|----------|----------|-------------|
| `:latest` only + rollout restart | Simple demos, learning | Rarely |
| Git SHA tag | CI/CD, traceability, rollback | ✅ **Recommended** |
| Semantic tags (`v1.0.0`) | Releases, git tags | ✅ Production releases |

Our demo uses **git SHA** — good balance for students.

---

## Updated pipeline (Step 10)

```text
git push
  │
  ▼
GitHub Actions (deploy.yml ONLY — one file!)
  │
  ├─ IMAGE_TAG = first 7 chars of commit SHA
  ├─ docker build → saiapp-demo:<SHA>
  ├─ docker tag  → saiapp-demo:latest
  ├─ docker push → both tags to ACR
  ├─ sed patch deployment.yaml with <SHA>
  ├─ kubectl apply -f k8s/
  └─ kubectl rollout status (wait for ready)
  │
  ▼
AKS pod runs saiapp-demo:<SHA> → http://<EXTERNAL-IP>/version
```

---

## Checklist — Step 10

| # | Item | Done? |
|---|------|-------|
| 1 | `deploy.yml` uses SHA tags (OLD lines commented) | ☐ |
| 2 | `deployment.yaml` updated (`IfNotPresent`, OLD commented) | ☐ |
| 3 | `main.py` v0.2.0 + `/version` | ☐ |
| 4 | Only **one** file in `.github/workflows/` | ☐ |
| 5 | ACR shows multiple tags (SHA + latest) | ☐ |
| 6 | `/version` returns `0.2.0` after deploy | ☐ |
| 7 | Understand rollback with `kubectl set image` | ☐ |
| 8 | Know dual-container vs duplicate workflow vs JSON typo | ☐ |

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
| **`Step10-Versioned-Deploy-and-Troubleshooting.md`** | **Version tags, rollback, all bugs we hit** |
