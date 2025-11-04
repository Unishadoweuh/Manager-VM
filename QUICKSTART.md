# Uni-Manager - Quick Start Guide

## 🚀 5-Minute Setup

Get Uni-Manager running in under 5 minutes!

### Prerequisites

- Docker & Docker Compose installed
- Domain name pointing to your server (for production)
- Proxmox VE server with API access (optional for initial setup)

### Step 1: Clone & Configure

```bash
# Clone the repository (or download the files)
cd /opt
git clone <repository-url> uni-manager
cd uni-manager

# Copy environment template
cp .env.example .env

# Generate secure keys
export SECRET_KEY=$(openssl rand -hex 32)
export ENCRYPTION_KEY=$(openssl rand -base64 32)
export POSTGRES_PASSWORD=$(openssl rand -base64 24)

# Update .env with generated keys (Linux/Mac)
sed -i "s/CHANGE_THIS_TO_A_RANDOM_64_CHARACTER_STRING.*/$SECRET_KEY/" .env
sed -i "s/CHANGE_THIS_TO_A_32_BYTE_KEY.*/$ENCRYPTION_KEY/" .env
sed -i "s/change_this_secure_password/$POSTGRES_PASSWORD/" .env

# Update domain
sed -i "s/yourdomain.com/manager.example.com/" .env

# Update admin credentials
nano .env  # Edit FIRST_ADMIN_EMAIL and FIRST_ADMIN_PASSWORD
```

### Step 2: Launch

```bash
# Build and start all services
docker-compose up -d

# Wait for services to initialize (30-60 seconds)
docker-compose ps

# Check logs
docker-compose logs -f backend
```

### Step 3: Access

```bash
# Development (no domain)
http://localhost:3000

# Production (with domain)
https://manager.example.com
```

**Login:**
- Email: (from FIRST_ADMIN_EMAIL)
- Password: (from FIRST_ADMIN_PASSWORD)

### Step 4: Initial Configuration

1. **Change Admin Password**
   - Settings → Security → Change Password

2. **Add Proxmox Server**
   - Admin Panel → Servers → Add Server
   - Name: Proxmox-01
   - API URL: https://your-proxmox:8006
   - API Token: PVEAPIToken=user@pam!token=secret
   - Click "Test Connection"
   - Save

3. **Create VM Templates**
   - Admin Panel → Templates → Create Template
   - Use sample templates or create custom

4. **Create Test User** (Optional)
   - Run seed script: `docker-compose exec backend python -m app.scripts.seed_db`
   - Or register via UI

5. **Add Credits to Test User**
   - Admin Panel → Users → Select User → Add Credits
   - Amount: 50.00
   - Reason: "Initial test credit"

### Step 5: Test VM Creation

1. Login as test user
2. Navigate to Templates
3. Select a template
4. Click "Deploy"
5. Fill in VM details
6. Click "Create VM"

---

## Example Usage Flow

### Scenario: New User Registration → Deploy VM

**1. User Registration**

```bash
curl -X POST https://manager.example.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

**2. Admin Adds Credits (Manual Mode)**

```bash
# Get admin token first
ADMIN_TOKEN=$(curl -X POST https://manager.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"adminpass"}' | jq -r .access_token)

# Add credits to new user
curl -X POST https://manager.example.com/api/v1/admin/users/2/credit \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "reason": "Welcome bonus"
  }'
```

**3. User Checks Balance**

```bash
USER_TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl https://manager.example.com/api/v1/user/credits \
  -H "Authorization: Bearer $USER_TOKEN"
```

**Response:**
```json
{
  "balance": "50.00",
  "currency": "USD"
}
```

**4. User Lists Available Templates**

```bash
curl https://manager.example.com/api/v1/templates \
  -H "Authorization: Bearer $USER_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Ubuntu 22.04 - Small",
    "cpu_cores": 2,
    "ram_mb": 2048,
    "disk_gb": 20,
    "os_name": "Ubuntu 22.04 LTS",
    "cost_per_hour": "0.0500",
    "cost_per_day": 1.20,
    "cost_per_month": 36.00
  }
]
```

**5. User Deploys VM**

```bash
curl -X POST https://manager.example.com/api/v1/vms \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "template_id": 1,
    "name": "my-web-server",
    "hostname": "web01.local",
    "notes": "Production web server"
  }'
```

**Response:**
```json
{
  "id": 1,
  "name": "my-web-server",
  "state": "creating",
  "template_id": 1,
  "cpu_cores": 2,
  "ram_mb": 2048,
  "disk_gb": 20,
  "created_at": "2025-11-04T10:00:00Z"
}
```

**6. User Checks VM Status**

```bash
curl https://manager.example.com/api/v1/vms/1 \
  -H "Authorization: Bearer $USER_TOKEN"
```

**7. User Starts VM**

```bash
curl -X POST https://manager.example.com/api/v1/vms/1/action \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

**8. Automatic Billing**

Celery worker bills the VM every hour:
- Checks if VM is running
- Calculates cost: hours × template.cost_per_hour
- Deducts from user balance
- Creates transaction record

**9. User Views Transactions**

```bash
curl https://manager.example.com/api/v1/user/transactions \
  -H "Authorization: Bearer $USER_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "amount": "50.00",
    "type": "admin_adjust",
    "description": "Welcome bonus",
    "balance_after": "50.00",
    "created_at": "2025-11-04T10:00:00Z"
  },
  {
    "id": 2,
    "amount": "-0.05",
    "type": "debit",
    "description": "VM usage: my-web-server (1.00 hours)",
    "balance_after": "49.95",
    "created_at": "2025-11-04T11:00:00Z"
  }
]
```

---

## Testing Checklist

### ✅ After Installation

- [ ] All containers running: `docker-compose ps`
- [ ] Backend healthy: `curl http://localhost:8000/api/v1/health`
- [ ] Frontend accessible: `curl http://localhost:3000`
- [ ] Database accessible: `docker-compose exec postgres psql -U unimanager`
- [ ] Redis accessible: `docker-compose exec redis redis-cli ping`

### ✅ After Configuration

- [ ] Admin login works
- [ ] Admin password changed
- [ ] Proxmox server added and online
- [ ] Templates created
- [ ] Test user created
- [ ] Test user has credits

### ✅ Functional Tests

- [ ] User can register (if enabled)
- [ ] User can login
- [ ] User can view templates
- [ ] User can deploy VM (mock or real)
- [ ] User can start/stop VM
- [ ] User can view transactions
- [ ] Admin can add credits
- [ ] Admin can ban/unban users
- [ ] Billing task runs (check logs)

---

## Common Issues

### 1. Containers Won't Start

```bash
# Check logs
docker-compose logs

# Common fixes:
# - Port already in use: Change ports in docker-compose.yml
# - Permission denied: Run with sudo or add user to docker group
# - Database won't start: Check POSTGRES_PASSWORD in .env
```

### 2. Can't Login

```bash
# Verify admin user exists
docker-compose exec postgres psql -U unimanager -d unimanager -c "SELECT email, role FROM users;"

# Recreate admin user
docker-compose exec backend python -m app.scripts.create_admin
```

### 3. Proxmox Connection Failed

```bash
# Test from backend container
docker-compose exec backend curl -k https://your-proxmox:8006/api2/json/version \
  -H "Authorization: PVEAPIToken=user@pam!token=secret"

# Common issues:
# - Firewall blocking port 8006
# - Invalid API token
# - SSL verification failing (set verify_ssl=false for testing)
```

### 4. Billing Not Working

```bash
# Check if enabled
grep ENABLE_AUTO_BILLING .env

# Check Celery worker
docker-compose logs celery-worker

# Manually trigger billing
docker-compose exec backend python -c "from app.tasks.billing import process_vm_billing; process_vm_billing()"
```

### 5. Frontend Can't Connect to Backend

```bash
# Check NEXT_PUBLIC_API_URL in .env
grep NEXT_PUBLIC_API_URL .env

# Should be:
# Development: http://localhost:8000/api
# Production: https://yourdomain.com/api

# Rebuild frontend
docker-compose build frontend
docker-compose restart frontend
```

---

## Next Steps

1. **Production Deployment:**
   - Set up proper domain with DNS
   - Configure SSL (automatic with Caddy)
   - Enable firewall
   - Set up backups
   - Configure monitoring

2. **Enable Payments:**
   - Set ENABLE_PAYMENTS=true
   - Add Stripe/PayPal credentials
   - Configure webhooks

3. **Customize:**
   - Add custom templates
   - Configure pricing
   - Set up quotas
   - Customize branding

4. **Scale:**
   - Add more Proxmox servers
   - Configure load balancing
   - Set up high availability
   - Add monitoring (Prometheus/Grafana)

---

## Support

- **Documentation:** `/docs` folder
- **API Docs:** https://yourdomain.com/api/v1/docs
- **Logs:** `docker-compose logs -f`
- **Database:** `docker-compose exec postgres psql -U unimanager`

**Need Help?**
- Check documentation: `/docs/ADMIN_GUIDE.md`
- Review API docs: `/docs/API.md`
- Check security guide: `/docs/SECURITY.md`
