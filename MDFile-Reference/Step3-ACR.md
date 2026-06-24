# Step 3 — Azure Resource Group + ACR

Reference for creating Azure resources and pushing the Docker image to **Azure Container Registry (ACR)**.

> **Note:** ACR = Azure Container Registry (stores Docker images).  
> This is **not** ACS (Azure Container Service — deprecated).

---

## Goal

```text
Local Docker image  →  Azure Container Registry  →  (later) AKS
```

Store `saiapp-demo` in the cloud so AKS can pull and run it.

---

## Prerequisites (Steps 1 & 2 done)

| Step | What |
|------|------|
| Step 1 | Python app + `uv venv` + `uv sync` |
| Step 2 | `Dockerfile` built → local image `saiapp-demo` |

Verify local image exists:

```powershell
docker images
```

---

## Your Azure Resources (this project)

| Resource | Name |
|----------|------|
| Resource Group | `sai-app-rg` |
| Container Registry | `sainathreddycontainer` |
| Login Server | `sainathreddycontainer.azurecr.io` |
| Region | East US |
| Pricing SKU | Basic |

---

# Part A — Create Resource Group

A **Resource Group** is a folder that holds all Azure resources for this project.

---

## Option 1: Azure Portal

1. Go to [Azure Portal](https://portal.azure.com)
2. Search **Resource groups** → **Create**
3. Fill in:
   - **Subscription:** your subscription
   - **Resource group name:** `sai-app-rg`
   - **Region:** `East US`
4. Click **Review + create** → **Create**

---

## Option 2: Azure CLI

```powershell
az login

az group create --name sai-app-rg --location eastus
```

Verify:

```powershell
az group show --name sai-app-rg --output table
```

---

# Part B — Create ACR (Container Registry)

ACR stores your Docker images in Azure (like a private Docker Hub).

---

## Option 1: Azure Portal

1. Search **Container registries** → **Create**
2. Fill in **Basics**:

| Field | Value |
|-------|-------|
| Subscription | your subscription |
| Resource group | `sai-app-rg` |
| Registry name | `sainathreddycontainer` |
| Location | East US |
| Domain name label scope | **Unsecure** (simple URL) |
| Pricing plan | **Basic** (fine for demo) |
| Role assignment permissions mode | **RBAC Registry Permissions** |

3. **Networking** — leave defaults (public access is OK for demo)
4. Click **Review + create** → **Create**
5. Wait for **Provisioning state: Succeeded**

Your login server will be:

```text
sainathreddycontainer.azurecr.io
```

---

## Option 2: Azure CLI

```powershell
az acr create `
  --resource-group sai-app-rg `
  --name sainathreddycontainer `
  --sku Basic `
  --location eastus
```

Verify:

```powershell
az acr show --name sainathreddycontainer --output table
```

Check if a name is available (before creating):

```powershell
az acr check-name --name sainathreddycontainer
```

---

## Portal Settings Explained

| Setting | What to pick | Why |
|---------|--------------|-----|
| **Domain name label scope → Unsecure** | Unsecure | Clean URL: `name.azurecr.io` |
| **Role assignment → RBAC Registry Permissions** | RBAC Registry | Simple permissions for demo |
| **Pricing plan → Basic** | Basic | Cheapest, enough for learning |

---

# Part C — Access Keys (Admin User)

Used to log in to ACR from your laptop with `docker login`.

## Portal

1. Open registry **`sainathreddycontainer`**
2. Left menu → **Settings** → **Access keys**
3. Enable **Admin user** → **Save**
4. Note down:
   - **Login server:** `sainathreddycontainer.azurecr.io`
   - **Username:** `sainathreddycontainer`
   - **Password:** (from portal — **do not commit to git**)

> Store the password in a password manager or `.env` file. Never push secrets to GitHub.

---

# Part D — Push Image to ACR

## Step 1: Build local image (if not already done)

```powershell
cd c:\Users\saina\OneDrive\Desktop\SaiApp
docker build -t saiapp-demo .
```

---

## Step 2: Login to ACR

**Option A — Azure CLI (recommended):**

```powershell
az login
az acr login --name sainathreddycontainer
```

**Option B — Docker login with access keys:**

```powershell
docker login sainathreddycontainer.azurecr.io -u sainathreddycontainer -p YOUR_PASSWORD
```

Replace `YOUR_PASSWORD` with the password from **Access keys** in the portal.

---

## Step 3: Tag the image for ACR

Give your local image the full ACR address:

```powershell
docker tag saiapp-demo sainathreddycontainer.azurecr.io/saiapp-demo:latest
```

| Part | Meaning |
|------|---------|
| `sainathreddycontainer.azurecr.io` | ACR login server |
| `saiapp-demo` | Repository (image) name |
| `latest` | Tag (version label) |

---

## Step 4: Push to ACR

```powershell
docker push sainathreddycontainer.azurecr.io/saiapp-demo:latest
```

First push may take a few minutes.

---

## Step 5: Verify

**Portal:**

1. Open **`sainathreddycontainer`**
2. Left menu → **Services** → **Repositories**
3. You should see **`saiapp-demo`** with tag **`latest`**

**CLI:**

```powershell
az acr repository list --name sainathreddycontainer --output table
az acr repository show-tags --name sainathreddycontainer --repository saiapp-demo --output table
```

---

# Full Command Block (copy-paste)

```powershell
# Prerequisites
az login

# Login to ACR
az acr login --name sainathreddycontainer

# Build (if needed)
cd c:\Users\saina\OneDrive\Desktop\SaiApp
docker build -t saiapp-demo .

# Tag + push
docker tag saiapp-demo sainathreddycontainer.azurecr.io/saiapp-demo:latest
docker push sainathreddycontainer.azurecr.io/saiapp-demo:latest

# Verify
az acr repository list --name sainathreddycontainer --output table
```

---

# Image vs Container (reminder)

| Thing | Local (Step 2) | Azure (Step 3) |
|-------|----------------|----------------|
| **Image** | `saiapp-demo` | `sainathreddycontainer.azurecr.io/saiapp-demo:latest` |
| **Container** | Created with `docker run` | Created later by **AKS** |

After push, your image lives in ACR. AKS will pull it in Step 4.

---

# Troubleshooting

| Problem | Fix |
|---------|-----|
| ACR create failed — name taken | Pick a new name or reuse existing registry |
| `unauthorized` on push | Run `az login` then `az acr login` again |
| `denied: requested access` | Enable Admin user, or ensure you have **AcrPush** role |
| `no such image` | Run `docker build -t saiapp-demo .` first |
| `az: command not found` | Install [Azure CLI](https://learn.microsoft.com/en/cli/azure/install-azure-cli) |

---

# Quick Command Reference

| Command | Meaning |
|---------|---------|
| `az group create --name sai-app-rg --location eastus` | Create resource group |
| `az acr create --resource-group sai-app-rg --name sainathreddycontainer --sku Basic` | Create ACR |
| `az acr login --name sainathreddycontainer` | Log in to ACR |
| `docker tag saiapp-demo sainathreddycontainer.azurecr.io/saiapp-demo:latest` | Tag for ACR |
| `docker push sainathreddycontainer.azurecr.io/saiapp-demo:latest` | Upload image to ACR |
| `az acr repository list --name sainathreddycontainer` | List images in ACR |

---

## What's Next (not done yet)

- Step 4: Create **AKS** (Azure Kubernetes Service)
- Step 5: Deploy app using image from ACR
- Step 6: Expose app via Load Balancer / public URL
