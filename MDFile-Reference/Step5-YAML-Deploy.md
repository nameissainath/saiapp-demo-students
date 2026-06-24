# Step 5 — Deploy with Kubernetes YAML

Reference for deploying the SaiApp demo using **`k8s/deployment.yaml`** and **`k8s/service.yaml`** instead of manual `kubectl create` commands.

> **Step 6:** CI/CD with GitHub Actions — see **`Step6-CICD.md`**

---

## Remember this (read this first)

**Two YAML files = two Step 4 commands. Nothing extra.**

```text
deployment.yaml  =  DEPLOY   (run your container on AKS)
service.yaml     =  EXPOSE  (give it a public URL / IP)
```

| YAML file | Same as Step 4 command | What it does in one line |
|-----------|----------------------|-------------------------|
| **`k8s/deployment.yaml`** | `kubectl create deployment saiapp --image=...` | Pull image from ACR → start pod → run FastAPI |
| **`k8s/service.yaml`** | `kubectl expose deployment saiapp --type=LoadBalancer --port=80 --target-port=8000` | Azure public IP → port 80 → your app on 8000 |

**Apply both at once:**

```powershell
kubectl apply -f k8s/
```

That runs **deploy + expose** together — same end result as Step 4, but saved in files.

**Mnemonic:**

```text
Deployment  →  "deploy the app"     →  deployment.yaml
Service     →  "serve it publicly"  →  service.yaml
```

---

## Goal

```text
Manual kubectl commands  →  YAML files in repo  →  kubectl apply
```

Same app on AKS, but config is saved in code and ready for CI/CD.

---

## Why YAML instead of typing commands?

| Manual commands (Step 4) | YAML files (Step 5) |
|------------------------|-------------------|
| Lost when terminal closes | Saved in git forever |
| Hard to repeat exactly | Same config every time |
| No change history | See who changed what in GitHub |
| CI/CD cannot use them | Step 6 runs `kubectl apply -f k8s/` automatically |

YAML = **config recipe** for Kubernetes. You write it once, apply many times.

---

## Prerequisites

| Done in | What |
|---------|------|
| Step 1–3 | App, Docker, image in ACR |
| Step 4 | AKS running, manual deploy tested |

Connect to cluster:

```powershell
az aks get-credentials --resource-group sai-app-rg --name sai-app-aks --overwrite-existing
kubectl get nodes
```

Image must exist in ACR:

```powershell
az acr repository list --name sainathreddycontainer --output table
```

---

## Files in this project

```text
k8s/
  deployment.yaml   →  DEPLOY  (run container from ACR)
  service.yaml      →  EXPOSE (public Load Balancer)
```

---

# Part A — deployment.yaml (= DEPLOY)

**Step 4 command it replaces:**

```powershell
kubectl create deployment saiapp --image=sainathreddycontainer.azurecr.io/saiapp-demo:latest
```

**Full file (`k8s/deployment.yaml`):**

```yaml
apiVersion: apps/v1
kind: Deployment          # "run and keep my app alive"

metadata:
  name: saiapp           # deployment name in cluster

spec:
  replicas: 1            # how many pods (1 = one copy; change to 2 to scale)

  selector:
    matchLabels:
      app: saiapp        # deployment manages pods labeled app=saiapp

  template:              # blueprint for each pod
    metadata:
      labels:
        app: saiapp      # must match selector above

    spec:
      containers:
      - name: saiapp
        image: sainathreddycontainer.azurecr.io/saiapp-demo:latest
        ports:
        - containerPort: 8000
        imagePullPolicy: Always   # always pull latest from ACR on deploy
```

**Field cheat sheet:**

| Field | Value | Remember as |
|-------|-------|-------------|
| `kind: Deployment` | — | "Run my app" |
| `replicas: 1` | 1 pod | Change to `2` for scale demo |
| `image: ...` | ACR image | Same image you pushed in Step 3 |
| `containerPort: 8000` | FastAPI port | Inside the container only |
| `imagePullPolicy: Always` | Always pull | Gets new image after rebuild + push |

**What happens when you apply:**

```text
kubectl apply -f k8s/deployment.yaml
        ↓
AKS pulls saiapp-demo:latest from ACR
        ↓
Pod starts → container runs → Uvicorn on port 8000
```

App is running **inside cluster only** — not public yet until you apply `service.yaml`.

---

# Part B — service.yaml (= EXPOSE)

**Step 4 command it replaces:**

```powershell
kubectl expose deployment saiapp --type=LoadBalancer --port=80 --target-port=8000
```

**Full file (`k8s/service.yaml`):**

```yaml
apiVersion: v1
kind: Service            # "route traffic to my app"

metadata:
  name: saiapp

spec:
  selector:
    app: saiapp           # send traffic to pods with this label (must match deployment)

  type: LoadBalancer      # Azure creates public IP

  ports:
  - protocol: TCP
    port: 80              # what users hit in browser
    targetPort: 8000      # forwards to app inside pod
```

**Field cheat sheet:**

| Field | Value | Remember as |
|-------|-------|-------------|
| `kind: Service` | — | "Expose my app" |
| `type: LoadBalancer` | Public IP | Same as `kubectl expose ... LoadBalancer` |
| `port: 80` | Browser port | `http://<IP>/` uses port 80 |
| `targetPort: 8000` | App port | Where FastAPI listens |
| `selector.app: saiapp` | Must match deployment | Links service → pods |

**Traffic flow (after both files applied):**

```text
Browser  →  http://20.x.x.x/     (port 80)
                ↓
           Service (LoadBalancer)
                ↓
           Pod → container port 8000
                ↓
           FastAPI (/ and /data)
```

---

## Side-by-side: Step 4 vs Step 5

| What you want | Step 4 (manual) | Step 5 (YAML) |
|---------------|-----------------|---------------|
| Run container | `kubectl create deployment ...` | `k8s/deployment.yaml` |
| Public URL | `kubectl expose ... LoadBalancer` | `k8s/service.yaml` |
| Do both | Two separate commands | `kubectl apply -f k8s/` |

---

## Deploy with YAML

From project root:

```powershell
cd c:\Users\saina\OneDrive\Desktop\SaiApp
kubectl apply -f k8s/
```

Or apply files separately:

```powershell
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

---

## Verify

```powershell
kubectl get deployments
kubectl get pods
kubectl get svc
```

Expected:

```text
deployment/saiapp   1/1
pod/saiapp-xxxxx    Running
service/saiapp      LoadBalancer   ...   <EXTERNAL-IP>   80:xxxxx/TCP
```

Wait for **EXTERNAL-IP** if `<pending>`:

```powershell
kubectl get svc -w
```

Test in browser:

```text
http://<EXTERNAL-IP>/
http://<EXTERNAL-IP>/data
```

---

## If You Already Deployed Manually (Step 4)

Delete old resources first to avoid conflicts:

```powershell
kubectl delete deployment saiapp
kubectl delete service saiapp
```

Then apply YAML:

```powershell
kubectl apply -f k8s/
```

Or `kubectl apply` will **update** existing resources if names match — usually fine.

---

## Update After Code Change

1. Rebuild and push image to ACR:

```powershell
docker build -t saiapp-demo .
docker tag saiapp-demo sainathreddycontainer.azurecr.io/saiapp-demo:latest
docker push sainathreddycontainer.azurecr.io/saiapp-demo:latest
```

2. Restart deployment (pulls new image because `imagePullPolicy: Always`):

```powershell
kubectl rollout restart deployment/saiapp
kubectl rollout status deployment/saiapp
kubectl get pods
```

---

## Scale to 2 Replicas (optional)

Edit `k8s/deployment.yaml`:

```yaml
replicas: 2
```

Apply:

```powershell
kubectl apply -f k8s/deployment.yaml
kubectl get pods
```

Or without editing file:

```powershell
kubectl scale deployment saiapp --replicas=2
```

---

## Useful Commands

| Command | Meaning |
|---------|---------|
| `kubectl apply -f k8s/` | Create/update from YAML |
| `kubectl get deployments` | Deployment status |
| `kubectl get pods` | Running pods |
| `kubectl get svc` | Service + public IP |
| `kubectl describe deployment saiapp` | Debug deployment |
| `kubectl logs <pod-name>` | App logs |
| `kubectl rollout restart deployment/saiapp` | Redeploy after new image |
| `kubectl delete -f k8s/` | Remove deployment + service |

---

## Manual vs YAML

| | Step 4 (manual) | Step 5 (YAML) |
|---|-----------------|---------------|
| Deploy | `kubectl create deployment ...` | `kubectl apply -f k8s/deployment.yaml` |
| Expose | `kubectl expose ...` | `kubectl apply -f k8s/service.yaml` |
| Saved in git | No | Yes |
| CI/CD ready | No | Yes (Step 6) |

---

## Full Command Block (copy-paste)

```powershell
az aks get-credentials --resource-group sai-app-rg --name sai-app-aks --overwrite-existing

kubectl apply -f k8s/

kubectl get deployments
kubectl get pods
kubectl get svc -w
```

---

## What's Next

- **Step 6:** CI/CD — see **`Step6-CICD.md`**

- Create `.github/workflows/deploy.yml`
- Add GitHub secrets (Azure, ACR, AKS)
- Auto build + push + `kubectl apply` on every git push
