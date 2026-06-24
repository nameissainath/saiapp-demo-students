# Azure Web App + ACR Reference

How the Web App pulls the same Docker image from ACR as AKS, and what was configured to fix pull/auth issues.

---

## Architecture

```
GitHub Actions
    ↓
Build + push → sainathreddycontainer.azurecr.io/cricket-api:v3
    ↓
┌─────────────────────┬──────────────────────────────┐
│ AKS                 │ Azure Web App                │
│ (attach-acr)        │ (Managed Identity + AcrPull) │
│ pulls image         │ pulls same image             │
└─────────────────────┴──────────────────────────────┘
```

Same image in ACR. **Different auth** for each target.

---

## Why AKS worked but Web App failed

| Target | How it pulls from ACR | Setup |
|--------|------------------------|-------|
| **AKS** | Cluster attached to ACR | `az aks update --attach-acr sainathreddycontainer` |
| **Web App** | Needs its own permission | Managed Identity + **AcrPull** role on ACR |

Error seen in Web App logs:

```
ImagePullUnauthorizedFailure
Failed to pull image: sainathreddycontainer.azurecr.io/cricket-api:v2
Check registry credentials.
```

**Cause:** Web App had no valid permission to pull from ACR (not a wrong tag issue).

---

## Fix applied: Managed Identity (recommended)

### Step 1 — Enable System Assigned Identity on Web App (Portal)

1. Go to [portal.azure.com](https://portal.azure.com)
2. Search **`cricket-api-sai`** → open the Web App
3. Left menu → **Settings** → **Identity**
4. Tab **System assigned**
5. Set **Status** to **On**
6. Click **Save** → confirm **Yes**
7. Copy **Object (principal) ID** (optional — for CLI; Portal member search uses app name)

**CLI alternative:**

```powershell
az webapp identity assign `
  --name cricket-api-sai `
  --resource-group sai-app-rg
```

Copy the **Object (principal) ID** from the output.

---

### Step 2 — Grant AcrPull on Container Registry (Portal)

1. Search **`sainathreddycontainer`** → open **Container registry**
2. Left menu → **Access control (IAM)**
3. Click **Add** → **Add role assignment**
4. **Role** tab → search **`AcrPull`** → select **AcrPull** → **Next**
   - Description: *Pull artifacts from a registry* (not "Contributor")
5. **Members** tab → **Assign access to:** User, group, or service principal
6. Click **+ Select members**
7. Search **`cricket-api-sai`** → select the Web App → **Select**
8. **Next** → **Review + assign** → **Review + assign**
9. Back on **Role assignments** — confirm **cricket-api-sai** has **AcrPull**

Wait **1–2 minutes** for the role to propagate.

**CLI alternative:**

```powershell
az role assignment create `
  --assignee "WEBAPP_PRINCIPAL_ID" `
  --role "AcrPull" `
  --scope "/subscriptions/2853d84e-1dda-4f6d-9ebd-3c6a3e1f9ede/resourceGroups/sai-app-rg/providers/Microsoft.ContainerRegistry/registries/sainathreddycontainer"
```

---

### Step 3 — Use Managed Identity in container settings (Portal)

1. Open Web App **`cricket-api-sai`**
2. Left menu → **Deployment** → **Deployment Center**
3. Tab **Containers** → click **Edit** on the **main** container (or **Edit container**)
4. Set:

| Setting | Value |
|---------|--------|
| Image source | **Azure Container Registry** |
| Registry | `sainathreddycontainer` |
| **Authentication** | **Managed identity** (not Admin credentials) |
| Image | `cricket-api` |
| Tag | `v3` (match current `IMAGE_TAG` in deploy.yml) |
| **Port** | **8000** |

5. Click **Save**

---

### Step 4 — Set port environment variable (Portal)

1. Web App → **Settings** → **Environment variables** (or **Configuration**)
2. **Application settings** tab → **+ Add**
3. Name: **`WEBSITES_PORT`** → Value: **`8000`**
4. **Apply** → **Confirm** (app restarts)

---

### Step 5 — Restart and verify (Portal)

1. Web App → **Overview** → **Restart**
2. **Monitoring** → **Log stream** — look for:
   ```
   Pulling image: sainathreddycontainer.azurecr.io/cricket-api:v3
   Container started successfully
   ```
3. Open: https://cricket-api-sai-buceewb9bhf3e8hr.centralindia-01.azurewebsites.net/players

---

## Alternative: ACR Admin credentials (demo / quick fix)

If not using managed identity:

```powershell
az acr update --name sainathreddycontainer --admin-enabled true
az acr credential show --name sainathreddycontainer
```

**Portal:** Edit container → Authentication → **Admin credentials**

Managed identity is preferred for production (no password rotation in Portal).

---

## GitHub Actions automation (deploy.yml)

After each push, the workflow updates Web App to the same tag as AKS:

```yaml
- name: Deploy to Azure Web App
  run: |
    az webapp config container set \
      --name ${{ secrets.AZURE_WEBAPP_NAME }} \
      --resource-group ${{ secrets.AKS_RESOURCE_GROUP }} \
      --docker-custom-image-name ${{ secrets.ACR_LOGIN_SERVER }}/cricket-api:${{ env.IMAGE_TAG }}

    az webapp restart \
      --name ${{ secrets.AZURE_WEBAPP_NAME }} \
      --resource-group ${{ secrets.AKS_RESOURCE_GROUP }}
```

**Important:** With **Managed Identity** configured in Portal, the workflow only needs to change the image tag and restart. ACR credentials are not stored in GitHub.

Bump `IMAGE_TAG` in deploy.yml (`v3` → `v4`) — both AKS and Web App update together. No manual Portal tag change needed.

---

## GitHub secrets for Web App

| Secret | Example | Purpose |
|--------|---------|---------|
| `AZURE_WEBAPP_NAME` | `cricket-api-sai` | Web App resource name |
| `AZURE_WEBAPP_HOSTNAME` | `cricket-api-sai-buceewb9bhf3e8hr.centralindia-01.azurewebsites.net` | Health check URL |

Reuse existing secrets: `AZURE_CREDENTIALS`, `ACR_LOGIN_SERVER`, `AKS_RESOURCE_GROUP`.

---

## Portal settings to avoid (caused issues)

| Do not use | Why |
|------------|-----|
| Deployment Center → **GitHub Actions** (Portal built-in) | Conflicts with our `deploy.yml`; expects commit SHA tags |
| Image tag **"Tagged with GitHub commit ID"** | Workflow pushes `v1`/`v2`/`v3`, not commit SHA |
| **Sidecar pattern** update banner | Not needed for single-container FastAPI app |
| Port **80** or empty | App listens on **8000** inside container |

Use **one** automation path: `.github/workflows/deploy.yml`.

---

## Web App resources

| Item | Value |
|------|--------|
| Web App name | `cricket-api-sai` |
| URL | https://cricket-api-sai-buceewb9bhf3e8hr.centralindia-01.azurewebsites.net |
| Resource group | `sai-app-rg` |
| Region | Central India |
| ACR | `sainathreddycontainer.azurecr.io` |
| Image | `cricket-api` |
| Container port | `8000` |
| Plan | Basic B1 (required for custom Docker) |

---

## Troubleshooting

### ImagePullUnauthorizedFailure

1. Confirm **AcrPull** on ACR for `cricket-api-sai` (IAM → Role assignments)
2. Confirm **Managed identity** is On (Web App → Identity)
3. Confirm container auth = **Managed identity** (not Admin with expired password)
4. Restart Web App after role assignment

### Site blocked after repeated failures

Wait 1 minute, fix auth, then **Restart**.

### App up in Portal but 502 / connection refused

- Set **Port = 8000** in Edit container
- Set **`WEBSITES_PORT=8000`** in Environment variables

### Manual Portal tag change works but CI does not

1. Check GitHub Actions → **Deploy to Azure Web App** step (green?)
2. Confirm `AZURE_WEBAPP_NAME` and `AZURE_WEBAPP_HOSTNAME` secrets exist
3. Confirm `IMAGE_TAG` in deploy.yml matches the tag pushed to ACR

---

## Verify pull is working

**Log stream** (Web App → Monitoring → Log stream) should show:

```
Pulling image: sainathreddycontainer.azurecr.io/cricket-api:v3
Container started successfully
```

**Browser:**

- `/players`
- `/news`
- `/docs`

---

## AKS vs Web App auth (summary)

| | AKS | Web App |
|---|-----|---------|
| Auth method | ACR attached to cluster | Managed Identity + AcrPull |
| Config location | `az aks update --attach-acr` | Portal Identity + ACR IAM |
| Deploy from CI | `kubectl apply` + sed tag | `az webapp config container set` + restart |
| Public URL | LoadBalancer IP | `*.azurewebsites.net` |

Both pull the **same image** from the **same ACR** after each `IMAGE_TAG` release.
