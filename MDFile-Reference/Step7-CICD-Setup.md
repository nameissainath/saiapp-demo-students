# Step 7 — CI/CD Setup & First Auto-Deploy

Hands-on steps after **Step 6** — Azure service principal, GitHub secrets, push workflow, run pipeline.

> **Concept overview:** see **`Step6-CICD.md`**  
> **This file:** do these steps in order.

---

## Remember this

```text
Service principal (Azure login for GitHub)
        ↓
GitHub secrets (5 names)
        ↓
Push deploy.yml
        ↓
git push → Actions runs → AKS updated
```

---

## Your project values

| Item | Value |
|------|-------|
| GitHub repo | `nameissainath/saiapp-demo-students` |
| Subscription ID | `2853d84e-1dda-4f6d-9ebd-3c6a3e1f9ede` |
| Resource group | `sai-app-rg` |
| ACR | `sainathreddycontainer` |
| ACR login server | `sainathreddycontainer.azurecr.io` |
| AKS cluster | `sai-app-aks` |
| Service principal name | `github-saiapp-deploy` |

---

## Step 7.1 — Get subscription ID

**What:** Find your Azure subscription ID (needed for service principal scope).

**CLI:**

```powershell
az login
az account show --query id -o tsv
```

**Expected:**

```text
2853d84e-1dda-4f6d-9ebd-3c6a3e1f9ede
```

**Portal:** Subscriptions → your subscription → copy **Subscription ID**.

| Done? |
|-------|
| ☐ |

---

## Step 7.2 — Create service principal (GitHub → Azure login)

**What:** Creates a robot account so GitHub Actions can deploy to **`sai-app-rg`** only (not whole subscription).

**CLI (recommended):**

```powershell
az ad sp create-for-rbac --name "github-saiapp-deploy" `
  --role contributor `
  --scopes /subscriptions/2853d84e-1dda-4f6d-9ebd-3c6a3e1f9ede/resourceGroups/sai-app-rg `
  --sdk-auth
```

| Flag | Meaning |
|------|---------|
| `--name` | App name in Azure |
| `--role contributor` | Manage resources in scope |
| `--scopes .../sai-app-rg` | Limited to your resource group |
| `--sdk-auth` | Prints JSON for GitHub |

**Expected output:** JSON with `clientId`, `clientSecret`, `subscriptionId`, `tenantId`, etc.

**Important:**

- Copy **entire JSON** — paste into GitHub secret `AZURE_CREDENTIALS`
- **Never** commit JSON to git or paste in chat
- You won't see `clientSecret` again — save it in GitHub immediately

**Portal alternative:** Microsoft Entra ID → App registrations → create app → secret → IAM Contributor on `sai-app-rg` → build JSON manually (harder). CLI is standard for CI/CD.

| Done? |
|-------|
| ☐ |

---

## Step 7.3 — Add GitHub secrets

**Where:**  
https://github.com/nameissainath/saiapp-demo-students/settings/secrets/actions

**Settings → Secrets and variables → Actions → New repository secret**

Add all **5** secrets (names must match exactly):

| Secret name | Value to paste |
|-------------|----------------|
| `AZURE_CREDENTIALS` | Full JSON from Step 7.2 |
| `ACR_NAME` | `sainathreddycontainer` |
| `ACR_LOGIN_SERVER` | `sainathreddycontainer.azurecr.io` |
| `AKS_RESOURCE_GROUP` | `sai-app-rg` |
| `AKS_CLUSTER_NAME` | `sai-app-aks` |

**What each secret does:**

| Secret | Used for |
|--------|----------|
| `AZURE_CREDENTIALS` | `azure/login` in workflow |
| `ACR_NAME` | `az acr login` |
| `ACR_LOGIN_SERVER` | `docker build` / `docker push` image path |
| `AKS_RESOURCE_GROUP` | `az aks get-credentials` |
| `AKS_CLUSTER_NAME` | `az aks get-credentials` |

| Done? |
|-------|
| ☐ |

---

## Step 7.4 — Push workflow file to GitHub

**What:** GitHub only runs CI/CD after `.github/worflows/deploy.yml` is in the repo.

**Local file:**

```text
.github/worflows/deploy.yml
```

**Commands:**

```powershell
cd c:\Users\saina\OneDrive\Desktop\SaiApp
git add .github/ MDFile-Reference/
git status
git commit -m "Add CI/CD workflow and Step6/Step7 docs"
git push
```

**Check `git status` shows:**

- `.github/worflows/deploy.yml`
- Not `.venv/` or secrets

| Done? |
|-------|
| ☐ |

---

## Step 7.5 — Run pipeline (first time)

**What happens:** Push to `main` triggers **Build and Deploy to AKS**.

1. GitHub repo → **Actions** tab
2. Click latest **Build and Deploy to AKS** run
3. Wait for green checkmark (5–10 min first time)

**Pipeline build steps in workflow:**

```text
Checkout → Azure login → ACR login → docker build → docker push
→ kubectl apply k8s/ → rollout restart → verify
```

**Manual run (optional):** Actions → workflow → **Run workflow**

| Done? |
|-------|
| ☐ |

---

## Step 7.6 — Verify app still works

```powershell
kubectl get pods
kubectl get svc
```

Browser:

```text
http://<EXTERNAL-IP>/
http://<EXTERNAL-IP>/data
```

| Done? |
|-------|
| ☐ |

---

## Step 7.7 — Daily use (after setup)

**Only this when you change code:**

```powershell
git add .
git commit -m "Describe your change"
git push
```

Then check **Actions** tab → green → test URL.

**You no longer run manually:**

```text
docker build
docker push
kubectl apply
```

GitHub Actions does it.

---

## Full checklist (Step 7)

| # | Task | Done? |
|---|------|-------|
| 1 | Subscription ID copied | ☐ |
| 2 | Service principal created (`github-saiapp-deploy`) | ☐ |
| 3 | JSON saved to `AZURE_CREDENTIALS` secret | ☐ |
| 4 | All 5 GitHub secrets added | ☐ |
| 5 | `deploy.yml` pushed to GitHub | ☐ |
| 6 | Actions run succeeded (green) | ☐ |
| 7 | App URL works | ☐ |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `Could not create role assignment` locally | Normal on student account — GitHub uses service principal instead |
| Azure login failed in Actions | Re-paste full JSON to `AZURE_CREDENTIALS` |
| Secret name typo | Must be exact: `ACR_NAME` not `ACR-NAME` |
| Workflow not visible | Enable Actions in repo Settings |
| ACR push denied | Service principal needs Contributor on `sai-app-rg` |
| Rollout timeout | `kubectl get pods` + `kubectl describe pod <name>` |

---

## End-to-end (Steps 1–7 complete)

```text
Step 1:  Python + uv
Step 2:  Docker image
Step 3:  ACR (push image)
Step 4:  AKS (manual deploy + Load Balancer)
Step 5:  k8s YAML (deployment + service)
Step 6:  CI/CD concept + deploy.yml
Step 7:  Service principal + secrets + first auto deploy  ← you are here
```

```text
git push  →  GitHub Actions  →  ACR  →  AKS  →  http://<EXTERNAL-IP>/data  ✅
```

---

## Command reference (Step 7)

```powershell
# Subscription ID
az account show --query id -o tsv

# Service principal (one-time)
az ad sp create-for-rbac --name "github-saiapp-deploy" `
  --role contributor `
  --scopes /subscriptions/2853d84e-1dda-4f6d-9ebd-3c6a3e1f9ede/resourceGroups/sai-app-rg `
  --sdk-auth

# Push workflow
git add .github/ MDFile-Reference/
git commit -m "Add CI/CD workflow"
git push
```

---

## When demo is finished

```powershell
az group delete --name sai-app-rg --yes --no-wait
```

Also delete GitHub secret `AZURE_CREDENTIALS` or rotate service principal if exposed.

---

## What's next

- **Step 8:** GitHub secrets copy-paste + push + first pipeline — see **`Step8-GitHub-Secrets-Push.md`**
