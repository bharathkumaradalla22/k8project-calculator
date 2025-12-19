This README is updated with :

Complete Sections:

1. Project Overview with your specific details:

Docker Hub username: bharathadalla
Worker Node IP: 13.232.97.164
Updated ports: 30007 (frontend), 30008 (backend)

2. 14-Step Deployment Process:

SSH to AWS master node
Clean up old namespace
Docker login
Build & push images
Deploy to Kubernetes
Configure security groups
Test the application

3. Comprehensive Troubleshooting Guide:

Pods not running
ImagePullBackOff errors
Frontend-backend connectivity
CORS issues

4. Quick Commands Reference:

Deployment commands
Monitoring commands
Debugging commands
Cleanup commands

5. Technical Architecture Diagram:

Visual flow from browser to pods
Port mappings
Service relationships

6.Verification Checklist:

Step-by-step verification commands
Success criteria

7. Important Notes:

Port configuration details
Docker image requirements
AWS security setup
High availability setup


# Kubernetes Sum Calculator Application

A production-ready calculator application deployed on Kubernetes cluster with 1 master node and 2 worker nodes on AWS. This application demonstrates microservices architecture, Docker containerization, and Kubernetes orchestration.

---

## 🎯 Project Overview

**Docker Hub Username**: `bharathadalla`  
**Worker Node Public IP**: `13.232.97.164`  
**Frontend Access**: http://13.232.97.164:30007  
**Backend API Access**: http://13.232.97.164:30008

### Architecture
- **Frontend**: Nginx serving HTML/CSS/JavaScript (Port 30007)
- **Backend**: Flask REST API (Port 30008)
- **Kubernetes**: 1 Master + 2 Worker Nodes
- **Deployment**: 2 replicas per service for high availability

---

## 📁 File Structure

```
k8practice/
├── backend/
│   ├── app.py                          ← Flask backend application
│   ├── requirements.txt                ← Python dependencies
│   └── Dockerfile                      ← Backend Docker image
├── frontend/
│   ├── index.html                      ← Frontend UI
│   └── Dockerfile                      ← Frontend Docker image
├── k8s-deployment.yaml                        ← Complete backend + frontend K8s config
├── backend-deployment.yaml             ← Backend deployment only
├── frontend-deployment.yaml            ← Frontend deployment only
├── frontend-service-nodeport.yaml      ← Frontend service (NodePort 30007)
├── deploy-all.yaml.yaml                ← Alternative all-in-one deployment
├── frontend-config.yaml                ← Frontend ConfigMap
└── frontend-fix.yaml.yaml              ← Frontend ConfigMap alternative
```

---

## 🚀 Complete Step-by-Step Deployment Process

### **Step 1: Connect to AWS Master Node**

```bash
# From your local machine, SSH to master node
ssh -i <your-key.pem> ubuntu@<master-node-public-ip>

# Or if using ec2-user
ssh -i <your-key.pem> ec2-user@<master-node-public-ip>
```

### **Step 2: Navigate to Project Directory**

```bash
cd /home/test/k8practice
ls -la
```

### **Step 3: Clean Up Old Deployment (if exists)**

```bash
# Delete the old namespace and all resources in it
kubectl delete namespace calculator-app

# Wait for deletion to complete
sleep 10

# Verify namespace is deleted
kubectl get namespaces
```

### **Step 4: Login to Docker Hub**

```bash
# Login to Docker Hub
docker login

# Enter credentials:
# Username: bharathadalla
# Password: <your-docker-hub-password>
```

### **Step 5: Build Docker Images**

```bash
# Build backend image
docker build -t bharathadalla/calculator-backend:v1 ./backend

# Build frontend image
docker build -t bharathadalla/k8s-calculator-frontend:v1 ./frontend

# Verify images are built successfully
docker images | grep bharathadalla
```

Expected output:
```
bharathadalla/calculator-backend         v1    abc123...   2 minutes ago   150MB
bharathadalla/k8s-calculator-frontend    v1    def456...   1 minute ago    23MB
```

### **Step 6: Push Images to Docker Hub**

```bash
# Push backend image
docker push bharathadalla/calculator-backend:v1

# Push frontend image
docker push bharathadalla/k8s-calculator-frontend:v1

# Verify push was successful
echo "✅ Images pushed successfully!"
```

### **Step 7: Create Kubernetes Namespace**

```bash
# Create new namespace
kubectl create namespace calculator-app

# Verify namespace is created
kubectl get namespaces
```

### **Step 8: Deploy Application to Kubernetes**

```bash
# Deploy using k8s-deployment.yaml (contains all resources)
kubectl apply -f k8s-deployment.yaml

# Wait for deployment to complete
sleep 15

# Check deployment status
kubectl get all -n calculator-app
```

### **Step 9: Verify Deployment**

```bash
# Check pods are running
kubectl get pods -n calculator-app

# Expected output:
# NAME                                    READY   STATUS    RESTARTS   AGE
# backend-deployment-xxxx                 1/1     Running   0          30s
# backend-deployment-yyyy                 1/1     Running   0          30s
# frontend-deployment-xxxx                1/1     Running   0          30s
# frontend-deployment-yyyy                1/1     Running   0          30s

# Check services and NodePort assignments
kubectl get svc -n calculator-app
```

Expected services output:
```
NAME                         TYPE        CLUSTER-IP       PORT(S)
backend-service              ClusterIP   10.x.x.x         5000/TCP
backend-service-nodeport     NodePort    10.x.x.x         5000:30008/TCP
frontend-service             NodePort    10.x.x.x         80:30007/TCP
```

### **Step 10: Check Pod Logs**

```bash
# Check backend logs
kubectl logs -n calculator-app -l app=backend --tail=20

# Check frontend logs
kubectl logs -n calculator-app -l app=frontend --tail=10
```

### **Step 11: Test Backend Health Endpoint**

```bash
# Test from master node
curl http://localhost:30008/health

# Expected response:
# {"status":"ok"}

# Test backend add endpoint
curl -X POST http://localhost:30008/add \
  -H "Content-Type: application/json" \
  -d '{"num1": 10, "num2": 20}'

# Expected response:
# {"result":30,"status":"success","message":"Added 10.0 and 20.0"}
```

### **Step 12: Configure AWS Security Group**

**Using AWS Console:**
1. Go to EC2 Dashboard
2. Select your worker node instance
3. Click on Security Group
4. Add Inbound Rules:
   - Type: Custom TCP, Port: **30007**, Source: 0.0.0.0/0 (Frontend)
   - Type: Custom TCP, Port: **30008**, Source: 0.0.0.0/0 (Backend API)
5. Save rules

**Using AWS CLI (from local machine):**
```bash
# Get your security group ID
aws ec2 describe-instances \
  --filters "Name=ip-address,Values=13.232.97.164" \
  --query "Reservations[].Instances[].SecurityGroups[].GroupId" \
  --output text

# Add inbound rules (replace sg-xxxxx with actual security group ID)
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 30007 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 30008 \
  --cidr 0.0.0.0/0
```

### **Step 13: Access Your Application**

Open your browser and navigate to:

```
http://13.232.97.164:30007
```

### **Step 14: Test the Calculator**

1. **Enter first number**: `15`
2. **Enter second number**: `25`
3. **Click**: "Calculate Sum"
4. **Expected Result**: `Result: 40` (displayed in green)

---

## 🔍 Troubleshooting Guide

### Issue: Pods Not Running

```bash
# Check pod status
kubectl get pods -n calculator-app

# Describe pod for detailed information
kubectl describe pod -n calculator-app <pod-name>

# Check events
kubectl get events -n calculator-app --sort-by='.lastTimestamp'
```

### Issue: ImagePullBackOff Error

```bash
# Verify images exist on Docker Hub
docker pull bharathadalla/calculator-backend:v1
docker pull bharathadalla/k8s-calculator-frontend:v1

# If images are correct, restart deployments
kubectl rollout restart deployment/backend-deployment -n calculator-app
kubectl rollout restart deployment/frontend-deployment -n calculator-app

# Watch rollout status
kubectl rollout status deployment/backend-deployment -n calculator-app
kubectl rollout status deployment/frontend-deployment -n calculator-app
```

### Issue: Frontend Can't Reach Backend

```bash
# Test backend from within cluster
kubectl run test-pod --image=curlimages/curl -it --rm -n calculator-app -- sh
# Inside the pod:
curl http://backend-service.calculator-app.svc.cluster.local:5000/health

# Test NodePort from master node
curl http://localhost:30008/health

# Check backend service endpoints
kubectl get endpoints -n calculator-app backend-service-nodeport
```

### Issue: Browser Shows Connection Refused

```bash
# Verify NodePort services
kubectl get svc -n calculator-app

# Check if ports are listening on worker node
kubectl get nodes -o wide

# SSH to worker node and test locally
ssh <worker-node-ip>
curl http://localhost:30007
curl http://localhost:30008/health
```

### Issue: CORS Errors in Browser

```bash
# Check backend logs for CORS issues
kubectl logs -n calculator-app -l app=backend --tail=50

# Verify CORS is enabled in backend
kubectl exec -n calculator-app <backend-pod-name> -- cat /app/app.py | grep CORS
```

---

## 🎯 Quick Commands Reference

### Deployment Commands
```bash
# One-line full deployment (after images are pushed)
cd /home/test/k8practice && \
kubectl delete namespace calculator-app --ignore-not-found && \
sleep 5 && \
kubectl create namespace calculator-app && \
kubectl apply -f k8s-deployment.yaml && \
kubectl get pods -n calculator-app -w

# Restart deployments
kubectl rollout restart deployment/backend-deployment -n calculator-app
kubectl rollout restart deployment/frontend-deployment -n calculator-app

# Scale deployments
kubectl scale deployment/backend-deployment --replicas=3 -n calculator-app
kubectl scale deployment/frontend-deployment --replicas=3 -n calculator-app
```

### Monitoring Commands
```bash
# Watch pods status
kubectl get pods -n calculator-app -w

# View all resources
kubectl get all -n calculator-app

# Check resource usage
kubectl top pods -n calculator-app
kubectl top nodes

# View logs continuously
kubectl logs -n calculator-app -l app=backend -f
kubectl logs -n calculator-app -l app=frontend -f
```

### Debugging Commands
```bash
# Execute commands inside pod
kubectl exec -it -n calculator-app <pod-name> -- /bin/sh

# Port forward for local testing
kubectl port-forward -n calculator-app svc/backend-service 5000:5000
kubectl port-forward -n calculator-app svc/frontend-service 8080:80

# Describe resources
kubectl describe deployment -n calculator-app backend-deployment
kubectl describe svc -n calculator-app backend-service-nodeport

# Get pod details with wide output
kubectl get pods -n calculator-app -o wide
```

### Cleanup Commands
```bash
# Delete specific deployments
kubectl delete deployment backend-deployment -n calculator-app
kubectl delete deployment frontend-deployment -n calculator-app

# Delete services
kubectl delete svc backend-service -n calculator-app
kubectl delete svc backend-service-nodeport -n calculator-app
kubectl delete svc frontend-service -n calculator-app

# Delete entire namespace (removes all resources)
kubectl delete namespace calculator-app
```

---

## 📊 Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User's Browser                           │
│                   http://13.232.97.164:30007                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS Security Group                           │
│           Inbound: Port 30007, 30008 allowed                    │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Worker Node (Public IP)                     │
│                      13.232.97.164                              │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
        ┌───────────────────┐     ┌───────────────────┐
        │  Frontend Service │     │  Backend Service  │
        │  NodePort: 30007  │     │  NodePort: 30008  │
        └─────────┬─────────┘     └─────────┬─────────┘
                  │                         │
        ┌─────────┴─────────┐     ┌─────────┴─────────┐
        ▼                   ▼     ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Frontend    │    │  Frontend    │    │   Backend    │    │   Backend    │
│   Pod 1      │    │   Pod 2      │    │    Pod 1     │    │    Pod 2     │
│  Nginx:80    │    │  Nginx:80    │    │  Flask:5000  │    │  Flask:5000  │
│ Worker Node1 │    │ Worker Node2 │    │ Worker Node1 │    │ Worker Node2 │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘

Frontend JavaScript calls: http://13.232.97.164:30008/add
                                     │
                                     ▼
                          Backend processes request
                                     │
                                     ▼
                    Returns: {"result": sum, "status": "success"}
```

---

## 🔧 Technical Details

### Frontend Container
- **Base Image**: `nginx:alpine`
- **Exposed Port**: 80
- **NodePort**: 30007
- **Replicas**: 2
- **Files**: index.html (HTML/CSS/JavaScript)
- **Features**:
  - Responsive UI
  - Input validation
  - AJAX calls to backend
  - Error handling

### Backend Container
- **Base Image**: `python:3.9-slim`
- **Exposed Port**: 5000
- **NodePort**: 30008
- **Replicas**: 2
- **Dependencies**: Flask, flask-cors
- **Endpoints**:
  - `GET /health` - Health check
  - `POST /add` - Addition operation
- **CORS**: Enabled for all origins

### Kubernetes Resources
- **Namespace**: `calculator-app`
- **Deployments**: 2 (backend, frontend)
- **Services**: 3 (backend ClusterIP, backend NodePort, frontend NodePort)
- **Pod Distribution**: Anti-affinity rules ensure pods spread across worker nodes
- **Health Checks**: Liveness and readiness probes configured
- **Resource Limits**: CPU and memory limits set for stability

---

## ✅ Verification Checklist

After deployment, verify:

```bash
# 1. Namespace exists
kubectl get namespace calculator-app

# Check all resources
kubectl get all -n calculator-app

# Check deployments
kubectl get deployments -n calculator-app

# Check pods and their node assignment
kubectl get pods -n calculator-app -o wide

# Check services and endpoints
kubectl get svc,endpoints -n calculator-app

# Check configmaps
kubectl get configmaps -n calculator-app

# View pod logs
kubectl logs -l app=frontend -n calculator-app
kubectl logs -l app=backend -n calculator-app

# Describe a pod
kubectl describe pod <pod-name> -n calculator-app

# Test backend connectivity
POD=$(kubectl get pods -n calculator-app -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD -n calculator-app -- curl -X POST http://localhost:5000/add \
  -H "Content-Type: application/json" \
  -d '{"num1":5, "num2":3}'
```

---

## Troubleshooting

### Issue: "Page cannot be displayed"
**Solution**: 
1. Check pods: `kubectl get pods -n calculator-app`
2. Check logs: `kubectl logs -l app=frontend -n calculator-app`
3. Verify service: `kubectl get svc frontend-service -n calculator-app`

### Issue: Backend error appears
**Solution**:
1. Check backend logs: `kubectl logs -l app=backend -n calculator-app`
2. Verify backend service: `kubectl get svc backend-service -n calculator-app`
3. Check endpoints: `kubectl get endpoints backend-service -n calculator-app`

### Issue: Cannot reach http://<ip>:30001
**Solution**:
1. Verify worker node IP: `kubectl get nodes -o wide`
2. Check firewall: Port 30001 open?
3. Verify service: `kubectl get svc frontend-service -n calculator-app`

---

## Documentation

- **QUICK_START.md** - Fast deployment guide (5 minutes)
- **DEPLOYMENT_GUIDE.md** - Detailed step-by-step guide
- **CHANGES_SUMMARY.md** - Detailed list of all changes made
- **DEPLOYMENT_CHECKLIST.md** - Pre-deployment verification checklist

---

## Cluster Requirements

- **Master Node**: 1 (for control plane)
- **Worker Nodes**: 2 (for application pods)
- **Memory per worker**: 256MB minimum (128MB frontend + 128MB backend)
- **CPU per worker**: 100m minimum
- **Network**: Worker nodes can communicate with each other

---

## Key Improvements

| Before | After |
|--------|-------|
| 1 frontend pod | 2 frontend pods (distributed) |
| 1 backend pod | 2 backend pods (distributed) |
| No health checks | Liveness probes on all pods |
| No resource limits | CPU/Memory requests and limits |
| Missing namespace | Namespace created |
| Parameter mismatch | All parameters unified |
| Hardcoded backend URL | Uses Kubernetes DNS |
| No input validation | Frontend validates inputs |
| No error handling | Try-catch blocks added |

---

## Production Checklist

- [x] All services have health checks
- [x] Pods distributed across nodes (anti-affinity)
- [x] Resource limits defined
- [x] Error handling implemented
- [x] Input validation added
- [x] Namespace isolation
- [x] Service discovery using DNS
- [x] Scalable (replicas can be increased)

---

## 📝 Important Notes

1. **Port Configuration**:
   - Frontend: Port **30007** (changed from 30001)
   - Backend: Port **30008** (changed from 30002)
   - Ports changed to avoid conflicts with existing services

2. **Docker Images**:
   - Images must be pushed to Docker Hub before deployment
   - Image names use `bharathadalla` Docker Hub username
   - Version tag: `v1`

3. **AWS Security**:
   - Both ports (30007, 30008) must be open in security group
   - Without open ports, browser cannot access the application

4. **High Availability**:
   - 2 replicas per service
   - Pods distributed across worker nodes
   - Automatic restart on failure

5. **Namespace**:
   - All resources deployed in `calculator-app` namespace
   - Clean deployment requires deleting old namespace first

---

## 🎓 Learning Points

This project demonstrates:

- ✅ **Containerization**: Docker for both frontend and backend
- ✅ **Microservices**: Separate frontend and backend services
- ✅ **Kubernetes Orchestration**: Deployments, Services, NodePort
- ✅ **High Availability**: Multiple replicas with pod anti-affinity
- ✅ **Cloud Deployment**: AWS EC2 with security groups
- ✅ **DevOps Pipeline**: Build → Push → Deploy workflow
- ✅ **Container Registry**: Docker Hub for image storage
- ✅ **Service Discovery**: Kubernetes internal DNS
- ✅ **Health Checks**: Liveness and readiness probes
- ✅ **Resource Management**: CPU and memory limits

---

## 🔗 Quick Links

- **Frontend**: http://13.232.97.164:30007
- **Backend Health**: http://13.232.97.164:30008/health
- **Docker Hub**: https://hub.docker.com/u/bharathadalla

---

## 📞 Support

If you encounter issues:

1. Check pod logs: `kubectl logs -n calculator-app <pod-name>`
2. Verify security group has ports 30007 and 30008 open
3. Ensure Docker images are pushed to Docker Hub
4. Confirm all pods are in Running state
5. Test backend health endpoint first

---

## 🎉 Success Criteria

Your deployment is successful when:

- ✅ All 4 pods (2 frontend + 2 backend) are Running
- ✅ Services show correct NodePort assignments
- ✅ Backend health endpoint returns `{"status":"ok"}`
- ✅ Browser can access http://13.232.97.164:30007
- ✅ Calculator successfully adds numbers
- ✅ Result displays in green color
- ✅ No CORS errors in browser console

---

## 📂 File Reference Guide

### ✅ **Kubernetes Manifest Files** (YAML)

#### **Primary Deployment File:**
- **[k8s-deployment.yaml](k8s-deployment.yaml)** - ⭐ **MAIN FILE** - Complete deployment
  - Namespace (`calculator-app`)
  - Backend Deployment (2 replicas)
  - Backend Services (ClusterIP + NodePort 30008)
  - Frontend Deployment (2 replicas)
  - Frontend Service (NodePort 30007)
  - **Usage**: `kubectl apply -f k8s-deployment.yaml`

#### **Individual Component Files:**
- **[backend-deployment.yaml](backend-deployment.yaml)** - Backend Deployment only
- **[frontend-deployment.yaml](frontend-deployment.yaml)** - Frontend Deployment only
- **[frontend-service-nodeport.yaml](frontend-service-nodeport.yaml)** - Frontend Service only
- **[deploy-all.yaml.yaml](deploy-all.yaml.yaml)** - Alternative all-in-one deployment
- **[frontend-config.yaml](frontend-config.yaml)** - Frontend ConfigMap
- **[frontend-fix.yaml.yaml](frontend-fix.yaml.yaml)** - Frontend ConfigMap (alternative)

### ❌ **Non-Kubernetes Files**

#### **Application Source Code:**
- `backend/app.py` - Python Flask REST API application
- `frontend/index.html` - HTML/CSS/JavaScript frontend UI
- `backend/requirements.txt` - Python dependencies (Flask, flask-cors)
- `app.py` (root directory) - Standalone reference file

#### **Docker Container Images:**
- `backend/Dockerfile` - Backend container image definition
- `frontend/Dockerfile` - Frontend container image definition

#### **Documentation Files:**
- `README.md` - This comprehensive guide
- `QUICK_START.md` - Fast deployment guide
- `DEPLOYMENT_GUIDE.md` - Detailed deployment instructions
- `CHANGES_SUMMARY.md` - List of all changes
- `DEPLOYMENT_CHECKLIST.md` - Pre-deployment verification
- `*.md` - Other documentation files

### 🎯 **Which Files to Use for Deployment?**

**Option 1: Single File Deployment (Recommended)**
```bash
kubectl apply -f k8s-deployment.yaml
```
This deploys everything in one command.

**Option 2: Separate File Deployment**
```bash
kubectl create namespace calculator-app
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service-nodeport.yaml
```

### 📦 **Docker Images**
- **Backend**: `bharathadalla/calculator-backend:v1`
- **Frontend**: `bharathadalla/k8s-calculator-frontend:v1`

Both must be built and pushed to Docker Hub before deployment.

---

**Last Updated**: December 20, 2025  
**Status**: ✅ Production Ready & Successfully Deployed  
**Environment**: AWS EC2 (1 Master + 2 Worker Nodes)  
**Worker Node IP**: 13.232.97.164  
**Docker Hub**: bharathadalla

---

**Happy Calculating! 🎉**


