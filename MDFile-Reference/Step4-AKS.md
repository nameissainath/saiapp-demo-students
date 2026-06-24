# Step 4 — Create AKS (Azure Kubernetes Service)

Reference for creating an AKS cluster in Azure — **Portal** and **CLI** — so it can later pull and run your image from ACR.

---

## Goal

```text
ACR (image stored)  →  AKS (cluster to run containers)  →  deploy app (Step 5)
```

AKS is the Kubernetes cluster that runs your Docker containers in the cloud.

---

## Prerequisites

| Done in | What |
|---------|------|
| Step 1 | Python app built locally |
| Step 2 | Docker image `saiapp-demo` |
| Step 3 | Resource group `sai-app-rg` + ACR `sainathreddycontainer` + image pushed |

Also install locally (if not already):

- [Azure CLI](https://learn.microsoft.com/en/cli/azure/install-azure-cli)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) (or installed via `az aks install-cli`)

---

## Your Azure Resources (this project)

| Resource | Name |
|----------|------|
| Resource Group | `sai-app-rg` |
| Container Registry | `sainathreddycontainer` |
| AKS Cluster (to create) | `sai-app-aks` |
| Region | East US |

---

## What AKS Will Create

When you create AKS, Azure also creates (automatically):

- **Node pool** — VM(s) that run your containers
- **Virtual network** — networking for the cluster (default is fine for demo)
- **Managed identity** — so AKS can talk to other Azure services (like ACR)

---

# Part A — Create AKS (Azure Portal)

## 1. Open the create wizard

1. Go to [Azure Portal](https://portal.azure.com)
2. Search **Kubernetes services** → **Create** → **Kubernetes cluster**

---

## 2. Basics tab

| Field | Value |
|-------|-------|
| **Subscription** | your subscription |
| **Resource group** | `sai-app-rg` |
| **Cluster name** | `sai-app-aks` |
| **Region** | East US (same as ACR) |
| **Availability zones** | None (OK for demo) |
| **AKS pricing tier** | **Free** (demo) |
| **Kubernetes version** | Default (latest stable) |
| **Automatic upgrade** | Enabled (default) |

**Node pools → default pool:**

| Field | Value |
|-------|-------|
| **Node pool name** | `nodepool1` (default) |
| **Node size** | `Standard_B2s` or `Standard_DS2_v2` (small/cheap for demo) |
| **Scale method** | Manual |
| **Node count** | `1` (demo — saves cost) |

Click **Next: Authentication**.

---

## 3. Authentication tab

| Field | Value |
|-------|-------|
| **Authentication method** | **Local accounts with Kubernetes RBAC** (simple for demo) |
| **Kubernetes RBAC** | Enabled |

Click **Next: Networking**.

---

## 4. Networking tab

For demo, keep defaults:

| Field | Value |
|-------|-------|
| **Network configuration** | Kubenet (default) |
| **Load balancer** | Standard (default) |
| **Set authorized IP ranges** | Disabled (for demo) |

Click **Next** through **Integrations**, **Monitoring**, **Tags** — leave defaults.

---

## 5. Integrations tab (optional but useful)

| Field | Value |
|-------|-------|
| **Container registries** | Select `sainathreddycontainer` if shown |

> If you attach ACR here, AKS can pull images without extra setup later.

Click **Review + create** → **Create**.

Cluster creation takes **5–15 minutes**.

---

## 6. Verify in Portal

After **Provisioning state: Succeeded**:

1. Open **`sai-app-aks`**
2. Note the **API server address** on the Overview page
3. Left menu → **Node pools** — should show 1 node **Ready**

---

# Part B — Create AKS (Azure CLI)

## 1. Login

```powershell
az login
az account show
```

---

## 2. Create the cluster

```powershell
az aks create `
  --resource-group sai-app-rg `
  --name sai-app-aks `
  --location eastus `
  --node-count 1 `
  --node-vm-size Standard_B2s `
  --generate-ssh-keys `
  --attach-acr sainathreddycontainer
```

| Flag | Meaning |
|------|---------|
| `--resource-group sai-app-rg` | Same RG as ACR |
| `--name sai-app-aks` | Cluster name |
| `--node-count 1` | 1 worker node (cheap demo) |
| `--node-vm-size Standard_B2s` | Small VM size |
| `--generate-ssh-keys` | SSH keys for node access (optional) |
| `--attach-acr sainathreddycontainer` | Lets AKS pull from your ACR |

> Creation takes several minutes. Wait until the command finishes.

---

## 3. Connect kubectl to the cluster

Download cluster credentials into your local kubeconfig:

```powershell
az aks get-credentials --resource-group sai-app-rg --name sai-app-aks --overwrite-existing
```

---

## 4. Verify the cluster works

```powershell
kubectl get nodes
```

Expected:

```text
NAME                                STATUS   ROLES   AGE   VERSION
aks-nodepool1-xxxxxxxx-vmss000000   Ready    agent   ...   v1.xx.x
```

```powershell
kubectl cluster-info
```

---

## 5. Verify AKS can pull from ACR

If you used `--attach-acr` during create, check:

```powershell
az aks check-acr --resource-group sai-app-rg --name sai-app-aks --acr sainathreddycontainer
```

Expected:

```text
Your cluster can pull images from sainathreddycontainer.azurecr.io!
```

**If you did NOT attach ACR during create**, run:

```powershell
az aks update `
  --resource-group sai-app-rg `
  --name sai-app-aks `
  --attach-acr sainathreddycontainer
```

---

# Part C — Portal vs CLI Summary

| Task | Portal | CLI |
|------|--------|-----|
| Create cluster | Kubernetes services → Create | `az aks create ...` |
| Connect kubectl | Use Cloud Shell or CLI locally | `az aks get-credentials ...` |
| Attach ACR | Integrations tab during create | `--attach-acr` flag |
| Check nodes | Node pools in portal | `kubectl get nodes` |
| Check ACR access | — | `az aks check-acr ...` |

---

# Full CLI Command Block (copy-paste)

```powershell
az login

# Create AKS + attach ACR
az aks create `
  --resource-group sai-app-rg `
  --name sai-app-aks `
  --location eastus `
  --node-count 1 `
  --node-vm-size Standard_B2s `
  --generate-ssh-keys `
  --attach-acr sainathreddycontainer

# Connect kubectl
az aks get-credentials --resource-group sai-app-rg --name sai-app-aks --overwrite-existing

# Verify
kubectl get nodes
az aks check-acr --resource-group sai-app-rg --name sai-app-aks --acr sainathreddycontainer
```

---

# Recommended Settings for Demo

| Setting | Demo value | Why |
|---------|------------|-----|
| Node count | 1 | Cheapest |
| VM size | Standard_B2s | Enough for FastAPI demo |
| Pricing tier | Free | No SLA cost for learning |
| Region | East US | Same as ACR |
| Attach ACR | Yes | Required to pull your image |

---

# Troubleshooting

| Problem | Fix |
|---------|-----|
| Quota exceeded | Reduce node count to 1, use smaller VM, or request quota increase |
| Region not available | Pick another region (update ACR region if needed) |
| `kubectl: command not found` | Run `az aks install-cli` |
| ACR pull fails later | Run `az aks update --attach-acr sainathreddycontainer` |
| Cluster create slow | Normal — wait 5–15 minutes |
| Permission denied | Need **Contributor** on subscription or resource group |

---

# Quick Command Reference

| Command | Meaning |
|---------|---------|
| `az aks create --resource-group sai-app-rg --name sai-app-aks ...` | Create AKS cluster |
| `az aks get-credentials --resource-group sai-app-rg --name sai-app-aks` | Connect kubectl |
| `kubectl get nodes` | Show cluster worker nodes |
| `az aks update --attach-acr sainathreddycontainer` | Link ACR to AKS |
| `az aks check-acr --acr sainathreddycontainer` | Test ACR pull access |
| `az aks list --resource-group sai-app-rg -o table` | List clusters in RG |

---

## What's Next (not done yet)

- Step 5: Deploy app to AKS (`kubectl create deployment` or YAML)
- Step 6: Expose app with Load Balancer (`kubectl expose`)
- Step 7: Open public URL and test `/` and `/data`

---

# Node, vCPU & Pods — Quick Reference

## Node = VM

A **node** is one Azure **virtual machine (VM)** in your cluster. Each node runs your app containers.

```text
AKS Cluster
   └── Node (1 VM)  →  runs pods/containers
```

---

## vCPU — per node vs total

When you pick a VM size (e.g. `Standard_DC2as_v5`), **2 vCPU** means **2 cores on that one VM** — not the whole cluster.

Total vCPUs Azure uses:

```text
Total vCPUs = Node count × vCPUs per node
```

| Node count | VM size (vCPU) | Total vCPUs |
|------------|----------------|-------------|
| 1 | 2 vCPU | **2** |
| 2 | 2 vCPU | **4** |
| 3 | 2 vCPU | **6** |

**Demo recommendation:** **1 node** + **2 vCPU VM** (e.g. DC2as_v5, B2s, or DS2_v2).

---

## Node count vs pods

| Term | Meaning |
|------|---------|
| **Node** | 1 VM in the cluster |
| **Pod** | Smallest unit Kubernetes runs (usually 1 container) |
| **Container** | Your app (`saiapp-demo`) |

For this demo you only need:

```text
1 node  →  1 pod  →  1 container
```

**Max pods / node** (e.g. 110) is a limit per VM — you won't use anywhere near that for a small demo.

---

## Scale method

| Method | Demo use |
|--------|----------|
| **Manual, 1 node** | ✅ Best — cheap, simple |
| **Autoscale 2–5** | Runs 2+ VMs always — more cost, not needed for learning |

---

# After AKS Is Created — Commands

Run these once the cluster shows **Succeeded** in the portal.

```text
AKS created  →  connect kubectl  →  verify ACR  →  deploy  →  expose  →  test
```

---

## 1. Connect kubectl to AKS

```powershell
az aks get-credentials --resource-group sai-app-rg --name sai-app-aks --overwrite-existing
kubectl get nodes
```

Expected: 1 node with status **Ready**.

---

## 2. Verify AKS can pull from ACR

```powershell
az aks check-acr --resource-group sai-app-rg --name sai-app-aks --acr sainathreddycontainer
```

Expected:

```text
Your cluster can pull images from sainathreddycontainer.azurecr.io!
```

If not attached during create:

```powershell
az aks update --resource-group sai-app-rg --name sai-app-aks --attach-acr sainathreddycontainer
```

---

## 3. Deploy app from ACR

```powershell
kubectl create deployment saiapp --image=sainathreddycontainer.azurecr.io/saiapp-demo:latest
```

Verify:

```powershell
kubectl get deployments
kubectl get pods
```

Wait until pod status is **Running**.

Check logs (optional):

```powershell
kubectl logs <pod-name>
```

---

## 4. Expose app with Load Balancer

App listens on port **8000** inside the container:

```powershell
kubectl expose deployment saiapp --type=LoadBalancer --port=80 --target-port=8000
```

Get public IP:

```powershell
kubectl get svc
```

Wait until **EXTERNAL-IP** shows an IP (not `<pending>`).

---

## 5. Test in browser

```text
http://<EXTERNAL-IP>/
http://<EXTERNAL-IP>/data
```

---

## Full Command Block (copy-paste)

```powershell
az aks get-credentials --resource-group sai-app-rg --name sai-app-aks --overwrite-existing
kubectl get nodes

az aks check-acr --resource-group sai-app-rg --name sai-app-aks --acr sainathreddycontainer

kubectl create deployment saiapp --image=sainathreddycontainer.azurecr.io/saiapp-demo:latest
kubectl get pods

kubectl expose deployment saiapp --type=LoadBalancer --port=80 --target-port=8000
kubectl get svc
```

---

# Working Steps — Verified (Use This)

Complete flow that was tested and works. Copy commands in order.

```text
AKS Succeeded  →  connect kubectl  →  check ACR  →  deploy  →  expose  →  get IP  →  test browser
```

---

## Your live resources

| Resource | Name / value |
|----------|--------------|
| Resource group | `sai-app-rg` |
| AKS cluster | `sai-app-aks` |
| ACR (use this one) | `sainathreddycontainer.azurecr.io` |
| Image | `saiapp-demo:latest` |
| Deployment name | `saiapp` |
| App port (inside container) | `8000` |
| Public port (Load Balancer) | `80` |

> Use **`sainathreddycontainer`** only for this project.  
> `sainathcontainer` is a different/old registry — ignore it.

---

## Step 1 — Connect PC to AKS

```powershell
az aks get-credentials --resource-group sai-app-rg --name sai-app-aks --overwrite-existing
kubectl get nodes
```

**What it does:** Downloads cluster login info so `kubectl` talks to your AKS cluster.

**Expected:**

```text
NAME                                STATUS   ROLES   AGE   VERSION
aks-nodepool1-xxxxxxxx-vmss000000   Ready    agent   ...   v1.xx.x
```

---

## Step 2 — Verify ACR access

```powershell
az aks check-acr --resource-group sai-app-rg --name sai-app-aks --acr sainathreddycontainer
```

**What it does:** Confirms AKS can pull images from your registry.

**Expected:**

```text
Your cluster can pull images from sainathreddycontainer.azurecr.io!
```

**If attach fails with Owner error:**

```text
Could not create a role assignment for ACR. Are you an Owner on this subscription?
```

- Common on student / $200 credit accounts (Contributor only).
- **Portal fix:** AKS → **Container registries** → both may already show as attached.
- If `check-acr` succeeds, skip `az aks update --attach-acr` and go to deploy.
- If pod gets `ImagePullBackOff`, use image pull secret (see Troubleshooting below).

**Attach via CLI (needs Owner role):**

```powershell
az aks update --resource-group sai-app-rg --name sai-app-aks --attach-acr sainathreddycontainer
```

---

## Step 3 — Check cluster is empty (optional)

```powershell
kubectl get deployments
kubectl get svc
```

Before deploy you may see:

```text
No resources found in default namespace.
```

Only default `kubernetes` service — normal.

---

## Step 4 — Deploy container from ACR

```powershell
kubectl create deployment saiapp --image=sainathreddycontainer.azurecr.io/saiapp-demo:latest
```

**What it does:**

| Part | Meaning |
|------|---------|
| `kubectl create deployment` | Tell Kubernetes to run your app |
| `saiapp` | Deployment name (you choose) |
| `--image=...` | Full ACR image path |

```text
sainathreddycontainer.azurecr.io / saiapp-demo : latest
         registry                    image name    tag
```

**Same as local `docker run`**, but AKS manages the pod (restart if crash).

**Verify:**

```powershell
kubectl get deployments
kubectl get pods
```

**Expected:**

```text
NAME     READY   STATUS    RESTARTS   AGE
saiapp   1/1     Running   0          59s
```

**What got created:**

```text
Deployment saiapp  →  ReplicaSet  →  Pod  →  Container (saiapp-demo)
```

---

## Step 5 — Expose app publicly (Load Balancer)

App runs on port **8000** inside the container. Load Balancer maps public port **80** → **8000**.

```powershell
kubectl expose deployment saiapp --type=LoadBalancer --port=80 --target-port=8000
```

**What it does:**

| Flag | Meaning |
|------|---------|
| `--type=LoadBalancer` | Azure creates a public IP |
| `--port=80` | Browser hits port 80 |
| `--target-port=8000` | Forwards to app inside pod |

**Expected:**

```text
service/saiapp exposed
```

---

## Step 6 — Get public IP

```powershell
kubectl get svc
```

First time **EXTERNAL-IP** may show `<pending>` — wait 1–3 minutes.

**Watch until IP appears:**

```powershell
kubectl get svc -w
```

Press `Ctrl+C` to stop watching.

**Expected:**

```text
NAME     TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)        AGE
saiapp   LoadBalancer   10.0.178.87    20.246.129.161   80:30507/TCP   59s
kubernetes   ClusterIP  10.0.0.1       <none>           443/TCP        ...
```

Your public IP will differ — use whatever `kubectl get svc` shows.

---

## Step 7 — Test in browser

```text
http://<EXTERNAL-IP>/
http://<EXTERNAL-IP>/data
```

**Example (your successful run):**

```text
http://20.246.129.161/
http://20.246.129.161/data
```

**Expected `/`:** `{"status":"ok","service":"saiapp-demo"}`

**Expected `/data`:** JSON fetched from jsonplaceholder API.

---

## Step 8 — Check logs (optional)

```powershell
kubectl logs <pod-name>
```

**Example:**

```powershell
kubectl logs saiapp-85948c9f6f-hnqw9
```

**Expected:**

```text
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     10.x.x.x:xxxxx - "GET / HTTP/1.1" 200 OK
INFO:     10.x.x.x:xxxxx - "GET /data HTTP/1.1" 200 OK
```

Get pod name anytime:

```powershell
kubectl get pods
```

---

## Full working command block (copy-paste)

```powershell
# 1. Connect
az aks get-credentials --resource-group sai-app-rg --name sai-app-aks --overwrite-existing
kubectl get nodes

# 2. Verify ACR
az aks check-acr --resource-group sai-app-rg --name sai-app-aks --acr sainathreddycontainer

# 3. Deploy
kubectl create deployment saiapp --image=sainathreddycontainer.azurecr.io/saiapp-demo:latest
kubectl get pods

# 4. Expose
kubectl expose deployment saiapp --type=LoadBalancer --port=80 --target-port=8000
kubectl get svc -w

# 5. Logs (replace pod name)
kubectl logs <pod-name>
```

---

## Useful commands after deploy

| Command | What it does |
|---------|--------------|
| `kubectl get deployments` | Show deployment status |
| `kubectl get pods` | Show running pods |
| `kubectl get svc` | Show services + public IP |
| `kubectl logs <pod-name>` | App logs |
| `kubectl describe pod <pod-name>` | Debug pod issues |

---

## Troubleshooting

### Pod status `ImagePullBackOff`

ACR pull failed. Create secret with ACR admin password:

```powershell
kubectl create secret docker-registry acr-secret `
  --docker-server=sainathreddycontainer.azurecr.io `
  --docker-username=sainathreddycontainer `
  --docker-password=YOUR_PASSWORD

kubectl patch serviceaccount default -p '{\"imagePullSecrets\": [{\"name\": \"acr-secret\"}]}'

kubectl delete deployment saiapp
kubectl create deployment saiapp --image=sainathreddycontainer.azurecr.io/saiapp-demo:latest
```

Password from: ACR → **Access keys** → Admin user.

### EXTERNAL-IP stuck on `<pending>`

Wait 2–5 minutes, run `kubectl get svc` again. Azure is creating the Load Balancer.

### Redeploy after code change

```powershell
# Rebuild + push new image to ACR first, then:
kubectl rollout restart deployment saiapp
```

---

## End-to-end flow (what you built)

```text
main.py (local)
    ↓  uv + Docker
saiapp-demo image (local)
    ↓  docker push
sainathreddycontainer.azurecr.io/saiapp-demo:latest (ACR)
    ↓  kubectl create deployment
Pod Running on AKS node
    ↓  kubectl expose LoadBalancer
http://<EXTERNAL-IP>/data (public URL) ✅
```

---

## Delete everything when demo is done (save credits)

```powershell
az group delete --name sai-app-rg --yes --no-wait
```

Removes AKS, ACR, and all resources in the resource group.



