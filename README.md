# Uni-Manager

A production-ready, self-service VM management platform built on Proxmox with credit-based billing, multi-server support, and advanced administration.

## 🚀 Features

- **User Management**: Registration, JWT authentication, password recovery, role-based access (admin/operator/user)
- **Credit System**: Prepaid/postpaid billing, automatic deduction, manual admin credits
- **VM Lifecycle**: Deploy from templates, start/stop/reboot/resize/snapshot/backup/delete, noVNC console
- **Templates**: Pre-configured VM templates with cost estimation
- **Multi-Server**: Manage multiple Proxmox nodes from one interface
- **Administration**: User management, server management, banning (temporary/permanent), audit logs
- **Monitoring**: Real-time metrics via WebSocket, historical graphs
- **Payments**: Stripe/PayPal integration (optional, can be disabled)
- **Security**: Encrypted Proxmox tokens, rate limiting, CSRF protection, audit trail

## 📋 Prerequisites

- Docker & Docker Compose
- Domain name (for production with HTTPS)
- Proxmox VE server(s) with API access
- (Optional) Stripe/PayPal account for payments

## 🛠️ Quick Start

### 1. Clone and Configure

```bash
git clone <repository-url> uni-manager
cd uni-manager
cp .env.example .env
```

### 2. Edit Environment Variables

Edit `.env` and update:

```bash
# Required
SECRET_KEY=<generate with: openssl rand -hex 32>
ENCRYPTION_KEY=<generate with: openssl rand -base64 32>
POSTGRES_PASSWORD=<secure-password>
FIRST_ADMIN_EMAIL=admin@yourdomain.com
FIRST_ADMIN_PASSWORD=<secure-password>
DOMAIN=yourdomain.com

# Optional (if payments enabled)
ENABLE_PAYMENTS=true
STRIPE_SECRET_KEY=sk_live_...
```

### 3. Launch Application

```bash
docker-compose up -d
```

Wait for all services to be healthy:

```bash
docker-compose ps
```

### 4. Access Application

- **Frontend**: https://yourdomain.com (or http://localhost:3000 for dev)
- **API Docs**: https://yourdomain.com/api/docs
- **Admin Login**: Use credentials from `FIRST_ADMIN_EMAIL` and `FIRST_ADMIN_PASSWORD`

## 📁 Project Structure

```
uni-manager/
├── backend/          # FastAPI application
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Configuration, security, database
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   ├── services/ # Business logic
│   │   ├── tasks/    # Celery tasks
│   │   └── scripts/  # Admin scripts
│   └── tests/        # Unit tests
├── frontend/         # Next.js application
│   └── src/
│       ├── app/      # Pages (App Router)
│       ├── components/ # React components
│       ├── lib/      # Utilities
│       └── hooks/    # Custom hooks
└── docs/             # Documentation
```

## 🔧 Administration

### Create Admin User (Manual)

```bash
docker-compose exec backend python -m app.scripts.create_admin
```

### Credit User Account

Via API:
```bash
curl -X POST https://yourdomain.com/api/v1/admin/users/{user_id}/credit \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.00, "reason": "Initial credit"}'
```

Or via Admin UI: Admin Panel → Users → Select User → Add Credit

### Add Proxmox Server

Admin Panel → Servers → Add Server:
- Name: Proxmox-01
- API URL: https://proxmox-server:8006
- API Token: PVEAPIToken=user@pam!tokenid=secret
- Test connection before saving

### Ban User

Admin Panel → Users → Select User → Ban:
- **Temporary**: Set end date, user auto-unbanned after
- **Permanent**: No end date, manual unban required
- Reason is logged and visible to admins

### View Audit Logs

Admin Panel → Logs (all actions are immutably logged)

## 🔐 Security Checklist

- [ ] Change all default passwords in `.env`
- [ ] Generate unique `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Enable HTTPS (automatic with Caddy if domain configured)
- [ ] Configure firewall (only ports 80, 443 exposed)
- [ ] Backup database regularly
- [ ] Review and adjust rate limits
- [ ] Enable 2FA for admin accounts (future feature)
- [ ] Monitor audit logs regularly
- [ ] Keep Docker images updated

## 🧪 Testing

### Backend Tests

```bash
docker-compose exec backend pytest
```

### Frontend Tests

```bash
docker-compose exec frontend npm test
```

### API Manual Testing

Access Swagger UI: https://yourdomain.com/api/docs

## 📊 Monitoring

- **Real-time**: Dashboard shows live VM status, node health
- **Metrics**: CPU, RAM, disk, network per node
- **Billing**: Transaction history, credit consumption graphs

## 🔄 Backup & Restore

### Database Backup

```bash
docker-compose exec postgres pg_dump -U unimanager unimanager > backup.sql
```

### Database Restore

```bash
cat backup.sql | docker-compose exec -T postgres psql -U unimanager unimanager
```

## 🚨 Troubleshooting

### Backend won't start
- Check database connection: `docker-compose logs postgres`
- Verify environment variables in `.env`

### Can't connect to Proxmox
- Verify API token has correct permissions
- Check network connectivity from backend container
- Test: `docker-compose exec backend curl -k https://proxmox-server:8006/api2/json/version`

### Billing not working
- Check Celery worker: `docker-compose logs celery-worker`
- Verify `ENABLE_AUTO_BILLING=true` in `.env`

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Admin Guide](docs/ADMIN_GUIDE.md)
- [Security Guide](docs/SECURITY.md)

## 🛣️ Roadmap

- [ ] Two-factor authentication (2FA)
- [ ] Email notifications for low balance, VM events
- [ ] Custom VM networks (VLANs, VPNs)
- [ ] Terraform/Ansible integration
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard

## 📄 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## 📞 Support

- Documentation: `/docs`
- Issues: GitHub Issues
- Email: support@yourdomain.com

---

**Uni-Manager** - Professional VM Management Made Simple
