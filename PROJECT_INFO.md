# 🧮 Kubernetes Calculator - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [Prerequisites](#prerequisites)
5. [Step-by-Step Deployment Guide](#step-by-step-deployment-guide)
6. [Issues Faced and Solutions](#issues-faced-and-solutions)
7. [Testing and Verification](#testing-and-verification)
8. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Project Name**: Kubernetes Calculator Application  
**Purpose**: A full-featured calculator web application demonstrating microservices architecture deployed on Kubernetes

**Features**:
- ✅ Addition, Subtraction, Multiplication, and Division operations
- ✅ RESTful API backend using Flask
- ✅ Responsive web frontend using HTML/CSS/JavaScript
- ✅ Containerized with Docker
- ✅ Orchestrated with Kubernetes
- ✅ Deployed on AWS EC2 cluster

---

## Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    AWS Cloud Environment                     │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Kubernetes Cluster                                    │ │
│  │                                                        │ │
│  │  Master Node: 172.31.44.115                           │ │
│  │  ┌──────────────────────────────────────────────┐    │ │
│  │  │  Control Plane (kubectl, kube-apiserver)     │    │ │
│  │  └──────────────────────────────────────────────┘    │ │
│  │                                                        │ │
│  │  Worker Node 1: 172.31.32.128                         │ │
│  │  Worker Node 2: 172.31.34.134 (Public: 3.110.197.69) │ │
│  │  ┌──────────────────────────────────────────────┐    │ │
│  │  │                                              │    │ │
│  │  │  Namespace: calculator-app                   │    │ │
│  │  │  ┌──────────────────────────────────────┐   │    │ │
│  │  │  │  Frontend Pod                        │   │    │ │
│  │  │  │  - Nginx Container (port 80)         │   │    │ │
│  │  │  │  - Image: k8s-calculator-frontend:v2 │   │    │ │
│  │  │  │  - NodePort: 30007                   │   │    │ │
│  │  │  └──────────────────────────────────────┘   │    │ │
│  │  │                    ↓                         │    │ │
│  │  │              HTTP Requests                   │    │ │
│  │  │                    ↓                         │    │ │
│  │  │  ┌──────────────────────────────────────┐   │    │ │
│  │  │  │  Backend Pod                         │   │    │ │
│  │  │  │  - Flask Container (port 5000)       │   │    │ │
│  │  │  │  - Image: calculator-backend:v2      │   │    │ │
│  │  │  │  - ClusterIP: Internal (5000)        │   │    │ │
│  │  │  │  - NodePort: 30008 (External)        │   │    │ │
│  │  │  └──────────────────────────────────────┘   │    │ │
│  │  │                                              │    │ │
│  │  └──────────────────────────────────────────────┘    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
         ↑
         │ (Port 30007 & 30008)
         │
   User Browser Access
   http://3.110.197.69:30007
```

### Component Breakdown

**Frontend Service**:
- **Container**: Nginx serving static HTML/CSS/JS
- **Internal Port**: 80
- **External Port**: NodePort 30007
- **Purpose**: User interface for calculator operations

**Backend Service**:
- **Container**: Flask REST API application
- **Internal Port**: 5000
- **External Ports**: 
  - ClusterIP 5000 (internal cluster communication)
  - NodePort 30008 (direct browser access)
- **Purpose**: Process calculation requests

**Communication Flow**:
1. User accesses frontend via `http://3.110.197.69:30007`
2. Frontend JavaScript sends POST requests to `http://3.110.197.69:30008/calculate`
3. Backend processes calculation and returns JSON response
4. Frontend displays result to user

---

## Technology Stack

### Backend
- **Language**: Python 3.9
- **Framework**: Flask 2.3.0
- **CORS Handling**: flask-cors 4.0.0
- **Base Image**: python:3.9-slim

### Frontend
- **Web Server**: Nginx (alpine variant)
- **Languages**: HTML5, CSS3, JavaScript (ES6)
- **Base Image**: nginx:alpine

### Infrastructure
- **Container Platform**: Docker
- **Orchestration**: Kubernetes
- **Cloud Provider**: AWS EC2
- **Container Registry**: Docker Hub (bharathadalla)
- **Cluster Setup**: 1 Master + 2 Worker Nodes

### Networking
- **Namespace**: calculator-app
- **Service Types**: ClusterIP (internal), NodePort (external)
- **Frontend Port**: 30007
- **Backend Port**: 30008

---

## Prerequisites

Before starting deployment, ensure you have:

1. **AWS EC2 Instances**:
   - 1 Master node (t2.medium or higher recommended)
   - 2 Worker nodes (t2.micro minimum)
   - Ubuntu 20.04+ or Amazon Linux 2

2. **Software Installed on All Nodes**:
   - Docker (version 20.10+)
   - Kubernetes (kubeadm, kubelet, kubectl)
   - Container runtime (containerd or Docker)

3. **Network Configuration**:
   - All nodes in same VPC
   - Security group allowing:
     - Port 6443 (Kubernetes API)
     - Port 30007-30008 (NodePorts)
     - Port 10250 (Kubelet API)
     - All traffic between nodes

4. **Local Development Machine**:
   - Docker installed
   - kubectl configured to access cluster
   - Docker Hub account credentials

---

## Step-by-Step Deployment Guide

### PHASE 1: Project Setup and Docker Image Creation

#### Step 1: Navigate to Project Directory
```bash
cd /home/test/k8practice
```
**Explanation**: Change to your project directory where backend/ and frontend/ folders exist.

---

#### Step 2: Review Backend Code Structure

**File**: `backend/app.py`
```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    num1 = float(data.get('num1', 0))
    num2 = float(data.get('num2', 0))
    operation = data.get('operation', '')
    
    if operation == 'add':
        result = num1 + num2
    elif operation == 'subtract':
        result = num1 - num2
    elif operation == 'multiply':
        result = num1 * num2
    elif operation == 'divide':
        if num2 == 0:
            return jsonify({"error": "Cannot divide by zero", "status": "error"}), 400
        result = num1 / num2
    
    return jsonify({"result": result, "status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

**File**: `backend/requirements.txt`
```
Flask==2.3.0
flask-cors==4.0.0
```

**File**: `backend/Dockerfile`
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
```

**Explanation**: 
- Flask app runs on port 5000
- CORS enabled for cross-origin requests from frontend
- Health endpoint for Kubernetes liveness probes
- Calculate endpoint supports 4 operations

---

#### Step 3: Review Frontend Code Structure

**File**: `frontend/index.html` (Key sections)
```javascript
async function calculate(operation) {
    const num1 = document.getElementById('num1').value;
    const num2 = document.getElementById('num2').value;
    
    const backendUrl = `http://${window.location.hostname}:30008/calculate`;
    
    const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            num1: parseFloat(num1), 
            num2: parseFloat(num2),
            operation: operation
        })
    });
    
    const data = await response.json();
    // Display result
}
```

**File**: `frontend/Dockerfile`
```dockerfile
FROM nginx:alpine
COPY index.html /usr/share/nginx/html/
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Explanation**:
- Frontend dynamically gets hostname (works with any IP)
- Calls backend on port 30008
- Nginx serves static files on port 80

---

#### Step 4: Build Docker Images

```bash
# Build backend image
docker build -t bharathadalla/calculator-backend:v2 ./backend

# Build frontend image
docker build -t bharathadalla/k8s-calculator-frontend:v2 ./frontend
```

**Explanation**:
- Creates Docker images from Dockerfiles
- Tagged as v2 (version 2 with full calculator functionality)
- Images stored locally before pushing to registry

**Expected Output**:
```
Successfully built abc123def456
Successfully tagged bharathadalla/calculator-backend:v2
```

---

#### Step 5: Test Images Locally (Optional but Recommended)

```bash
# Test backend
docker run -d -p 5000:5000 --name test-backend bharathadalla/calculator-backend:v2

# Test backend health
curl http://localhost:5000/health
# Expected: {"status":"ok"}

# Test calculation
curl -X POST http://localhost:5000/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":10,"num2":5,"operation":"add"}'
# Expected: {"result":15.0,"status":"success","message":"10.0 + 5.0 = 15.0"}

# Clean up
docker stop test-backend && docker rm test-backend
```

**Explanation**: Verify images work correctly before pushing to registry and deploying to Kubernetes.

---

#### Step 6: Login to Docker Hub

```bash
docker login
# Enter username: bharathadalla
# Enter password: [your-docker-hub-password]
```

**Explanation**: Authenticate to Docker Hub to push images to your registry.

---

#### Step 7: Push Images to Docker Hub

```bash
# Push backend image
docker push bharathadalla/calculator-backend:v2

# Push frontend image
docker push bharathadalla/k8s-calculator-frontend:v2
```

**Explanation**: 
- Uploads images to Docker Hub registry
- Makes images accessible to Kubernetes cluster
- v2 tag allows version management

**Expected Output**:
```
The push refers to repository [docker.io/bharathadalla/calculator-backend]
v2: digest: sha256:abc123... size: 1234
```

---

### PHASE 2: Kubernetes Cluster Preparation

#### Step 8: Verify Cluster Status (On Master Node)

```bash
# SSH to master node
ssh -i your-key.pem ubuntu@172.31.44.115

# Check cluster nodes
kubectl get nodes

# Expected Output:
# NAME                STATUS   ROLES           AGE   VERSION
# ip-172-31-44-115    Ready    control-plane   10d   v1.28.0
# ip-172-31-32-128    Ready    <none>          10d   v1.28.0
# ip-172-31-34-134    Ready    <none>          10d   v1.28.0
```

**Explanation**: Confirms all 3 nodes (1 master + 2 workers) are Ready and connected to cluster.

---

#### Step 9: Check Available Resources

```bash
# Check node resources
kubectl top nodes

# Check existing namespaces and pods
kubectl get namespaces
kubectl get pods --all-namespaces

# Check available CPU and Memory
kubectl describe nodes | grep -A 5 "Allocated resources"
```

**Explanation**: 
- Ensures nodes have sufficient CPU/Memory
- Identifies potential resource conflicts
- Important: Our cluster had limited resources (this caused issues later)

---

#### Step 10: Copy Deployment File to Master Node

On your local machine:
```bash
# Copy k8s-deployment.yaml to master node
scp -i your-key.pem k8s-deployment.yaml ubuntu@172.31.44.115:/home/ubuntu/
```

**Explanation**: Transfers the Kubernetes manifest file from local machine to master node where kubectl can apply it.

---

### PHASE 3: Kubernetes Deployment

#### Step 11: Review Deployment Manifest

**File**: `k8s-deployment.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: calculator-app
---
# BACKEND DEPLOYMENT
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
  namespace: calculator-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: python-backend
        image: bharathadalla/calculator-backend:v2 
        ports:
        - containerPort: 5000
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
---
# BACKEND SERVICE (INTERNAL)
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: calculator-app
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
---
# BACKEND SERVICE (EXTERNAL ACCESS)
apiVersion: v1
kind: Service
metadata:
  name: backend-service-nodeport
  namespace: calculator-app
spec:
  type: NodePort
  selector:
    app: backend
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
      nodePort: 30008
---
# FRONTEND DEPLOYMENT
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-deployment
  namespace: calculator-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: nginx-frontend
        image: bharathadalla/k8s-calculator-frontend:v2
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "16Mi"
            cpu: "25m"
          limits:
            memory: "32Mi"
            cpu: "50m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
---
# FRONTEND SERVICE
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: calculator-app
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
      nodePort: 30007
```

**Key Components Explained**:

1. **Namespace**: `calculator-app` - Isolates resources from other applications
2. **Replicas**: 1 each (reduced from 2 due to resource constraints - see Issues section)
3. **Resources**: 
   - Backend: 100m CPU, 64Mi memory (reduced - see Issues section)
   - Frontend: 25m CPU, 16Mi memory (reduced - see Issues section)
4. **NodePorts**: 
   - 30007 for frontend (user interface)
   - 30008 for backend (API endpoint)
5. **Liveness Probes**: Health checks to restart unhealthy containers

---

#### Step 12: Deploy to Kubernetes

```bash
# On master node
cd /home/ubuntu

# Apply the deployment
kubectl apply -f k8s-deployment.yaml
```

**Expected Output**:
```
namespace/calculator-app created
deployment.apps/backend-deployment created
service/backend-service created
service/backend-service-nodeport created
deployment.apps/frontend-deployment created
service/frontend-service created
```

**Explanation**: 
- Creates namespace first
- Deploys backend and frontend pods
- Creates ClusterIP service (internal) and NodePort services (external)
- Kubernetes schedules pods on worker nodes

---

#### Step 13: Monitor Pod Creation

```bash
# Watch pods being created
kubectl get pods -n calculator-app -w

# Wait until STATUS shows "Running" for both pods
# Press Ctrl+C to stop watching

# Check final status
kubectl get pods -n calculator-app -o wide
```

**Expected Output** (after successful deployment):
```
NAME                                   READY   STATUS    RESTARTS   AGE   IP           NODE
backend-deployment-xyz123              1/1     Running   0          2m    10.244.1.5   ip-172-31-32-128
frontend-deployment-abc456             1/1     Running   0          2m    10.244.2.3   ip-172-31-34-134
```

**Explanation**: 
- `-w` flag watches real-time status changes
- `-o wide` shows which worker node each pod is running on
- Both pods should show "Running" status

---

#### Step 14: Verify Services

```bash
# Check services
kubectl get services -n calculator-app

# Expected Output:
# NAME                       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
# backend-service            ClusterIP   10.96.100.50    <none>        5000/TCP         3m
# backend-service-nodeport   NodePort    10.96.100.51    <none>        5000:30008/TCP   3m
# frontend-service           NodePort    10.96.100.52    <none>        80:30007/TCP     3m
```

**Explanation**:
- ClusterIP service: Internal communication between pods
- NodePort services: External access via worker node IPs
- Port mappings: 5000→30008 (backend), 80→30007 (frontend)

---

### PHASE 4: Testing and Verification

#### Step 15: Test Backend Health Endpoint

```bash
# From master node - test using worker node private IP
curl http://172.31.34.134:30008/health

# Expected Output:
# {"status":"ok"}
```

**Explanation**: Verifies backend pod is running and responding to requests.

---

#### Step 16: Test Backend Calculate Endpoint

```bash
# Test addition
curl -X POST http://172.31.34.134:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":10,"num2":5,"operation":"add"}'

# Expected: {"result":15.0,"status":"success","message":"10.0 + 5.0 = 15.0"}

# Test subtraction
curl -X POST http://172.31.34.134:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":10,"num2":5,"operation":"subtract"}'

# Expected: {"result":5.0,"status":"success","message":"10.0 - 5.0 = 5.0"}

# Test multiplication
curl -X POST http://172.31.34.134:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":10,"num2":5,"operation":"multiply"}'

# Expected: {"result":50.0,"status":"success","message":"10.0 × 5.0 = 50.0"}

# Test division
curl -X POST http://172.31.34.134:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":10,"num2":5,"operation":"divide"}'

# Expected: {"result":2.0,"status":"success","message":"10.0 ÷ 5.0 = 2.0"}

# Test division by zero (error case)
curl -X POST http://172.31.34.134:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":10,"num2":0,"operation":"divide"}'

# Expected: {"error":"Cannot divide by zero","status":"error"}
```

**Explanation**: Tests all four calculator operations to ensure backend logic works correctly.

---

#### Step 17: Test Frontend HTML

```bash
# Get frontend HTML
curl http://172.31.34.134:30007 | head -30

# Expected: Should see HTML with calculator interface including:
# - Four operation buttons (Add, Subtract, Multiply, Divide)
# - Backend URL pointing to port 30008
# - JavaScript calculate function
```

**Explanation**: Verifies frontend is serving the correct updated HTML with full calculator functionality.

---

#### Step 18: Configure AWS Security Group for Public Access

**Option A: Via AWS Console**

1. Go to AWS EC2 Console
2. Select your worker node instance (172.31.34.134 / 3.110.197.69)
3. Click "Security" tab
4. Click on the Security Group name
5. Click "Edit inbound rules"
6. Add two new rules:
   ```
   Type: Custom TCP
   Port: 30007
   Source: 0.0.0.0/0
   Description: Frontend Calculator UI
   
   Type: Custom TCP
   Port: 30008
   Source: 0.0.0.0/0
   Description: Backend Calculator API
   ```
7. Click "Save rules"

**Option B: Via AWS CLI**

```bash
# Get your security group ID
aws ec2 describe-instances \
  --filters "Name=private-ip-address,Values=172.31.34.134" \
  --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
  --output text

# Let's say it returns: sg-0123456789abcdef0

# Add rule for frontend port 30007
aws ec2 authorize-security-group-ingress \
  --group-id sg-0123456789abcdef0 \
  --protocol tcp \
  --port 30007 \
  --cidr 0.0.0.0/0

# Add rule for backend port 30008
aws ec2 authorize-security-group-ingress \
  --group-id sg-0123456789abcdef0 \
  --protocol tcp \
  --port 30008 \
  --cidr 0.0.0.0/0
```

**Explanation**: 
- Opens firewall ports 30007 and 30008 on worker node
- Allows incoming traffic from any IP (0.0.0.0/0)
- Required for public internet access to application

---

#### Step 19: Test Public Access

```bash
# From your local machine or any internet-connected device

# Test frontend (open in web browser)
http://3.110.197.69:30007

# Test backend health (in terminal)
curl http://3.110.197.69:30008/health

# Test backend calculation (in terminal)
curl -X POST http://3.110.197.69:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":25,"num2":5,"operation":"multiply"}'

# Expected: {"result":125.0,"status":"success","message":"25.0 × 5.0 = 125.0"}
```

**Explanation**: 
- Uses public IP 3.110.197.69 to access application from internet
- Frontend should load in browser with calculator interface
- All operations (add, subtract, multiply, divide) should work

---

### PHASE 5: Monitoring and Management

#### Step 20: View Logs

```bash
# Get backend pod logs
kubectl logs -n calculator-app -l app=backend --tail=50

# Get frontend pod logs
kubectl logs -n calculator-app -l app=frontend --tail=50

# Follow logs in real-time
kubectl logs -n calculator-app -l app=backend -f
```

**Explanation**: 
- Shows application logs for debugging
- `-l app=backend` filters by label
- `--tail=50` shows last 50 lines
- `-f` follows logs in real-time (like tail -f)

---

#### Step 21: Check Resource Usage

```bash
# Check pod resource usage
kubectl top pods -n calculator-app

# Expected Output:
# NAME                                   CPU(cores)   MEMORY(bytes)
# backend-deployment-xyz123              2m           45Mi
# frontend-deployment-abc456             1m           8Mi
```

**Explanation**: Shows actual CPU and memory consumption of running pods.

---

#### Step 22: Describe Pods for Detailed Info

```bash
# Detailed backend pod information
kubectl describe pod -n calculator-app -l app=backend

# Detailed frontend pod information
kubectl describe pod -n calculator-app -l app=frontend
```

**Explanation**: 
- Shows pod events, status, resource limits
- Useful for troubleshooting startup or runtime issues

---

## Issues Faced and Solutions

### Issue #1: Frontend-Backend Connectivity Failure

**Problem**: Frontend could not reach backend, getting "Cannot reach backend" errors in browser console.

**Root Cause**: 
1. Port mismatch - Frontend was trying to connect to port 30006, but backend was on port 30002
2. Missing CORS configuration in Flask backend

**Symptoms**:
```javascript
// Browser console error:
❌ Error: Cannot reach backend at port 30006
CORS policy: No 'Access-Control-Allow-Origin' header
```

**Solution Steps**:

1. **Fixed CORS in Backend** (backend/app.py):
```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
```

2. **Updated Frontend to Use Correct Port** (frontend/index.html):
```javascript
// Old (wrong):
const backendUrl = `http://${window.location.hostname}:30006/add`;

// New (correct):
const backendUrl = `http://${window.location.hostname}:30008/calculate`;
```

3. **Rebuilt and Redeployed Docker Images**:
```bash
docker build -t bharathadalla/calculator-backend:v2 ./backend
docker build -t bharathadalla/k8s-calculator-frontend:v2 ./frontend
docker push bharathadalla/calculator-backend:v2
docker push bharathadalla/k8s-calculator-frontend:v2

kubectl delete namespace calculator-app
kubectl apply -f k8s-deployment.yaml
```

**Verification**:
```bash
# Test that CORS headers are present
curl -i http://172.31.34.134:30008/health
# Should see: Access-Control-Allow-Origin: *
```

---

### Issue #2: Port Conflicts (30001/30002 Already in Use)

**Problem**: Deployment failed with error: "provided port is already allocated"

**Root Cause**: Ports 30001 and 30002 were already used by another application on the cluster

**Symptoms**:
```bash
kubectl get events -n calculator-app
# Error: Port 30002 is already allocated
```

**Solution Steps**:

1. **Changed Ports to 30005/30006** (first attempt):
```yaml
# In k8s-deployment.yaml
nodePort: 30005  # frontend
nodePort: 30006  # backend
```

2. **Port 30006 Still Had Issues, Changed to 30007/30008** (final solution):
```yaml
# Final configuration in k8s-deployment.yaml
nodePort: 30007  # frontend (changed from 30005)
nodePort: 30008  # backend (changed from 30006)
```

3. **Updated Frontend Code to Match**:
```javascript
const backendUrl = `http://${window.location.hostname}:30008/calculate`;
```

4. **Redeployed**:
```bash
kubectl apply -f k8s-deployment.yaml
```

**Verification**:
```bash
# Check that ports are correctly assigned
kubectl get services -n calculator-app
# Should show: 80:30007/TCP and 5000:30008/TCP
```

---

### Issue #3: Pods Stuck in Pending State - Insufficient CPU

**Problem**: After deployment, 3 out of 4 pods remained in "Pending" status and never started.

**Root Cause**: Worker nodes had insufficient CPU resources to accommodate resource requests specified in deployment.

**Symptoms**:
```bash
kubectl get pods -n calculator-app
# NAME                                   READY   STATUS    RESTARTS   AGE
# backend-deployment-xyz123-1            1/1     Running   0          3m
# backend-deployment-xyz123-2            0/1     Pending   0          3m
# frontend-deployment-abc456-1           0/1     Pending   0          3m
# frontend-deployment-abc456-2           0/1     Pending   0          3m

kubectl describe pod frontend-deployment-abc456-1 -n calculator-app
# Events:
# Warning  FailedScheduling  2m   default-scheduler  0/2 nodes available: 
# 2 Insufficient cpu
```

**Detailed Analysis**:

Original resource requests were too high:
```yaml
# Original (too high for t2.micro workers):
backend:
  requests:
    memory: "128Mi"
    cpu: "200m"  # Too high!
    
frontend:
  requests:
    memory: "32Mi"
    cpu: "50m"   # Too high!
```

With 2 replicas each, total requests:
- Backend: 2 × 200m = 400m CPU
- Frontend: 2 × 50m = 100m CPU  
- **Total: 500m CPU** (half a CPU core)

T2.micro worker nodes only have ~900m allocatable CPU after system pods.

**Solution Steps**:

1. **Reduced Resource Requests**:
```yaml
# In k8s-deployment.yaml
backend:
  resources:
    requests:
      memory: "64Mi"   # Reduced from 128Mi
      cpu: "100m"      # Reduced from 200m (50% reduction)
    limits:
      memory: "128Mi"
      cpu: "250m"

frontend:
  resources:
    requests:
      memory: "16Mi"   # Reduced from 32Mi
      cpu: "25m"       # Reduced from 50m (50% reduction)
    limits:
      memory: "32Mi"
      cpu: "50m"
```

2. **Reduced Replicas from 2 to 1**:
```yaml
spec:
  replicas: 1  # Changed from 2
```

New total resource requests:
- Backend: 1 × 100m = 100m CPU
- Frontend: 1 × 25m = 25m CPU
- **Total: 125m CPU** (much more reasonable)

3. **Applied Changes**:
```bash
# Delete old deployment
kubectl delete namespace calculator-app

# Wait for cleanup
sleep 10

# Redeploy with new resource limits
kubectl apply -f k8s-deployment.yaml

# Monitor pod creation
kubectl get pods -n calculator-app -w
```

4. **Verified All Pods Running**:
```bash
kubectl get pods -n calculator-app
# NAME                                   READY   STATUS    RESTARTS   AGE
# backend-deployment-xyz123              1/1     Running   0          1m
# frontend-deployment-abc456             1/1     Running   0          1m
```

**Verification Commands**:
```bash
# Check resource allocation on nodes
kubectl describe nodes | grep -A 5 "Allocated resources"

# Check that pods are actually running
kubectl get pods -n calculator-app -o wide

# Verify CPU usage is within limits
kubectl top pods -n calculator-app
```

**Lessons Learned**:
- Always check available node resources before deployment
- Start with minimal resource requests and increase if needed
- Use `kubectl top nodes` to see available resources
- For production, use larger instance types or autoscaling

---

### Issue #4: Wrong Docker Image Version Deployed (v1 Instead of v2)

**Problem**: Application accessible via private IP but displayed OLD simple calculator (sum only) instead of FULL calculator (4 operations).

**Root Cause**: Kubernetes deployment was using old v1 images instead of newly built v2 images with full calculator functionality.

**Symptoms**:
```bash
curl http://172.31.34.134:30007
# HTML showed:
# - Simple "Add Two Numbers" calculator
# - Backend URL pointing to port 30006 (old port)
# - Only /add endpoint (missing /calculate)

# But new code has:
# - Full calculator with 4 operations (add, subtract, multiply, divide)
# - Backend URL pointing to port 30008
# - New /calculate endpoint
```

**Root Cause Analysis**:

Deployment manifest was referencing v1 images:
```yaml
# Wrong - old images:
image: bharathadalla/calculator-backend:v1 
image: bharathadalla/k8s-calculator-frontend:v1
```

But updated code existed in files, just not built into Docker images yet!

**Solution Steps**:

1. **Updated k8s-deployment.yaml to Reference v2 Images**:
```yaml
# Corrected:
image: bharathadalla/calculator-backend:v2
image: bharathadalla/k8s-calculator-frontend:v2
```

2. **Built v2 Docker Images with Updated Code**:
```bash
cd /home/test/k8practice

# Build new images with v2 tag
docker build -t bharathadalla/calculator-backend:v2 ./backend
docker build -t bharathadalla/k8s-calculator-frontend:v2 ./frontend

# Verify images exist locally
docker images | grep calculator
```

3. **Pushed v2 Images to Docker Hub**:
```bash
# Login to Docker Hub
docker login

# Push images
docker push bharathadalla/calculator-backend:v2
docker push bharathadalla/k8s-calculator-frontend:v2
```

4. **Redeployed to Kubernetes**:
```bash
# Delete old deployment
kubectl delete namespace calculator-app

# Wait for cleanup
sleep 10

# Deploy with v2 images
kubectl apply -f k8s-deployment.yaml

# Wait for pods to start
sleep 30

# Verify pods are running with new images
kubectl get pods -n calculator-app -o wide
```

5. **Verified v2 Images Deployed**:
```bash
# Check which image each pod is using
kubectl describe pod -n calculator-app -l app=backend | grep Image
# Should show: bharathadalla/calculator-backend:v2

kubectl describe pod -n calculator-app -l app=frontend | grep Image
# Should show: bharathadalla/k8s-calculator-frontend:v2
```

6. **Tested Full Calculator Functionality**:
```bash
# Test frontend shows 4 operation buttons
curl http://172.31.34.134:30007 | grep -E "(Add|Subtract|Multiply|Divide)"

# Test all backend operations
curl -X POST http://172.31.34.134:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":20,"num2":4,"operation":"divide"}'
# Expected: {"result":5.0,"status":"success","message":"20.0 ÷ 4.0 = 5.0"}
```

**Verification**:
```bash
# Frontend HTML should now show:
curl http://localhost:30007 | head -30
# ✅ Four buttons: Add, Subtract, Multiply, Divide
# ✅ Backend URL: port 30008 (not 30006)
# ✅ JavaScript calculate(operation) function
```

**Lessons Learned**:
- Always verify Docker image tags match deployment manifest
- Use version tags (v1, v2) instead of "latest" for better tracking
- Rebuild AND push images after code changes
- Check running pods to confirm correct image version deployed

---

### Issue #5: Public IP Access Blocked - Security Group Not Configured

**Problem**: Application accessible on private IP (172.31.34.134:30007) but NOT on public IP (3.110.197.69:30007).

**Root Cause**: AWS Security Group did not have inbound rules allowing traffic on ports 30007 and 30008.

**Symptoms**:
```bash
# Works (private IP):
curl http://172.31.34.134:30007
# Returns HTML

# Fails (public IP):
curl http://3.110.197.69:30007
# Timeout or connection refused
```

**Solution Steps**:

**Via AWS Console**:
1. Navigate to EC2 Dashboard
2. Select worker node instance (3.110.197.69)
3. Security tab → Click security group
4. Edit Inbound Rules → Add Rule:
   - Type: Custom TCP
   - Port: 30007
   - Source: 0.0.0.0/0 (or your IP for better security)
   - Description: Calculator Frontend
5. Add another rule:
   - Type: Custom TCP
   - Port: 30008
   - Source: 0.0.0.0/0
   - Description: Calculator Backend API
6. Save rules

**Via AWS CLI**:
```bash
# Get security group ID
SG_ID=$(aws ec2 describe-instances \
  --filters "Name=private-ip-address,Values=172.31.34.134" \
  --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' \
  --output text)

echo "Security Group ID: $SG_ID"

# Add rule for frontend port 30007
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 30007 \
  --cidr 0.0.0.0/0 \
  --description "Calculator Frontend UI"

# Add rule for backend port 30008
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 30008 \
  --cidr 0.0.0.0/0 \
  --description "Calculator Backend API"

# Verify rules added
aws ec2 describe-security-groups \
  --group-ids $SG_ID \
  --query 'SecurityGroups[0].IpPermissions[*].[FromPort,ToPort,IpProtocol,IpRanges[0].CidrIp]' \
  --output table
```

**Verification**:
```bash
# Test public IP access from any machine
curl http://3.110.197.69:30008/health
# Expected: {"status":"ok"}

# Test frontend in browser
Open: http://3.110.197.69:30007
# Should display calculator interface
```

**Security Best Practice** (Optional):
Instead of 0.0.0.0/0 (all IPs), restrict to specific IPs:
```bash
# Only allow your IP
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 30007 \
  --cidr YOUR_PUBLIC_IP/32

# Or allow a specific IP range
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 30007 \
  --cidr 203.0.113.0/24
```

---

## Testing and Verification

### Complete Test Checklist

#### ✅ Backend Health Check
```bash
curl http://3.110.197.69:30008/health
# Expected: {"status":"ok"}
```

#### ✅ Backend Calculate - Addition
```bash
curl -X POST http://3.110.197.69:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":100,"num2":50,"operation":"add"}'
# Expected: {"result":150.0,"status":"success","message":"100.0 + 50.0 = 150.0"}
```

#### ✅ Backend Calculate - Subtraction
```bash
curl -X POST http://3.110.197.69:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":100,"num2":50,"operation":"subtract"}'
# Expected: {"result":50.0,"status":"success","message":"100.0 - 50.0 = 50.0"}
```

#### ✅ Backend Calculate - Multiplication
```bash
curl -X POST http://3.110.197.69:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":12,"num2":8,"operation":"multiply"}'
# Expected: {"result":96.0,"status":"success","message":"12.0 × 8.0 = 96.0"}
```

#### ✅ Backend Calculate - Division
```bash
curl -X POST http://3.110.197.69:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":144,"num2":12,"operation":"divide"}'
# Expected: {"result":12.0,"status":"success","message":"144.0 ÷ 12.0 = 12.0"}
```

#### ✅ Backend Calculate - Division by Zero (Error Handling)
```bash
curl -X POST http://3.110.197.69:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1":10,"num2":0,"operation":"divide"}'
# Expected: {"error":"Cannot divide by zero","status":"error"}
```

#### ✅ Frontend UI Check
```bash
curl http://3.110.197.69:30007 | grep -E "(Add|Subtract|Multiply|Divide)"
# Should find all four operation buttons
```

#### ✅ End-to-End Browser Test
1. Open: http://3.110.197.69:30007
2. Enter: 25 and 5
3. Click "Add" → Should show: 25 + 5 = 30
4. Click "Subtract" → Should show: 25 - 5 = 20
5. Click "Multiply" → Should show: 25 × 5 = 125
6. Click "Divide" → Should show: 25 ÷ 5 = 5
7. Try divide by 0 → Should show error message

#### ✅ Pod Status Verification
```bash
kubectl get pods -n calculator-app
# Both pods should show "Running" status
```

#### ✅ Service Verification
```bash
kubectl get services -n calculator-app
# Should show NodePort services on 30007 and 30008
```

#### ✅ Logs Check (No Errors)
```bash
kubectl logs -n calculator-app -l app=backend --tail=20
kubectl logs -n calculator-app -l app=frontend --tail=20
# Should not show critical errors
```

---

## Troubleshooting

### Common Commands for Debugging

#### Check Pod Status and Events
```bash
# List all pods with status
kubectl get pods -n calculator-app

# Detailed pod information
kubectl describe pod -n calculator-app POD_NAME

# Check events for scheduling issues
kubectl get events -n calculator-app --sort-by='.lastTimestamp'
```

#### View Logs
```bash
# Backend logs
kubectl logs -n calculator-app -l app=backend

# Frontend logs
kubectl logs -n calculator-app -l app=frontend

# Follow logs in real-time
kubectl logs -n calculator-app -l app=backend -f

# Previous container logs (if pod restarted)
kubectl logs -n calculator-app POD_NAME --previous
```

#### Test Network Connectivity
```bash
# Test from within cluster (exec into a pod)
kubectl exec -it -n calculator-app POD_NAME -- /bin/sh

# Inside pod, test backend service
wget -O- http://backend-service:5000/health

# Test from master node
curl http://WORKER_NODE_IP:30008/health
curl http://WORKER_NODE_IP:30007
```

#### Check Resource Usage
```bash
# Node resources
kubectl top nodes

# Pod resources
kubectl top pods -n calculator-app

# Describe node for allocation details
kubectl describe node WORKER_NODE_NAME
```

#### Restart Pods
```bash
# Delete pod (will be recreated automatically)
kubectl delete pod -n calculator-app POD_NAME

# Or rollout restart deployment
kubectl rollout restart deployment backend-deployment -n calculator-app
kubectl rollout restart deployment frontend-deployment -n calculator-app
```

#### Clean and Redeploy
```bash
# Complete cleanup
kubectl delete namespace calculator-app

# Wait for cleanup
sleep 10

# Redeploy
kubectl apply -f k8s-deployment.yaml

# Watch deployment
watch kubectl get pods -n calculator-app
```

---

## Quick Reference

### Important URLs
- **Frontend**: http://3.110.197.69:30007
- **Backend Health**: http://3.110.197.69:30008/health
- **Backend API**: http://3.110.197.69:30008/calculate

### Node Information
- **Master Node**: 172.31.44.115 (Private)
- **Worker Node 1**: 172.31.32.128 (Private)
- **Worker Node 2**: 172.31.34.134 (Private), 3.110.197.69 (Public)

### Docker Images
- **Backend**: bharathadalla/calculator-backend:v2
- **Frontend**: bharathadalla/k8s-calculator-frontend:v2

### Ports
- **Frontend NodePort**: 30007
- **Backend NodePort**: 30008
- **Backend Internal**: 5000
- **Frontend Internal**: 80

### Namespace
- **Name**: calculator-app

---

## Maintenance and Updates

### Update Application Code

When you make code changes:

1. **Update source files** (backend/app.py or frontend/index.html)

2. **Rebuild Docker images**:
```bash
docker build -t bharathadalla/calculator-backend:v3 ./backend
docker build -t bharathadalla/k8s-calculator-frontend:v3 ./frontend
```

3. **Push to Docker Hub**:
```bash
docker push bharathadalla/calculator-backend:v3
docker push bharathadalla/k8s-calculator-frontend:v3
```

4. **Update k8s-deployment.yaml**:
```yaml
image: bharathadalla/calculator-backend:v3
image: bharathadalla/k8s-calculator-frontend:v3
```

5. **Apply changes**:
```bash
kubectl apply -f k8s-deployment.yaml
kubectl rollout restart deployment backend-deployment -n calculator-app
kubectl rollout restart deployment frontend-deployment -n calculator-app
```

---

### Scale Application

```bash
# Increase replicas (if resources allow)
kubectl scale deployment backend-deployment --replicas=2 -n calculator-app
kubectl scale deployment frontend-deployment --replicas=2 -n calculator-app

# Decrease replicas
kubectl scale deployment backend-deployment --replicas=1 -n calculator-app
```

---

## Conclusion

This project successfully demonstrates:
✅ Microservices architecture with frontend and backend separation
✅ Containerization with Docker
✅ Orchestration with Kubernetes on AWS
✅ NodePort services for external access
✅ Resource management and troubleshooting
✅ CORS handling for cross-origin requests
✅ Health checks and liveness probes
✅ Proper namespace organization

**Key Achievements**:
- Full calculator functionality (4 operations)
- Accessible via public IP
- Handles errors gracefully (division by zero)
- Optimized for resource-constrained environment
- Documented troubleshooting process

**Production Readiness Improvements** (Future):
- Implement Ingress instead of NodePort
- Add authentication/authorization
- Use ConfigMaps for environment variables
- Implement monitoring with Prometheus/Grafana
- Add CI/CD pipeline
- Use managed Kubernetes (EKS) instead of self-managed
- Implement horizontal pod autoscaling
- Add persistent storage if needed
- Use SSL/TLS certificates for HTTPS

---

**Project Author**: Bharath Adalla  
**Docker Hub**: bharathadalla  
**Deployment Date**: December 2025  
**Kubernetes Version**: v1.28.0  
**Infrastructure**: AWS EC2 (1 Master + 2 Workers)

---

*For questions or issues, review the Troubleshooting section or check pod logs using kubectl commands above.*
