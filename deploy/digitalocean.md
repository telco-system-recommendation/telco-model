# DigitalOcean Deployment Guide

## Prerequisites

1. **DigitalOcean Account**: Sign up at [digitalocean.com](https://digitalocean.com)
2. **Docker Installed**: On your local machine
3. **doctl CLI** (optional): DigitalOcean command-line tool

---

## Option 1: Deploy to DigitalOcean App Platform (Easiest)

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add Docker configuration"
git push origin feat/fastAPI-implementation
```

### Step 2: Create App on DigitalOcean

1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click **"Create App"**
3. Connect your GitHub repository: `telco-system-recommendation/telco-model`
4. Select branch: `feat/fastAPI-implementation`
5. DigitalOcean will auto-detect the Dockerfile

### Step 3: Configure App Settings

**Resources**:
- **Type**: Web Service
- **Dockerfile Path**: `Dockerfile`
- **HTTP Port**: 8000
- **Instance Size**: Basic ($12/month) or Professional ($24/month)

**Environment Variables**:
```
RETRAIN_THRESHOLD=1000
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

**Health Check**:
- **Path**: `/health`
- **Initial Delay**: 30 seconds

### Step 4: Deploy
- Click **"Next"** → **"Create Resources"**
- Wait 5-10 minutes for deployment
- Your API will be available at: `https://your-app-name.ondigitalocean.app`

---

## Option 2: Deploy to DigitalOcean Droplet (More Control)

### Step 1: Create Droplet

```bash
# Using doctl CLI
doctl compute droplet create telco-model \
  --image docker-20-04 \
  --size s-2vcpu-4gb \
  --region sgp1 \
  --ssh-keys YOUR_SSH_KEY_ID
```

Or via Web UI:
1. Go to [Create Droplet](https://cloud.digitalocean.com/droplets/new)
2. **Image**: Docker on Ubuntu 22.04
3. **Plan**: Basic ($24/month - 2 vCPU, 4GB RAM)
4. **Region**: Choose closest to your users
5. **Add SSH Keys**
6. Click **"Create Droplet"**

### Step 2: SSH into Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

### Step 3: Deploy Application

```bash
# Clone repository
git clone https://github.com/telco-system-recommendation/telco-model.git
cd telco-model

# Checkout the correct branch
git checkout feat/fastAPI-implementation

# Create .env file
cp .env.example .env
nano .env  # Edit as needed

# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Step 4: Configure Firewall

```bash
# Allow HTTP, HTTPS, and SSH
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw enable
```

### Step 5: Set up Nginx Reverse Proxy (Optional but Recommended)

```bash
# Install Nginx
apt update
apt install -y nginx certbot python3-certbot-nginx

# Create Nginx configuration
cat > /etc/nginx/sites-available/telco-model << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
ln -s /etc/nginx/sites-available/telco-model /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Setup SSL (if you have a domain)
certbot --nginx -d your-domain.com
```

---

## Option 3: Deploy to DigitalOcean Container Registry + Kubernetes

### Step 1: Create Container Registry

```bash
# Create registry
doctl registry create telco-model-registry

# Login to registry
doctl registry login
```

### Step 2: Build and Push Image

```bash
# Tag image
docker build -t registry.digitalocean.com/telco-model-registry/telco-api:latest .

# Push to registry
docker push registry.digitalocean.com/telco-model-registry/telco-api:latest
```

### Step 3: Create Kubernetes Cluster

```bash
doctl kubernetes cluster create telco-cluster \
  --region sgp1 \
  --node-pool "name=worker-pool;size=s-2vcpu-4gb;count=2"
```

### Step 4: Deploy to Kubernetes

See `k8s/` folder for Kubernetes manifests.

---

## Testing Deployment

### Test API Endpoint

```bash
# Health check
curl https://your-app-url/health

# Make prediction
curl -X POST https://your-app-url/predict \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": [[0.5, 0.3, 0.7, 0.2, 0.8, 0.1, 0.9, 0.4, 0.6, 0.5, 0.3, 0.7, 0.2, 0.8, 0.1, 0.9, 0.4, 0.6, 0.5, 0.3, 0.7, 0.2, 0.8, 0.1, 0.9]]
  }'

# Check retrain status
curl https://your-app-url/retrain/status
```

---

## Monitoring & Maintenance

### View Logs

```bash
# Docker Compose
docker-compose logs -f

# App Platform
# Use DigitalOcean dashboard: Apps → Your App → Runtime Logs

# Kubernetes
kubectl logs -f deployment/telco-model-api
```

### Monitor Resources

```bash
# Docker stats
docker stats

# Droplet monitoring
# Use DigitalOcean dashboard: Droplets → Metrics
```

### Backup Data

```bash
# Backup retrain data
docker exec telco-model-api tar czf /tmp/retrain-backup.tar.gz /app/data/retrain
docker cp telco-model-api:/tmp/retrain-backup.tar.gz ./backups/

# Backup model
docker cp telco-model-api:/app/model ./backups/model-$(date +%Y%m%d)
```

### Update Application

```bash
# Pull latest changes
git pull origin feat/fastAPI-implementation

# Rebuild and restart
docker-compose down
docker-compose up -d --build

# Or for App Platform
git push origin feat/fastAPI-implementation
# Auto-deploys in 5-10 minutes
```

---

## Cost Estimation

### App Platform
- **Basic**: $12/month (512MB RAM, 1 vCPU)
- **Professional**: $24/month (1GB RAM, 1 vCPU)
- **Recommended**: Professional for ML workloads

### Droplet
- **Basic**: $24/month (4GB RAM, 2 vCPU)
- **General Purpose**: $48/month (8GB RAM, 2 vCPU)
- **Recommended**: Basic for small-medium traffic

### Container Registry
- **Free**: 500MB storage
- **Starter**: $5/month (5GB storage)

### Kubernetes
- **Cluster**: Free (control plane)
- **Worker Nodes**: $24/month each (4GB RAM, 2 vCPU)
- **Minimum**: 2 nodes = $48/month

---

## Production Recommendations

1. **Enable SSL**: Use Let's Encrypt (free) or DigitalOcean certificates
2. **Set up Monitoring**: Use DigitalOcean Monitoring or external tools
3. **Configure Backups**: Enable automatic backups for Droplets
4. **Use Managed Database**: For production data storage (PostgreSQL)
5. **Set up CI/CD**: GitHub Actions for automated deployments
6. **Enable Logging**: Send logs to external service (Papertrail, Loggly)
7. **Rate Limiting**: Protect API from abuse
8. **API Authentication**: Add JWT or API key authentication

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker logs telco-model-api

# Check if port is in use
netstat -tulpn | grep 8000

# Verify model files exist
docker exec telco-model-api ls -la /app/model/
```

### Out of Memory
```bash
# Increase Droplet size or
# Reduce model size or
# Add swap space
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

### Slow Predictions
- Upgrade to larger Droplet
- Enable model caching
- Use Redis for frequent predictions
- Consider GPU instances for heavy workloads

---

## Support

- **DigitalOcean Docs**: https://docs.digitalocean.com
- **Community**: https://www.digitalocean.com/community
- **Support Tickets**: Available for paid accounts

---

## Next Steps

1. ✅ Build Docker image locally: `docker build -t telco-model .`
2. ✅ Test locally: `docker run -p 8000:8000 telco-model`
3. ✅ Push to GitHub
4. ✅ Deploy to DigitalOcean App Platform
5. ✅ Configure domain and SSL
6. ✅ Set up monitoring
7. ✅ Enable backups
