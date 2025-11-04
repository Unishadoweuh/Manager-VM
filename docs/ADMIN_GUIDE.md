# Uni-Manager Administration Guide

## Table of Contents

1. [Initial Setup](#initial-setup)
2. [User Management](#user-management)
3. [Server Management](#server-management)
4. [Template Management](#template-management)
5. [Credit Management](#credit-management)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

## Initial Setup

### 1. First Admin User

The first admin user is created automatically on startup using environment variables:

```bash
FIRST_ADMIN_EMAIL=admin@yourdomain.com
FIRST_ADMIN_PASSWORD=changeme
```

**⚠️ IMPORTANT:** Change this password immediately after first login!

### 2. Configure Payment System (Optional)

If you want to enable payments:

```bash
ENABLE_PAYMENTS=true
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
```

If payments are disabled, you can manually credit user accounts.

### 3. Add Proxmox Servers

1. Navigate to **Admin Panel → Servers**
2. Click **Add Server**
3. Fill in details:
   - **Name:** Friendly name (e.g., "Proxmox-DC1")
   - **API URL:** https://your-proxmox.example.com:8006
   - **API Token:** PVEAPIToken=user@pam!tokenid=secret
   - **Verify SSL:** Enable for production
4. Click **Test Connection** to verify
5. Click **Save**

#### Creating Proxmox API Token

On your Proxmox server:

```bash
# Create a user
pveum user add apiuser@pve

# Create an API token
pveum user token add apiuser@pve automation --privsep=0

# Grant permissions
pveum acl modify / -user apiuser@pve -role PVEAdmin
```

Copy the token displayed and use it in Uni-Manager.

### 4. Create VM Templates

1. Navigate to **Admin Panel → Templates**
2. Click **Create Template**
3. Fill in template details:
   - **Name:** Ubuntu 22.04 - Small
   - **Description:** Ubuntu 22.04 LTS with 2 CPU
   - **CPU Cores:** 2
   - **RAM (MB):** 2048
   - **Disk (GB):** 20
   - **OS Type:** linux
   - **OS Name:** Ubuntu 22.04 LTS
   - **Cost per Hour:** 0.05
   - **Is Public:** Yes
   - **Is Active:** Yes
4. Click **Create**

## User Management

### Viewing Users

1. Navigate to **Admin Panel → Users**
2. View all users with their:
   - Email
   - Role (user/operator/admin)
   - Balance
   - Status (active/suspended/banned)
   - Registration date

### Adding Credits to User

**Method 1: Admin Panel UI**

1. Navigate to **Admin Panel → Users**
2. Click on the user
3. Click **Add Credits**
4. Enter:
   - **Amount:** 100.00
   - **Reason:** "Promotional credit"
5. Click **Confirm**

**Method 2: API**

```bash
curl -X POST https://yourdomain.com/api/v1/admin/users/5/credit \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 100.00,
    "reason": "Promotional credit"
  }'
```

**Method 3: Direct Database (Emergency)**

```bash
docker-compose exec postgres psql -U unimanager -d unimanager

-- Add $100 to user ID 5
UPDATE users SET balance = balance + 100.00 WHERE id = 5;

-- Create transaction record
INSERT INTO transactions (user_id, amount, type, description, balance_after, created_at)
SELECT 5, 100.00, 'admin_adjust', 'Emergency credit', balance, NOW()
FROM users WHERE id = 5;
```

### Banning Users

#### Temporary Ban

Ban user until a specific date:

1. Navigate to **Admin Panel → Users**
2. Click on the user
3. Click **Ban User**
4. Enter:
   - **Reason:** "Abuse of service"
   - **Ban Until:** 2025-12-31 23:59:59
5. Click **Confirm**

**Effects:**
- User cannot create new VMs
- User cannot start existing VMs
- User can still stop/view VMs
- Ban automatically expires on specified date

#### Permanent Ban

Ban user indefinitely:

1. Same as above but leave **Ban Until** empty
2. User remains banned until manually unbanned

**Effects:**
- Same as temporary ban
- No automatic expiration
- Requires manual unban

### Unbanning Users

1. Navigate to **Admin Panel → Users**
2. Click on banned user
3. Click **Unban User**
4. Enter reason: "Appeal approved"
5. Click **Confirm**

### Suspending Users

Suspend temporarily (manual unsuspend required):

```bash
# Via database
UPDATE users SET status = 'suspended' WHERE id = 5;
```

**Use cases:**
- Payment issues
- Investigation pending
- Policy violations

### Changing User Role

```bash
# Promote user to operator
UPDATE users SET role = 'operator' WHERE id = 5;

# Promote user to admin
UPDATE users SET role = 'admin' WHERE id = 5;

# Demote to regular user
UPDATE users SET role = 'user' WHERE id = 5;
```

## Server Management

### Monitoring Server Health

1. Navigate to **Admin Panel → Servers**
2. View server status:
   - 🟢 **Online:** Server is reachable
   - 🔴 **Offline:** Server is not reachable
   - ⚠️ **Error:** Connection error
   - 🔧 **Maintenance:** Manually set to maintenance mode

### Server Capacity

View resource usage:
- **CPU:** Used/Total cores
- **RAM:** Used/Total MB
- **Disk:** Used/Total GB

### Disabling VM Creation

Temporarily prevent new VMs on a server:

1. Navigate to **Admin Panel → Servers**
2. Click on server
3. Toggle **Allow VM Creation** to OFF
4. Click **Save**

**Use cases:**
- Maintenance window
- Resource constraints
- Migration in progress

### Server Priority

Set which server is preferred for new VMs:

1. Edit server
2. Set **Priority:** Higher number = preferred
3. Click **Save**

Example:
- Proxmox-DC1: Priority 10 (preferred)
- Proxmox-DC2: Priority 5 (fallback)
- Proxmox-Test: Priority 0 (avoid)

## Template Management

### Editing Template Pricing

1. Navigate to **Admin Panel → Templates**
2. Click on template
3. Edit **Cost per Hour**
4. Click **Save**

**Note:** New pricing applies to new VMs only. Existing VMs keep original pricing.

### Deactivating Templates

Prevent users from deploying a template:

1. Edit template
2. Toggle **Is Active** to OFF
3. Click **Save**

**Use cases:**
- Deprecated OS version
- Security vulnerabilities
- Temporary removal

### Making Templates Private

Hide template from regular users:

1. Edit template
2. Toggle **Is Public** to OFF
3. Click **Save**

**Use cases:**
- Admin-only templates
- Testing templates
- Special configurations

## Credit Management

### Viewing Transactions

1. Navigate to **Admin Panel → Users**
2. Click on user
3. View **Transaction History**

Transaction types:
- **credit:** Payment received
- **debit:** VM usage charge
- **admin_adjust:** Manual admin adjustment
- **refund:** Refund issued
- **payment:** Stripe/PayPal payment

### Refunding User

```bash
curl -X POST https://yourdomain.com/api/v1/admin/users/5/credit \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "reason": "Refund for downtime"
  }'
```

### Viewing All Transactions

```bash
# Via API
curl https://yourdomain.com/api/v1/admin/logs?limit=100 \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Via database
docker-compose exec postgres psql -U unimanager -d unimanager

SELECT * FROM transactions 
ORDER BY created_at DESC 
LIMIT 100;
```

## Monitoring

### Viewing Audit Logs

1. Navigate to **Admin Panel → Logs**
2. Filter by:
   - **Action:** (vm_created, user_banned, etc.)
   - **User:** Specific user ID
   - **Date Range:** Time period

Important actions logged:
- User registration/login
- VM creation/deletion
- Credit adjustments
- User bans
- Server additions
- Template changes

### System Health Dashboard

View real-time system health:

1. Navigate to **Admin Panel → Dashboard**
2. Monitor:
   - Total users
   - Active VMs
   - Server status
   - Recent activities

### Celery Task Monitoring

View background task status:

```bash
# View Celery worker logs
docker-compose logs -f celery-worker

# View Celery beat logs
docker-compose logs -f celery-beat

# Check task queue
docker-compose exec redis redis-cli LLEN celery
```

## Troubleshooting

### User Can't Create VMs

**Check:**
1. User balance > 0?
2. User status = active?
3. User not banned?
4. Available servers online?
5. Template is active?

**Solution:**
```bash
# Check user
SELECT id, email, balance, status, ban_reason 
FROM users WHERE id = 5;

# Add credits if needed
-- See "Adding Credits to User" above

# Check servers
SELECT id, name, status, is_active, allow_vm_creation 
FROM servers;
```

### Billing Not Working

**Check:**
```bash
# View Celery worker logs
docker-compose logs celery-worker | grep billing

# Check if auto-billing is enabled
grep ENABLE_AUTO_BILLING .env

# Manually trigger billing
docker-compose exec backend python -c "
from app.tasks.billing import process_vm_billing
process_vm_billing()
"
```

### Server Connection Failed

**Check:**
1. API URL correct?
2. API token valid?
3. Network connectivity?
4. Proxmox server running?
5. Firewall rules?

**Test:**
```bash
# From backend container
docker-compose exec backend curl -k \
  https://proxmox.example.com:8006/api2/json/version \
  -H "Authorization: PVEAPIToken=user@pam!token=secret"
```

### Database Full

**Cleanup old logs:**
```bash
# Delete logs older than 1 year
docker-compose exec postgres psql -U unimanager -d unimanager

DELETE FROM logs 
WHERE created_at < NOW() - INTERVAL '365 days';

VACUUM ANALYZE logs;
```

### Reset Admin Password

```bash
docker-compose exec postgres psql -U unimanager -d unimanager

-- Generate new hash for "newpassword123"
-- Use bcrypt hash generator or Python:
-- from passlib.context import CryptContext
-- CryptContext(schemes=["bcrypt"]).hash("newpassword123")

UPDATE users 
SET password_hash = '$2b$12$...' 
WHERE email = 'admin@yourdomain.com';
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U unimanager unimanager > backup_$(date +%Y%m%d).sql

# Restore backup
cat backup_20251104.sql | docker-compose exec -T postgres psql -U unimanager unimanager
```

## Best Practices

1. **Regular Backups:** Daily database backups
2. **Monitor Logs:** Check audit logs regularly
3. **Update Pricing:** Review template pricing monthly
4. **Server Health:** Monitor server capacity weekly
5. **User Balance:** Set low-balance alerts
6. **Security:** Rotate API tokens quarterly
7. **Updates:** Keep Docker images updated
8. **Testing:** Test new templates before making public
9. **Documentation:** Document custom configurations
10. **Support:** Maintain user support channels

## Security Checklist

- [ ] Admin password changed from default
- [ ] Unique SECRET_KEY and ENCRYPTION_KEY set
- [ ] HTTPS enabled (Caddy auto-configures)
- [ ] Firewall configured (only 80, 443 open)
- [ ] Proxmox API tokens use least privilege
- [ ] SSL certificate verification enabled for Proxmox
- [ ] Regular security updates applied
- [ ] Audit logs reviewed monthly
- [ ] Database backups automated
- [ ] Rate limiting enabled
