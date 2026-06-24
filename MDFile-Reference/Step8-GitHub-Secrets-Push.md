# Step 8 — GitHub Secrets, Push & First Pipeline Run

Complete copy-paste reference for **adding secrets**, **pushing workflow**, and **running CI/CD**. Do this before/after Step 7 service principal is created.

> **You will push later** — use this file as your checklist.

---

## Remember this

```text
5 GitHub secrets  →  git push  →  Actions tab  →  app live
```

**Do NOT add ACR admin username/password to GitHub** — CI/CD uses service principal JSON only.

---

## Where to add secrets (GitHub Portal)

1. Repo: **nameissainath/saiapp-demo-students**
2. **Settings** tab
3. Left sidebar → **Secrets and variables** → **Actions**
4. Click **New repository secret** (5 times)

**Direct link:**

```text
https://github.com/nameissainath/saiapp-demo-students/settings/secrets/actions
```

**Use:** Repository secrets (green button) — **not** Environment secrets.

---

## All 5 secrets — copy-paste

Names are **case-sensitive**. Must match exactly.

### 1. `AZURE_CREDENTIALS`

| Field | Value |
|-------|-------|
| **Name** | `AZURE_CREDENTIALS` |
| **Secret** | Full JSON from `az ad sp create-for-rbac ... --sdk-auth` |

**Get JSON (if not saved yet):**

```powershell
az ad sp create-for-rbac --name "github-saiapp-deploy" `
  --role contributor `
  --scopes /subscriptions/2853d84e-1dda-4f6d-9ebd-3c6a3e1f9ede/resourceGroups/sai-app-rg `
  --sdk-auth
```

**JSON shape (paste YOUR output, not this example):**

```json
{
  "clientId": "...",
  "clientSecret": "...",
  "subscriptionId": "2853d84e-1dda-4f6d-9ebd-3c6a3e1f9ede",
  "tenantId": "...",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

---

### 2. `ACR_NAME`

| Field | Value |
|-------|-------|
| **Name** | `ACR_NAME` |
| **Secret** | `sainathreddycontainer` |

---

### 3. `ACR_LOGIN_SERVER`

| Field | Value |
|-------|-------|
| **Name** | `ACR_LOGIN_SERVER` |
| **Secret** | `sainathreddycontainer.azurecr.io` |

---

### 4. `AKS_RESOURCE_GROUP`

| Field | Value |
|-------|-------|
| **Name** | `AKS_RESOURCE_GROUP` |
| **Secret** | `sai-app-rg` |

---

### 5. `AKS_CLUSTER_NAME`

| Field | Value |
|-------|-------|
| **Name** | `AKS_CLUSTER_NAME` |
| **Secret** | `sai-app-aks` |

---

## Secrets checklist

| # | Secret name | Value | Done? |
|---|-------------|-------|-------|
| 1 | `AZURE_CREDENTIALS` | Full JSON | ☐ |
| 2 | `ACR_NAME` | `sainathreddycontainer` | ☐ |
| 3 | `ACR_LOGIN_SERVER` | `sainathreddycontainer.azurecr.io` | ☐ |
| 4 | `AKS_RESOURCE_GROUP` | `sai-app-rg` | ☐ |
| 5 | `AKS_CLUSTER_NAME` | `sai-app-aks` | ☐ |

After adding, you should see **5 repository secrets** (values hidden — normal).

---

## What NOT to add as GitHub secrets

| Do NOT add | Why |
|------------|-----|
| ACR **admin password** | CI/CD uses `az acr login` after Azure login — not admin user |
| ACR **username** | Same — not needed in workflow |
| `.env` file contents | Never put secrets in repo |
| Service principal JSON in code | Only in GitHub secret |

### When ACR admin credentials ARE used (local only)

| Use | Command |
|-----|---------|
| Push from laptop | `docker login sainathreddycontainer.azurecr.io -u sainathreddycontainer -p PASSWORD` |
| AKS ImagePullBackOff fix | `kubectl create secret docker-registry ...` (Step 4) |

Get password from: Azure Portal → **sainathreddycontainer** → **Access keys** → Admin user.  
**Never commit password to git or markdown files.**

---

## Enable GitHub Actions (if needed)

**Settings → Actions → General**

- Allow **All actions**
- Workflow permissions: read/write as needed (defaults usually OK)

---

## Push workflow to GitHub (when ready)

Files to push:

```text
.github/worflows/deploy.yml
MDFile-Reference/          (Step docs)
```

**Commands:**

```powershell
cd c:\Users\saina\OneDrive\Desktop\SaiApp
git add .github/ MDFile-Reference/
git status
git commit -m "Add CI/CD workflow and Step docs"
git push
```

**`git status` should show:**

- ✅ `.github/worflows/deploy.yml`
- ✅ `MDFile-Reference/Step8-...md` etc.
- ❌ NOT `.venv/`, `__pycache__/`, `.env`

**Or push everything safe:**

```powershell
git add .
git status
git commit -m "Add CI/CD workflow and docs"
git push
```

(`.gitignore` blocks `.venv` and cache.)

---

## Watch first pipeline run

1. GitHub → **Actions** tab
2. Workflow: **Build and Deploy to AKS**
3. First run starts after push to `main`
4. Wait **5–10 minutes** — green checkmark = success

**Manual run:** Actions → **Build and Deploy to AKS** → **Run workflow**

### What the pipeline does

```text
Checkout code
    ↓
Azure login (AZURE_CREDENTIALS)
    ↓
az acr login (ACR_NAME)
    ↓
docker build + docker push → sainathreddycontainer.azurecr.io/saiapp-demo:latest
    ↓
az aks get-credentials
    ↓
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
    ↓
kubectl rollout restart deployment/saiapp
    ↓
Verify rollout success
```

---

## Verify app after green pipeline

```powershell
kubectl get pods
kubectl get svc
```

Browser:

```text
http://<EXTERNAL-IP>/
http://<EXTERNAL-IP>/data
```

---

## Daily workflow (after setup complete)

```powershell
# Edit code → then:
git add .
git commit -m "Your change description"
git push
# Check Actions tab → green → test URL
```

**You stop running manually:**

```text
docker build
docker push
kubectl apply
kubectl expose
```

---

## Security reminders

| Rule | Why |
|------|-----|
| Never commit `AZURE_CREDENTIALS` JSON | Full Azure access to `sai-app-rg` |
| Never commit ACR admin password | Registry access |
| Never paste secrets in chat/issues | Can be leaked |
| Rotate secrets if exposed | Regenerate in Azure Entra ID + update GitHub secret |
| Delete `sai-app-rg` when demo done | Stop credits + reduce risk |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Workflow not in Actions tab | Push `.github/worflows/deploy.yml` to `main` |
| Secret not found | Exact name: `AZURE_CREDENTIALS` not `Azure_Credentials` |
| Azure login failed | Re-paste full JSON; check subscription ID in JSON |
| ACR push failed | Service principal needs Contributor on `sai-app-rg` |
| kubectl failed | Check `AKS_RESOURCE_GROUP` and `AKS_CLUSTER_NAME` |
| Red X on rollout | Actions log → `kubectl describe pod` locally |

---

## Full journey (Steps 1–8)

| Step | What |
|------|------|
| 1 | Python + uv |
| 2 | Docker image |
| 3 | ACR — push image |
| 4 | AKS — manual deploy + Load Balancer |
| 5 | `k8s/deployment.yaml` + `service.yaml` |
| 6 | CI/CD concept + `deploy.yml` |
| 7 | Service principal (`github-saiapp-deploy`) |
| 8 | GitHub secrets + push + first Actions run ← **this file** |

```text
git push  →  GitHub Actions  →  ACR  →  AKS  →  public URL  ✅
```

---

## What's next

- **Step 9:** Full recap + daily workflow — see **`Step9-Complete-Journey.md`**

---

## Quick quick reference

```powershell
# Secrets already added in GitHub — then:
cd c:\Users\saina\OneDrive\Desktop\SaiApp
git add .github/ MDFile-Reference/
git commit -m "Add CI/CD workflow and docs"
git push

# Verify locally after pipeline succeeds:
kubectl get svc
```

**GitHub repo:** https://github.com/nameissainath/saiapp-demo-students
