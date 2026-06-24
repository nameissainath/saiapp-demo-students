# Step 11 — Azure Web App (optional extension)

Deploy the **same Docker image** to **Azure Web App** in addition to AKS.

> **Current codebase status:** `deploy.yml` deploys to **AKS only**. Web App steps below are **not in the repo yet** — add them when you create the Web App in Azure Portal.

---

## What you have today (Steps 1–10)

| Item | This project |
|------|----------------|
| Image name | `saiapp-demo` (not `cricket-api`) |
| ACR | `sainathreddycontainer.azurecr.io` |
| K8s folder | `k8s/` (`deployment.yaml`, `service.yaml`) |
| Workflow | `.github/workflows/deploy.yml` |
| Version tag | `env IMAGE_TAG: v2` in `deploy.yml` |
| Deploy target | **AKS only** |

**Current pipeline flow:**

```text
Push to main
    ↓
Azure login + ACR login
    ↓
docker build → saiapp-demo:IMAGE_TAG + saiapp-demo:latest
    ↓
docker push to ACR
    ↓
sed patch k8s/deployment.yaml → kubectl apply (deployment + service)
    ↓
kubectl rollout status
```

---

## API endpoints (current `main.py`)

Test on AKS (`http://<EXTERNAL-IP>/`) or Web App after you add it:

| URL | Description |
|-----|-------------|
| `GET /` | Health check |
| `GET /version` | App version |
| `GET /cricket` | Sample cricket teams |
| `GET /games` | Sample games list |
| `GET /data` | JSONPlaceholder post |
| `GET /users` | JSONPlaceholder user |
| `GET /docs` | FastAPI Swagger UI |

---

## Release a new version (same as Step 10)

1. Make code changes (e.g. edit `main.py`)
2. Bump in `.github/workflows/deploy.yml`:

   ```yaml
   env:
     IMAGE_TAG: v2   # change to v3, v4, ...
   ```

3. Commit and push to `main`

ACR gets `saiapp-demo:v3` + `latest`. AKS runs the new tag via `sed` + `kubectl apply`.

---

## GitHub Actions secrets (current — AKS)

| Secret | Example value |
|--------|---------------|
| `AZURE_CREDENTIALS` | Service principal JSON |
| `ACR_NAME` | `sainathreddycontainer` |
| `ACR_LOGIN_SERVER` | `sainathreddycontainer.azurecr.io` |
| `AKS_RESOURCE_GROUP` | `sai-app-rg` |
| `AKS_CLUSTER_NAME` | `sai-app-aks` |

---

## Adding Azure Web App (future — add to `deploy.yml`)

When you create a **Linux Web App** pulling from the same ACR, add **two secrets** and **two workflow steps**.

### New GitHub secrets

| Secret | Example | Description |
|--------|---------|-------------|
| `AZURE_WEBAPP_NAME` | `saiapp-web` | Web App resource name in Portal |
| `AZURE_WEBAPP_HOSTNAME` | `saiapp-web.azurewebsites.net` | Hostname for health check (no `https://`) |

### Add to `deploy.yml` (after AKS deploy)

```yaml
- name: Deploy to Azure Web App
  run: |
    az webapp config container set \
      --name ${{ secrets.AZURE_WEBAPP_NAME }} \
      --resource-group ${{ secrets.AKS_RESOURCE_GROUP }} \
      --docker-custom-image-name ${{ secrets.ACR_LOGIN_SERVER }}/saiapp-demo:${{ env.IMAGE_TAG }}

    az webapp restart \
      --name ${{ secrets.AZURE_WEBAPP_NAME }} \
      --resource-group ${{ secrets.AKS_RESOURCE_GROUP }}

- name: Verify Web App
  run: |
    echo "Web App URL: https://${{ secrets.AZURE_WEBAPP_HOSTNAME }}"
    curl --fail --retry 5 --retry-delay 10 \
      "https://${{ secrets.AZURE_WEBAPP_HOSTNAME }}/"
```

**Same `IMAGE_TAG`** — ACR, AKS, and Web App all use `saiapp-demo:v2` (or v3, etc.).

---

## Web App Portal settings (one-time)

Configure once in Azure Portal:

| Setting | Value |
|---------|--------|
| Publish | Docker Container (Linux) |
| Image source | Azure Container Registry |
| Registry | `sainathreddycontainer` |
| Image | **`saiapp-demo`** |
| Port / `WEBSITES_PORT` | **`8000`** |
| Pricing plan | Basic B1 (or higher) |

Enable **Admin user** on ACR or use managed identity so Web App can pull the image.

---

## Full pipeline (after Web App is added)

```text
Push to main
    ↓
Build + push  saiapp-demo:IMAGE_TAG  +  latest
    ↓
AKS   → kubectl apply (k8s/deployment.yaml, service.yaml)
    ↓
Web App → az webapp config container set + restart
    ↓
Verify AKS rollout + Web App health check
```

---

## Useful commands

```powershell
# AKS
az aks get-credentials --resource-group sai-app-rg --name sai-app-aks --overwrite-existing
kubectl get pods
kubectl get svc

# ACR tags
az acr repository show-tags --name sainathreddycontainer --repository saiapp-demo --output table

# Web App (browser, after Step 11 setup)
# https://<AZURE_WEBAPP_HOSTNAME>/
# https://<AZURE_WEBAPP_HOSTNAME>/cricket
# https://<AZURE_WEBAPP_HOSTNAME>/docs
```

---

## Common doc mistakes (fixed in this file)

| Wrong in old draft | Correct for this project |
|--------------------|--------------------------|
| `cricket-api` image | **`saiapp-demo`** |
| `aks/deployment.yaml` | **`k8s/deployment.yaml`** |
| `hpa.yaml` | **Not in repo** (optional later) |
| `/players`, `/news` | **`/cricket`, `/games`, `/docs`** |
| Web App already in workflow | **Not yet** — add steps when ready |

---

## Service principal (reference)

```powershell
az ad sp create-for-rbac --name "github-saiapp-deploy" `
  --role contributor `
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/sai-app-rg `
  --sdk-auth
```

Copy JSON into GitHub secret `AZURE_CREDENTIALS`. Contributor on `sai-app-rg` covers AKS, ACR, and Web App in that resource group.

---

## Step docs index

| File | Topic |
|------|-------|
| `Step10-Versioned-Deploy-and-Troubleshooting.md` | v1/v2 tags, rollback, troubleshooting |
| **`Step11-Webapp.md`** | **Optional Web App + same image as AKS** |
