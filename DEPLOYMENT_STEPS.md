# 🚀 Complete Deployment Steps

## Cluster Information
- **Master Node Private IP**: 172.31.44.115
- **Worker Node 1 Private IP**: 172.31.32.128
- **Worker Node 2 Private IP**: 172.31.34.134
- **Worker Node Public IP**: 13.232.97.164
- **Docker Hub Username**: bharathadalla
- **Namespace**: calculator-app
- **Frontend Port**: 30007
- **Backend API Port**: 30008

---

## 📋 Step-by-Step Deployment Commands

### **STEP 1: SSH to Master Node**

```bash
# From your local machine
ssh -i <your-key.pem> ubuntu@<master-node-public-ip>

# Or if using ec2-user
ssh -i <your-key.pem> ec2-user@<master-node-public-ip>
```

---

### **STEP 2: Navigate to Project Directory**

```bash
cd /home/test/k8practice
pwd
# Should show: /home/test/k8practice
```

---

### **STEP 3: Clean Up Old Deployment (If Exists)**

```bash
# Delete old namespace and all resources
kubectl delete namespace calculator-app --ignore-not-found

# Wait for complete deletion
sleep 10

# Verify deletion
kubectl get namespaces | grep calculator-app
# Should return nothing if successfully deleted
```

---

### **STEP 4: Login to Docker Hub**

```bash
# Login to Docker Hub
docker login

# Enter credentials when prompted:
# Username: bharathadalla
# Password: <your-docker-hub-password>

# Verify login
docker info | grep Username
# Should show: Username: bharathadalla
```

---

### **STEP 5: Build Docker Images with New Version**

```bash
# Build backend image (v2 - updated calculator)
docker build -t bharathadalla/calculator-backend:v2 ./backend

# Verify backend build
docker images | grep calculator-backend

# Build frontend image (v2 - updated UI and ports)
docker build -t bharathadalla/k8s-calculator-frontend:v2 ./frontend

# Verify frontend build
docker images | grep k8s-calculator-frontend

# List all your images
docker images | grep bharathadalla
```

Expected output:
```
bharathadalla/calculator-backend         v2    abc123...   1 minute ago   150MB
bharathadalla/k8s-calculator-frontend    v2    def456...   30 seconds ago  23MB
```

---

### **STEP 6: Push Images to Docker Hub**

```bash
# Push backend image
docker push bharathadalla/calculator-backend:v2

echo "✅ Backend image pushed successfully!"

# Push frontend image
docker push bharathadalla/k8s-calculator-frontend:v2

echo "✅ Frontend image pushed successfully!"

# Verify images on Docker Hub (optional)
curl -s https://hub.docker.com/v2/repositories/bharathadalla/calculator-backend/tags/ | grep v2
curl -s https://hub.docker.com/v2/repositories/bharathadalla/k8s-calculator-frontend/tags/ | grep v2
```

---

### **STEP 7: Update Deployment Files with New Image Version**

```bash
# Update k8s-deployment.yaml to use v2 images
sed -i 's/calculator-backend:v1/calculator-backend:v2/g' k8s-deployment.yaml
sed -i 's/k8s-calculator-frontend:v1/k8s-calculator-frontend:v2/g' k8s-deployment.yaml

# Verify the changes
grep "image:" k8s-deployment.yaml
```

Expected output:
```
        image: bharathadalla/calculator-backend:v2
        image: bharathadalla/k8s-calculator-frontend:v2
```

---

### **STEP 8: Create Namespace**

```bash
# Create calculator-app namespace
kubectl create namespace calculator-app

# Verify namespace creation
kubectl get namespaces | grep calculator-app
```

Expected output:
```
calculator-app    Active   5s
```

---

### **STEP 9: Deploy Application to Kubernetes**

```bash
# Deploy all resources from main deployment file
kubectl apply -f k8s-deployment.yaml

# Wait for deployment
sleep 15

echo "✅ Deployment initiated!"
```

---

### **STEP 10: Verify Deployment Status**

```bash
# Check all resources in namespace
kubectl get all -n calculator-app

# Check pods are running (wait until STATUS = Running)
kubectl get pods -n calculator-app -o wide

# Watch pods until all are running (Ctrl+C to exit)
kubectl get pods -n calculator-app -w
```

Expected output:
```
NAME                                    READY   STATUS    RESTARTS   AGE   NODE
backend-deployment-xxxx                 1/1     Running   0          45s   172.31.32.128
backend-deployment-yyyy                 1/1     Running   0          45s   172.31.34.134
frontend-deployment-xxxx                1/1     Running   0          45s   172.31.32.128
frontend-deployment-yyyy                1/1     Running   0          45s   172.31.34.134
```

---

### **STEP 11: Verify Services and NodePorts**

```bash
# Check services
kubectl get svc -n calculator-app

# Check service details
kubectl describe svc backend-service-nodeport -n calculator-app
kubectl describe svc frontend-service -n calculator-app
```

Expected output:
```
NAME                         TYPE        CLUSTER-IP       PORT(S)
backend-service              ClusterIP   10.x.x.x         5000/TCP
backend-service-nodeport     NodePort    10.x.x.x         5000:30008/TCP
frontend-service             NodePort    10.x.x.x         80:30007/TCP
```

---

### **STEP 12: Check Pod Logs**

```bash
# Check backend logs
kubectl logs -n calculator-app -l app=backend --tail=20

# Expected: Flask app running on port 5000

# Check frontend logs
kubectl logs -n calculator-app -l app=frontend --tail=20

# Expected: Nginx access logs
```

---

### **STEP 13: Test Backend Health from Master Node**

```bash
# Test backend health endpoint
curl http://localhost:30008/health

# Expected response:
# {"status":"ok"}

# Test backend calculate endpoint
curl -X POST http://localhost:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1": 10, "num2": 5, "operation": "add"}'

# Expected response:
# {"result":15,"status":"success","message":"10 + 5 = 15"}

# Test frontend
curl -I http://localhost:30007

# Expected: HTTP/1.1 200 OK
```

---

### **STEP 14: Verify Pod Distribution Across Worker Nodes**

```bash
# Check which worker node each pod is on
kubectl get pods -n calculator-app -o wide

# You should see pods distributed across both worker nodes:
# - 172.31.32.128
# - 172.31.34.134
```

---

### **STEP 15: Configure AWS Security Group**

#### **Option A: Using AWS Console**
1. Go to EC2 Dashboard → Security Groups
2. Select the security group for your worker nodes
3. Add Inbound Rules:
   - **Type**: Custom TCP
   - **Port**: 30007
   - **Source**: 0.0.0.0/0 (or Your IP)
   - **Description**: Frontend Calculator UI
   
   - **Type**: Custom TCP
   - **Port**: 30008
   - **Source**: 0.0.0.0/0 (or Your IP)
   - **Description**: Backend Calculator API

#### **Option B: Using AWS CLI (from local machine)**

```bash
# Get security group ID
aws ec2 describe-instances \
  --filters "Name=private-ip-address,Values=172.31.32.128" \
  --query "Reservations[].Instances[].SecurityGroups[].GroupId" \
  --output text

# Add inbound rule for frontend (port 30007)
aws ec2 authorize-security-group-ingress \
  --group-id <your-security-group-id> \
  --protocol tcp \
  --port 30007 \
  --cidr 0.0.0.0/0

# Add inbound rule for backend (port 30008)
aws ec2 authorize-security-group-ingress \
  --group-id <your-security-group-id> \
  --protocol tcp \
  --port 30008 \
  --cidr 0.0.0.0/0

echo "✅ Security group rules added!"
```

---

### **STEP 16: Test from Worker Node (Optional)**

```bash
# SSH to worker node from master
ssh 172.31.32.128

# Test services locally
curl http://localhost:30007
curl http://localhost:30008/health

# Exit worker node
exit
```

---

### **STEP 17: Access Application from Browser**

Open your browser and navigate to:

**Frontend URL:**
```
http://13.232.97.164:30007
```

**Backend Health Check:**
```
http://13.232.97.164:30008/health
```

---

### **STEP 18: Test All Calculator Operations**

1. **Open**: http://13.232.97.164:30007
2. **Test Addition**: 
   - Enter: 15 and 10
   - Click: ➕ Add
   - Expected: `15 + 10 = 25`
3. **Test Subtraction**:
   - Enter: 15 and 10
   - Click: ➖ Subtract
   - Expected: `15 - 10 = 5`
4. **Test Multiplication**:
   - Enter: 15 and 10
   - Click: ✖️ Multiply
   - Expected: `15 × 10 = 150`
5. **Test Division**:
   - Enter: 15 and 3
   - Click: ➗ Divide
   - Expected: `15 ÷ 3 = 5`
6. **Test Division by Zero**:
   - Enter: 15 and 0
   - Click: ➗ Divide
   - Expected: ❌ Error: Cannot divide by zero

---

## 🎯 One-Line Complete Deployment

After images are pushed, use this single command:

```bash
cd /home/test/k8practice && \
kubectl delete namespace calculator-app --ignore-not-found && \
sleep 5 && \
kubectl create namespace calculator-app && \
kubectl apply -f k8s-deployment.yaml && \
echo "⏳ Waiting for pods to start..." && \
sleep 20 && \
kubectl get pods -n calculator-app -o wide && \
echo "✅ Deployment complete! Access: http://13.232.97.164:30007"
```

---

## 🔍 Verification Checklist

Run these commands to verify everything:

```bash
# 1. Check namespace
kubectl get namespace calculator-app
echo "✅ Namespace exists"

# 2. Check all pods are running
kubectl get pods -n calculator-app | grep Running | wc -l
# Should return: 4 (2 backend + 2 frontend)

# 3. Check services
kubectl get svc -n calculator-app
echo "✅ Services configured"

# 4. Test backend health
curl -s http://localhost:30008/health | grep ok
echo "✅ Backend is healthy"

# 5. Test frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:30007
# Should return: 200

# 6. Check pod distribution
kubectl get pods -n calculator-app -o wide | grep -E "172.31.32.128|172.31.34.134"
echo "✅ Pods distributed across worker nodes"

echo ""
echo "🎉 All checks passed! Application is ready!"
echo "🌐 Frontend: http://13.232.97.164:30007"
echo "🔧 Backend: http://13.232.97.164:30008/health"
```

---

## 🐛 Troubleshooting Commands

### If Pods are Not Running:

```bash
# Check pod status
kubectl get pods -n calculator-app

# Describe problematic pod
kubectl describe pod <pod-name> -n calculator-app

# Check events
kubectl get events -n calculator-app --sort-by='.lastTimestamp' | tail -20

# Check logs
kubectl logs <pod-name> -n calculator-app
```

### If ImagePullBackOff Error:

```bash
# Verify images exist on Docker Hub
docker pull bharathadalla/calculator-backend:v2
docker pull bharathadalla/k8s-calculator-frontend:v2

# Delete and recreate deployment
kubectl delete deployment backend-deployment -n calculator-app
kubectl delete deployment frontend-deployment -n calculator-app
kubectl apply -f k8s-deployment.yaml
```

### If Services Not Accessible:

```bash
# Check service endpoints
kubectl get endpoints -n calculator-app

# Test from within cluster
kubectl run test-pod --image=curlimages/curl -it --rm -n calculator-app -- sh
# Inside pod:
curl http://backend-service:5000/health
exit

# Check NodePort on worker node
ssh 172.31.32.128
curl http://localhost:30007
curl http://localhost:30008/health
exit
```

---

## 📊 Monitoring Commands

```bash
# Watch pods continuously
watch kubectl get pods -n calculator-app -o wide

# View logs in real-time
kubectl logs -n calculator-app -l app=backend -f

# Check resource usage
kubectl top pods -n calculator-app
kubectl top nodes

# View all resources
kubectl get all -n calculator-app -o wide
```

---

## 🗑️ Cleanup Commands (If Needed)

```bash
# Delete entire application
kubectl delete namespace calculator-app

# Remove old Docker images (on master node)
docker rmi bharathadalla/calculator-backend:v1
docker rmi bharathadalla/k8s-calculator-frontend:v1

# Keep v2 images for future use
```

---

## ✅ Success Criteria

Your deployment is successful when:

- ✅ Namespace `calculator-app` exists
- ✅ 4 pods are in `Running` state (2 backend + 2 frontend)
- ✅ Pods are distributed across both worker nodes (172.31.32.128 and 172.31.34.134)
- ✅ Services show correct NodePort assignments (30007, 30008)
- ✅ Backend health check returns `{"status":"ok"}`
- ✅ Frontend is accessible at http://13.232.97.164:30007
- ✅ All calculator operations work (add, subtract, multiply, divide)
- ✅ Division by zero shows proper error message
- ✅ No errors in pod logs

---

## 🎉 Final Testing

```bash
# Complete end-to-end test
curl -X POST http://13.232.97.164:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1": 100, "num2": 25, "operation": "add"}'

curl -X POST http://13.232.97.164:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1": 100, "num2": 25, "operation": "subtract"}'

curl -X POST http://13.232.97.164:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1": 100, "num2": 25, "operation": "multiply"}'

curl -X POST http://13.232.97.164:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1": 100, "num2": 25, "operation": "divide"}'

echo ""
echo "🎊 Congratulations! Your Kubernetes Calculator is fully operational!"
echo "📱 Access it at: http://13.232.97.164:30007"
```

---

## 🏷️ Update Docker Hub After Successful Testing

Once you've tested the application and everything works perfectly, follow these steps to update Docker Hub with production-ready images.

### **STEP 1: Verify Application is Working**

```bash
# SSH to master node
ssh -i <your-key.pem> ubuntu@<master-node-public-ip>
cd /home/test/k8practice

# Check all pods are running
kubectl get pods -n calculator-app
# All should show: Running

# Test backend API
curl -s http://localhost:30008/health | grep ok
# Should return: {"status":"ok"}

# Test all calculator operations
curl -X POST http://localhost:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1": 50, "num2": 10, "operation": "add"}'
# Should return: {"result":60,"status":"success"...}

curl -X POST http://localhost:30008/calculate \
  -H "Content-Type: application/json" \
  -d '{"num1": 50, "num2": 10, "operation": "divide"}'
# Should return: {"result":5,"status":"success"...}

echo "✅ Application is working correctly!"
```

### **STEP 2: Tag Images as Latest (Production)**

```bash
# Tag backend as latest
docker tag bharathadalla/calculator-backend:v2 bharathadalla/calculator-backend:latest

# Tag frontend as latest
docker tag bharathadalla/k8s-calculator-frontend:v2 bharathadalla/k8s-calculator-frontend:latest

# Verify tags
docker images | grep bharathadalla
```

Expected output:
```
bharathadalla/calculator-backend         v2        abc123...   2 hours ago   150MB
bharathadalla/calculator-backend         latest    abc123...   2 hours ago   150MB
bharathadalla/k8s-calculator-frontend    v2        def456...   2 hours ago   23MB
bharathadalla/k8s-calculator-frontend    latest    def456...   2 hours ago   23MB
```

### **STEP 3: Create Stable Version Tag (Recommended)**

```bash
# Create stable version tag with date or version number
VERSION="stable-$(date +%Y%m%d)"
echo "Creating version: $VERSION"

# Tag backend with stable version
docker tag bharathadalla/calculator-backend:v2 bharathadalla/calculator-backend:$VERSION

# Tag frontend with stable version
docker tag bharathadalla/k8s-calculator-frontend:v2 bharathadalla/k8s-calculator-frontend:$VERSION

# Example: If today is 2025-12-20, creates tags like:
# bharathadalla/calculator-backend:stable-20251220
# bharathadalla/k8s-calculator-frontend:stable-20251220
```

### **STEP 4: Push All Tags to Docker Hub**

```bash
# Push backend v2
docker push bharathadalla/calculator-backend:v2
echo "✅ Backend v2 pushed"

# Push backend latest
docker push bharathadalla/calculator-backend:latest
echo "✅ Backend latest pushed"

# Push backend stable version
docker push bharathadalla/calculator-backend:$VERSION
echo "✅ Backend $VERSION pushed"

# Push frontend v2
docker push bharathadalla/k8s-calculator-frontend:v2
echo "✅ Frontend v2 pushed"

# Push frontend latest
docker push bharathadalla/k8s-calculator-frontend:latest
echo "✅ Frontend latest pushed"

# Push frontend stable version
docker push bharathadalla/k8s-calculator-frontend:$VERSION
echo "✅ Frontend $VERSION pushed"

echo ""
echo "🎉 All images pushed to Docker Hub successfully!"
```

### **STEP 5: Verify Images on Docker Hub**

```bash
# Check backend tags
curl -s https://hub.docker.com/v2/repositories/bharathadalla/calculator-backend/tags/ | grep name

# Check frontend tags
curl -s https://hub.docker.com/v2/repositories/bharathadalla/k8s-calculator-frontend/tags/ | grep name

# Or visit in browser:
echo "Backend: https://hub.docker.com/r/bharathadalla/calculator-backend/tags"
echo "Frontend: https://hub.docker.com/r/bharathadalla/k8s-calculator-frontend/tags"
```

### **STEP 6: Update Deployment to Use Latest Tag (Optional)**

```bash
# Update k8s-deployment.yaml to use latest tag
sed -i 's/calculator-backend:v2/calculator-backend:latest/g' k8s-deployment.yaml
sed -i 's/k8s-calculator-frontend:v2/k8s-calculator-frontend:latest/g' k8s-deployment.yaml

# Verify changes
grep "image:" k8s-deployment.yaml

# Apply updated deployment
kubectl apply -f k8s-deployment.yaml

# Restart deployments to pull latest images
kubectl rollout restart deployment/backend-deployment -n calculator-app
kubectl rollout restart deployment/frontend-deployment -n calculator-app

# Watch rollout status
kubectl rollout status deployment/backend-deployment -n calculator-app
kubectl rollout status deployment/frontend-deployment -n calculator-app
```

### **STEP 7: Add Release Notes (Documentation)**

Create a release notes file:

```bash
cat > RELEASE_NOTES.md << 'EOF'
# Release Notes - Calculator App v2.0

## Release Date: December 20, 2025

## Version: 2.0 (stable-20251220)

## Docker Images
- **Backend**: bharathadalla/calculator-backend:v2
- **Frontend**: bharathadalla/k8s-calculator-frontend:v2

## What's New
- ✨ Full calculator functionality (Add, Subtract, Multiply, Divide)
- 🎨 Modern UI with color-coded operation buttons
- 🔢 Support for decimal numbers
- ⚠️ Division by zero error handling
- 🧹 Clear button to reset calculator
- ✅ Input validation with helpful messages
- 🚀 Updated ports: Frontend (30007), Backend (30008)
- 📦 Namespace changed to calculator-app

## Deployment
- Namespace: calculator-app
- Frontend Port: 30007
- Backend API Port: 30008
- Replicas: 2 (per service)
- Worker Nodes: 2 (High Availability)

## Testing Status
- ✅ All calculator operations tested
- ✅ Division by zero handling verified
- ✅ Pod distribution across worker nodes confirmed
- ✅ Health checks passing
- ✅ Frontend UI responsive
- ✅ Backend API endpoints working

## Access URLs
- Frontend: http://13.232.97.164:30007
- Backend Health: http://13.232.97.164:30008/health
- Backend API: http://13.232.97.164:30008/calculate

## Known Issues
None

## Rollback Instructions
If needed, rollback to previous version:
```bash
kubectl set image deployment/backend-deployment python-backend=bharathadalla/calculator-backend:v1 -n calculator-app
kubectl set image deployment/frontend-deployment nginx-frontend=bharathadalla/k8s-calculator-frontend:v1 -n calculator-app
```

## Contributors
- Docker Hub: bharathadalla
- Cluster: AWS EC2 (1 Master + 2 Worker Nodes)
EOF

echo "✅ Release notes created"
```

### **STEP 8: Clean Up Old Images (Optional)**

```bash
# List all Docker images
docker images | grep bharathadalla

# Remove old v1 images to save space (if no longer needed)
docker rmi bharathadalla/calculator-backend:v1
docker rmi bharathadalla/k8s-calculator-frontend:v1

# Remove dangling images
docker image prune -f

echo "✅ Old images cleaned up"
```

### **STEP 9: Create Git Tag (If Using Version Control)**

```bash
# If your project is in a Git repository
git add .
git commit -m "Release v2.0 - Full calculator with updated ports"
git tag -a v2.0 -m "Release v2.0: Full calculator functionality"
git push origin main
git push origin v2.0

echo "✅ Git repository updated with release tag"
```

---

## 📊 Docker Hub Best Practices

### **Recommended Tagging Strategy:**

1. **Development**: `v1`, `v2`, `v3` - For specific versions during development
2. **Latest**: `latest` - Always points to the most recent stable version
3. **Stable**: `stable-YYYYMMDD` - Date-stamped stable releases
4. **Production**: `prod` or `production` - Currently running in production
5. **Semantic**: `1.0.0`, `1.1.0`, `2.0.0` - Semantic versioning for major releases

### **Example Tagging for Production Release:**

```bash
# After successful testing
VERSION="2.0.0"

# Backend
docker tag bharathadalla/calculator-backend:v2 bharathadalla/calculator-backend:latest
docker tag bharathadalla/calculator-backend:v2 bharathadalla/calculator-backend:$VERSION
docker tag bharathadalla/calculator-backend:v2 bharathadalla/calculator-backend:production

# Frontend
docker tag bharathadalla/k8s-calculator-frontend:v2 bharathadalla/k8s-calculator-frontend:latest
docker tag bharathadalla/k8s-calculator-frontend:v2 bharathadalla/k8s-calculator-frontend:$VERSION
docker tag bharathadalla/k8s-calculator-frontend:v2 bharathadalla/k8s-calculator-frontend:production

# Push all tags
docker push bharathadalla/calculator-backend:latest
docker push bharathadalla/calculator-backend:$VERSION
docker push bharathadalla/calculator-backend:production

docker push bharathadalla/k8s-calculator-frontend:latest
docker push bharathadalla/k8s-calculator-frontend:$VERSION
docker push bharathadalla/k8s-calculator-frontend:production
```

---

## 🔄 Complete Update Workflow

```bash
#!/bin/bash
# Complete Docker Hub update script after successful testing

echo "🚀 Starting Docker Hub update process..."

# 1. Verify application is working
echo "1️⃣ Verifying application status..."
kubectl get pods -n calculator-app | grep Running || exit 1
curl -s http://localhost:30008/health | grep ok || exit 1

# 2. Tag images
echo "2️⃣ Tagging images..."
VERSION="stable-$(date +%Y%m%d)"
docker tag bharathadalla/calculator-backend:v2 bharathadalla/calculator-backend:latest
docker tag bharathadalla/calculator-backend:v2 bharathadalla/calculator-backend:$VERSION
docker tag bharathadalla/k8s-calculator-frontend:v2 bharathadalla/k8s-calculator-frontend:latest
docker tag bharathadalla/k8s-calculator-frontend:v2 bharathadalla/k8s-calculator-frontend:$VERSION

# 3. Push to Docker Hub
echo "3️⃣ Pushing to Docker Hub..."
docker push bharathadalla/calculator-backend:v2
docker push bharathadalla/calculator-backend:latest
docker push bharathadalla/calculator-backend:$VERSION
docker push bharathadalla/k8s-calculator-frontend:v2
docker push bharathadalla/k8s-calculator-frontend:latest
docker push bharathadalla/k8s-calculator-frontend:$VERSION

# 4. Create release notes
echo "4️⃣ Creating release notes..."
cat > RELEASE_v2.0.txt << EOF
Release: Calculator App v2.0
Date: $(date)
Version: $VERSION
Backend: bharathadalla/calculator-backend:$VERSION
Frontend: bharathadalla/k8s-calculator-frontend:$VERSION
Status: ✅ Production Ready
EOF

echo "✅ Docker Hub update complete!"
echo "📦 Images available:"
echo "   - bharathadalla/calculator-backend:latest"
echo "   - bharathadalla/calculator-backend:$VERSION"
echo "   - bharathadalla/k8s-calculator-frontend:latest"
echo "   - bharathadalla/k8s-calculator-frontend:$VERSION"
```

Save this script as `update-dockerhub.sh`, make it executable, and run it:

```bash
chmod +x update-dockerhub.sh
./update-dockerhub.sh
```

---

**Deployment Date**: December 20, 2025  
**Version**: 2.0  
**Status**: ✅ Ready to Deploy & Update Docker Hub
