#!/bin/bash
# Uni-Manager Installation Script for Debian/Ubuntu
# This script installs Uni-Manager on a fresh Debian or Ubuntu server

set -e  # Exit on error

echo "========================================="
echo "   Uni-Manager Installation Script"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "ERROR: Please run as root (use sudo)"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo "ERROR: Cannot detect OS"
    exit 1
fi

echo "Detected OS: $OS $VERSION"
echo ""

# Update system
echo "📦 Updating system packages..."
apt-get update
apt-get upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
apt-get install -y \
    curl \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    apt-transport-https \
    software-properties-common

# Install Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    
    # Add Docker's official GPG key
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    # Set up the repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    echo "✓ Docker installed successfully"
else
    echo "✓ Docker is already installed"
fi

# Install Docker Compose (standalone)
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "✓ Docker Compose installed successfully"
else
    echo "✓ Docker Compose is already installed"
fi

# Create installation directory
INSTALL_DIR="/opt/uni-manager"
echo "📁 Creating installation directory: $INSTALL_DIR"
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    
    # Generate random secrets
    SECRET_KEY=$(openssl rand -hex 32)
    ENCRYPTION_KEY=$(openssl rand -base64 32)
    POSTGRES_PASSWORD=$(openssl rand -base64 24)
    
    # Prompt for domain
    read -p "Enter your domain name (e.g., manager.example.com): " DOMAIN
    
    # Prompt for admin email
    read -p "Enter admin email: " ADMIN_EMAIL
    
    # Prompt for admin password
    read -sp "Enter admin password: " ADMIN_PASSWORD
    echo ""
    
    # Create .env file
    cat > .env <<EOF
# Environment
NODE_ENV=production
ENVIRONMENT=production

# Database
POSTGRES_USER=unimanager
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=unimanager
DATABASE_URL=postgresql://unimanager:$POSTGRES_PASSWORD@postgres:5432/unimanager

# Redis
REDIS_URL=redis://redis:6379/0

# Backend API
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
API_V1_PREFIX=/api/v1
PROJECT_NAME=Uni-Manager

# Security
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ENCRYPTION_KEY=$ENCRYPTION_KEY

# CORS
BACKEND_CORS_ORIGINS=https://$DOMAIN,http://localhost:3000

# Frontend
NEXT_PUBLIC_API_URL=https://$DOMAIN/api
NEXT_PUBLIC_WS_URL=wss://$DOMAIN/ws

# Feature Flags
ENABLE_PAYMENTS=false
ENABLE_AUTO_BILLING=true
ENABLE_AUTO_SHUTDOWN=true
ENABLE_REGISTRATION=true

# Rate Limiting
RATE_LIMIT_LOGIN_ATTEMPTS=5
RATE_LIMIT_LOGIN_WINDOW=300

# Billing
BILLING_CYCLE_MINUTES=60
MIN_BALANCE_THRESHOLD=0

# Audit Logs
LOG_RETENTION_DAYS=365

# Admin
FIRST_ADMIN_EMAIL=$ADMIN_EMAIL
FIRST_ADMIN_PASSWORD=$ADMIN_PASSWORD

# Domain
DOMAIN=$DOMAIN
EOF
    
    echo "✓ .env file created"
else
    echo "✓ .env file already exists"
fi

# Clone or update repository
if [ -d ".git" ]; then
    echo "📥 Updating Uni-Manager..."
    git pull
else
    echo "📥 Cloning Uni-Manager repository..."
    # If you have files locally, skip this
    echo "⚠️  Please ensure all Uni-Manager files are in $INSTALL_DIR"
fi

# Build and start containers
echo "🚀 Building and starting Docker containers..."
docker-compose down || true
docker-compose build
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

echo ""
echo "========================================="
echo "   ✅ Installation Complete!"
echo "========================================="
echo ""
echo "Uni-Manager has been installed successfully!"
echo ""
echo "Access your installation:"
echo "  URL: https://$DOMAIN"
echo "  Admin Email: $ADMIN_EMAIL"
echo ""
echo "Next steps:"
echo "  1. Configure DNS to point $DOMAIN to this server"
echo "  2. Wait a few moments for SSL certificate provisioning"
echo "  3. Log in with admin credentials"
echo "  4. Add Proxmox servers in Admin Panel"
echo "  5. Create VM templates"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop: docker-compose stop"
echo "  Start: docker-compose start"
echo "  Restart: docker-compose restart"
echo ""
echo "Documentation: https://github.com/yourusername/uni-manager"
echo ""
