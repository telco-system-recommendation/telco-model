#!/bin/bash
# Setup script for DigitalOcean Droplet
# Run this after SSH into your droplet: bash setup-droplet.sh

set -e

echo "🚀 Setting up Telco Model API on DigitalOcean Droplet..."

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Install useful tools
echo "🔧 Installing additional tools..."
apt install -y git curl wget htop ufw

# Configure firewall
echo "🔒 Configuring firewall..."
ufw --force enable
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw allow 8000/tcp # API (optional, if not using nginx)

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /opt/telco-model
cd /opt/telco-model

# Clone repository (you'll need to configure SSH keys or use HTTPS with token)
echo "📥 Ready to clone repository..."
echo "Run: git clone https://github.com/telco-system-recommendation/telco-model.git ."
echo "Then: git checkout feat/fastAPI-implementation"

# Create data directories
mkdir -p data/retrain/logs data/retrain/backups

# Create .env file
cat > .env << 'EOF'
# API Configuration
RETRAIN_THRESHOLD=1000
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1

# Add your custom configuration here
EOF

echo "✅ Basic setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone the repository: git clone https://github.com/telco-system-recommendation/telco-model.git ."
echo "2. Checkout branch: git checkout feat/fastAPI-implementation"
echo "3. Edit .env file: nano .env"
echo "4. Start application: docker-compose up -d"
echo "5. View logs: docker-compose logs -f"
echo ""
echo "Optional: Install Nginx reverse proxy"
echo "  apt install -y nginx certbot python3-certbot-nginx"
echo "  Copy deploy/nginx.conf to /etc/nginx/sites-available/telco-model"
echo ""
