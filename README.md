# AI Model Deployment Pipeline

A DevOps + AI project that deploys a Hugging Face sentiment-analysis model as a production-style
service using **FastAPI**, **Docker**, **Kubernetes**, and **CI/CD** (both **GitHub Actions** and
**Jenkins** pipelines are included).

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Prerequisites](#prerequisites)
5. [Running Locally (No Docker)](#running-locally-no-docker)
6. [Running with Docker](#running-with-docker)
7. [Deploying to Kubernetes](#deploying-to-kubernetes)
8. [CI/CD Option A: GitHub Actions](#cicd-option-a-github-actions)
9. [CI/CD Option B: Jenkins](#cicd-option-b-jenkins)
10. [API Reference](#api-reference)
11. [Health Checks](#health-checks)
12. [Troubleshooting](#troubleshooting)
13. [Future Roadmap](#future-roadmap)

---

## Overview

This project wraps a pre-trained Hugging Face model (`distilbert-base-uncased-finetuned-sst-2-english`)
in a REST API and deploys it the way a real production ML service would be deployed:

- **FastAPI** serves predictions over HTTP
- **Docker** packages the app so it runs identically anywhere
- **Kubernetes** keeps multiple replicas running and healthy
- **CI/CD** automatically builds and publishes a new image on every code change

Two CI/CD options are included so you can demonstrate either tool depending on what a company uses:
GitHub Actions (cloud-native, common in modern startups) or Jenkins (widely used in enterprises).

---

## Architecture

```
                 ┌────────────────────┐
   Client  ───▶  │   FastAPI Service   │  ───▶  Hugging Face Model  ───▶  JSON Response
                 │   (/predict, /health)│
                 └────────────────────┘
                          │
                    Docker Image
                          │
        ┌─────────────────────────────────┐
        │      Kubernetes Cluster          │
        │  Deployment (2 replicas)         │
        │  Service (stable network entry)  │
        └─────────────────────────────────┘
                          ▲
                          │
        ┌─────────────────────────────────┐
        │   CI/CD (GitHub Actions OR       │
        │   Jenkins) — build & push image  │
        │   automatically on every push    │
        └─────────────────────────────────┘
```

---

## Project Structure

```
ai-model-deploy/
├── main.py                          # FastAPI app + Hugging Face model
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Container build instructions
├── .dockerignore
├── k8s/
│   ├── deployment.yaml              # Kubernetes Deployment (2 replicas, health probes)
│   └── service.yaml                 # Kubernetes Service (stable network endpoint)
├── .github/workflows/
│   └── docker-build.yml             # GitHub Actions CI/CD pipeline
├── Jenkinsfile                      # Jenkins CI/CD pipeline (alternative to GitHub Actions)
└── README.md
```

---

## Prerequisites

| Tool | Needed for |
|---|---|
| Python 3.10+ | Running locally without Docker |
| Docker | Building/running the container |
| Minikube or Kind | Local Kubernetes cluster |
| kubectl | Talking to the Kubernetes cluster |
| A Docker Hub account | Pushing images from CI/CD |
| Jenkins (optional) | If using the Jenkins pipeline instead of GitHub Actions |

---

## Running Locally (No Docker)

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://localhost:8000/docs` for the interactive Swagger UI to test the API directly in your browser.

---

## Running with Docker

```bash
# Build the image
docker build -t ai-model-deploy:latest .

# Run the container
docker run -p 8000:8000 ai-model-deploy:latest
```

Visit `http://localhost:8000/docs` to test it.

---

## Deploying to Kubernetes

```bash
# Start a local cluster
minikube start

# Make Docker build directly into Minikube's environment
eval $(minikube docker-env)
docker build -t ai-model-deploy:latest .

# Apply the manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check that pods are running
kubectl get pods

# Forward a local port to access the service
kubectl port-forward service/ai-model-deploy-service 8000:80
```

Now `http://localhost:8000/docs` works exactly as before, but it's being served by Kubernetes.

---

## CI/CD Option A: GitHub Actions

File: `.github/workflows/docker-build.yml`

**What it does:** On every push to `main`, it builds a new Docker image and pushes it to Docker Hub.

**Setup:**
1. Go to your GitHub repo → **Settings → Secrets and variables → Actions**
2. Add two repository secrets:
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN` (create this from Docker Hub → Account Settings → Security)
3. Push any change to `main` — the workflow runs automatically. Check progress under the **Actions** tab.

---

## CI/CD Option B: Jenkins

File: `Jenkinsfile`

**What it does:** Checks out the code, builds the Docker image, logs in to Docker Hub, pushes the
image, and deploys the updated manifests to Kubernetes — all in one pipeline.

**Setup:**
1. Install Jenkins and the **Docker Pipeline** plugin.
2. In Jenkins, go to **Manage Jenkins → Credentials** and add your Docker Hub username/password
   as a credential with the ID `dockerhub-credentials` (this ID must match the `Jenkinsfile`).
3. Create a new **Pipeline** job in Jenkins, point it to this repository, and set the pipeline
   script path to `Jenkinsfile`.
4. Run the job (or connect a webhook from GitHub so it runs automatically on every push).

**Jenkins vs GitHub Actions — which to use:**

| | GitHub Actions | Jenkins |
|---|---|---|
| Setup | Zero infrastructure — runs on GitHub's servers | Needs a Jenkins server (self-hosted or cloud) |
| Best for | Personal projects, startups, cloud-native teams | Enterprises, on-premise infrastructure, complex pipelines |
| Config | YAML in the repo | Groovy `Jenkinsfile` in the repo |

You only need one for this project to work — both are included so you can demo whichever is more
relevant to the company or client you're presenting to.

---

## API Reference

### `GET /`
Returns a simple status message confirming the service is running.

### `GET /health`
Used by Kubernetes readiness/liveness probes to confirm the app is alive.

```json
{ "status": "ok" }
```

### `POST /predict`
**Request body:**
```json
{ "text": "I love working on DevOps projects!" }
```

**Response:**
```json
{ "label": "POSITIVE", "score": 0.9998 }
```

Test with curl:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"text": "I love working on DevOps projects!"}'
```

---

## Health Checks

Kubernetes uses the `/health` endpoint in two ways (configured in `k8s/deployment.yaml`):

- **Readiness probe** — decides if a pod should receive traffic
- **Liveness probe** — decides if a pod needs to be restarted

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---|---|---|
| `ImagePullBackOff` in Kubernetes | Image not built inside Minikube's Docker env | Run `eval $(minikube docker-env)` before building |
| Model download is slow on first build | Hugging Face model weights are large | Be patient on first `docker build`; it's cached after |
| Jenkins push fails with auth error | Credential ID mismatch | Confirm Jenkins credential ID is exactly `dockerhub-credentials` |
| Port already in use | Another process on port 8000 | Change the `-p` port mapping, e.g. `-p 8080:8000` |

---

## Future Roadmap

- [ ] Support multiple selectable Hugging Face models
- [ ] Add Horizontal Pod Autoscaler (HPA) for automatic scaling under load
- [ ] Integrate Prometheus + Grafana for monitoring dashboards
- [ ] Deploy to a free-tier cloud platform (Render/Railway) for a public live demo link
