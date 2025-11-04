# Uni-Manager Security Guide

## Security Architecture

Uni-Manager implements defense-in-depth security with multiple layers of protection.

## Authentication & Authorization

### JWT Tokens

**Access Tokens:**
- Expiration: 30 minutes (configurable)
- Used for API authentication
- Stored in memory (not localStorage)
- Includes: user_id, expiration, token_type

**Refresh Tokens:**
- Expiration: 7 days (configurable)
- Used to obtain new access tokens
- Stored securely (httpOnly cookies recommended)
- Rotated on each refresh

### Password Security

**Hashing:**
- Algorithm: bcrypt
- Work factor: 12 rounds (2^12 = 4096 iterations)
- Salted automatically

**Password Requirements:**
- Minimum length: 8 characters
- Enforced at API level via Pydantic validators

**Recommendations for Production:**
```python
# Add to schemas/auth.py
class UserRegister(BaseModel):
    password: str = Field(
        ..., 
        min_length=12,
        regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])'
    )
```

### Rate Limiting

**Login Attempts:**
- Max: 5 attempts per 5 minutes
- Per: Email address
- Storage: Redis
- Response: HTTP 429

**Implementation:**
```python
# Rate limit key: "login:{email}"
# Automatic reset after successful login
```

### Role-Based Access Control (RBAC)

**Roles:**

1. **User:**
   - Create/manage own VMs
   - View own transactions
   - Update own profile

2. **Operator:**
   - All User permissions
   - View all VMs
   - View server status
   - Basic monitoring

3. **Admin:**
   - All Operator permissions
   - Manage users (credit, ban, unban)
   - Manage servers
   - Manage templates
   - View audit logs
   - System configuration

**Permission Checks:**
```python
# Enforced via FastAPI dependencies
@app.get("/admin/users")
async def list_users(
    current_admin: User = Depends(get_current_admin_user)
):
    # Only admins can access
```

## Data Encryption

### At Rest

**Proxmox API Tokens:**
- Encrypted using Fernet (symmetric encryption)
- Encryption key from environment variable
- Never stored in plain text

**Generating Encryption Key:**
```bash
# Generate a secure encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Database:**
- Passwords: bcrypt hashed
- API tokens: Fernet encrypted
- Sensitive fields: Encrypted as needed

### In Transit

**TLS/SSL:**
- Caddy handles automatic HTTPS
- Let's Encrypt certificates
- TLS 1.2+ only
- Strong cipher suites

**Internal Communication:**
- Backend ↔ Database: Encrypted via PostgreSQL SSL
- Backend ↔ Redis: Can be encrypted (redis-tls)
- Backend ↔ Proxmox: HTTPS (configurable verify_ssl)

## Input Validation

### API Layer

**Pydantic Schemas:**
- All inputs validated against schemas
- Type checking enforced
- SQL injection prevention via ORM
- XSS prevention via output encoding

**Example:**
```python
class VMCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, regex=r'^[a-zA-Z0-9-_]+$')
    cpu_cores: int = Field(..., ge=1, le=16)
    ram_mb: int = Field(..., ge=512, le=65536)
```

### Database Layer

**SQLAlchemy ORM:**
- Parameterized queries
- No raw SQL (unless necessary)
- Input sanitization

## CORS Policy

**Configuration:**
```bash
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

**Settings:**
- Credentials: Allowed
- Methods: Restricted to necessary methods
- Headers: Validated

**Production:**
```python
# Strict CORS - only production domains
allow_origins=["https://yourdomain.com"]
allow_credentials=True
allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
```

## Audit Logging

### What is Logged

**All Security-Relevant Actions:**
- User login/logout
- Failed login attempts
- User registration
- Password changes
- Role changes
- User bans/unbans
- VM creation/deletion
- Credit additions
- Server additions
- Template changes
- API errors

**Log Fields:**
- Timestamp (UTC)
- User ID
- Action
- IP address
- User agent
- Details (JSON)
- Status (success/error)

### Log Retention

**Default:** 365 days

**Compliance:**
- Immutable logs (append-only)
- No deletion by non-admins
- Regular backups

**Configuration:**
```bash
LOG_RETENTION_DAYS=365
```

**Cleanup:**
```sql
-- Automated cleanup (via Celery task)
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '365 days';
```

## Security Headers

**Caddy Configuration:**
```
header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "DENY"
    X-XSS-Protection "1; mode=block"
    Referrer-Policy "strict-origin-when-cross-origin"
    Permissions-Policy "geolocation=(), microphone=(), camera=()"
}
```

## Secure Configuration

### Environment Variables

**Never Commit:**
- `.env` file
- Secret keys
- Database passwords
- API tokens

**Git Ignore:**
```
.env
.env.*
!.env.example
```

### Secrets Management

**Development:**
```bash
# Generate secure random values
openssl rand -hex 32  # SECRET_KEY
openssl rand -base64 32  # ENCRYPTION_KEY
openssl rand -base64 24  # POSTGRES_PASSWORD
```

**Production Options:**
1. Environment variables (Docker secrets)
2. HashiCorp Vault
3. AWS Secrets Manager
4. Azure Key Vault

### Docker Security

**Non-Root Users:**
```dockerfile
# Backend
RUN useradd -m -u 1000 appuser
USER appuser

# Frontend
RUN adduser --system --uid 1001 nextjs
USER nextjs
```

**Read-Only Filesystems:**
```yaml
# docker-compose.yml
services:
  backend:
    read_only: true
    tmpfs:
      - /tmp
```

## Network Security

### Firewall Rules

**Minimal Exposure:**
```bash
# UFW example
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   # SSH (restrict to known IPs)
ufw allow 80/tcp   # HTTP (redirect to HTTPS)
ufw allow 443/tcp  # HTTPS
ufw enable
```

### Internal Network

**Docker Network Isolation:**
```yaml
networks:
  unimanager-network:
    driver: bridge
    internal: false  # Only web-facing services exposed
```

**Service Communication:**
- Frontend → Backend: Via Caddy reverse proxy
- Backend → Database: Internal Docker network
- Backend → Redis: Internal Docker network
- Backend → Proxmox: External (HTTPS)

## Vulnerability Management

### Dependency Updates

**Regular Updates:**
```bash
# Backend
pip list --outdated
pip install --upgrade -r requirements.txt

# Frontend
npm outdated
npm update
```

**Automated Scanning:**
- Dependabot (GitHub)
- Snyk
- Safety (Python)

### Security Scanning

**Docker Images:**
```bash
# Scan images for vulnerabilities
docker scan unimanager-backend:latest
docker scan unimanager-frontend:latest
```

**Code Scanning:**
```bash
# Python
bandit -r app/

# Static analysis
pylint app/
```

## Incident Response

### Detecting Breaches

**Monitor For:**
- Unusual login patterns
- Failed login spikes
- Unauthorized role changes
- Suspicious VM creation
- Database access anomalies

**Alerts:**
```python
# Set up alerts for:
# - Multiple failed logins
# - Admin account creation
# - Large credit adjustments
# - API rate limit hits
```

### Response Steps

**If Compromised:**

1. **Immediate:**
   - Rotate all secrets (SECRET_KEY, ENCRYPTION_KEY)
   - Invalidate all JWT tokens
   - Reset admin passwords
   - Block suspicious IPs

2. **Investigation:**
   - Review audit logs
   - Check transactions
   - Identify affected users
   - Assess data exposure

3. **Recovery:**
   - Restore from clean backup
   - Notify affected users
   - Document incident
   - Update security measures

4. **Post-Incident:**
   - Conduct post-mortem
   - Update security policies
   - Train staff
   - Improve monitoring

## Compliance

### GDPR Considerations

**Data Minimization:**
- Collect only necessary data
- No unnecessary tracking

**Right to Erasure:**
```python
# User deletion endpoint
@router.delete("/user/me")
async def delete_account(user: User = Depends(get_current_user)):
    # Soft delete or anonymize
    user.email = f"deleted_{user.id}@deleted.local"
    user.status = UserStatus.DELETED
    # Retain for legal/billing purposes, then purge
```

**Data Export:**
```python
@router.get("/user/export")
async def export_data(user: User = Depends(get_current_user)):
    # Export all user data in machine-readable format
    return {
        "user": user,
        "vms": user.vms,
        "transactions": user.transactions
    }
```

### PCI DSS (If Processing Payments)

**Stripe/PayPal:**
- Never store card details
- Use tokenization
- Webhook signature verification
- PCI-compliant payment gateway

## Security Checklist

### Deployment

- [ ] All default passwords changed
- [ ] Unique SECRET_KEY generated
- [ ] Unique ENCRYPTION_KEY generated
- [ ] Strong database password set
- [ ] HTTPS enabled and working
- [ ] SSL certificates valid
- [ ] Firewall configured
- [ ] Docker running as non-root
- [ ] Environment variables secured
- [ ] `.env` not in version control

### Configuration

- [ ] CORS origins restricted to production domains
- [ ] Rate limiting enabled
- [ ] Session timeout configured
- [ ] Password complexity enforced
- [ ] API token rotation policy
- [ ] Backup strategy implemented
- [ ] Log retention configured
- [ ] Monitoring alerts set up

### Operations

- [ ] Regular security updates scheduled
- [ ] Dependency scanning automated
- [ ] Audit logs reviewed monthly
- [ ] Backups tested quarterly
- [ ] Incident response plan documented
- [ ] Security training for admins
- [ ] Access control reviewed quarterly
- [ ] Penetration testing (annually)

### Monitoring

- [ ] Failed login alerts
- [ ] Unusual activity alerts
- [ ] Resource usage alerts
- [ ] Error rate monitoring
- [ ] Audit log analysis
- [ ] Database backup verification
- [ ] SSL certificate expiry alerts

## Reporting Security Issues

**Please report security vulnerabilities to:**
- Email: security@yourdomain.com
- Do not open public GitHub issues for security bugs

**Include:**
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

**Response:**
- Acknowledgment: 24 hours
- Initial assessment: 72 hours
- Fix timeline: Based on severity
- Credit: In security advisory (if desired)

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
