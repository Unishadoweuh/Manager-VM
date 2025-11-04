# Uni-Manager API Documentation

## Table of Contents

1. [Authentication](#authentication)
2. [User Endpoints](#user-endpoints)
3. [VM Management](#vm-management)
4. [Templates](#templates)
5. [Payments](#payments)
6. [Administration](#administration)
7. [Monitoring](#monitoring)

## Base URL

```
Production: https://yourdomain.com/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### POST /auth/register

Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "company": "Acme Inc"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### POST /auth/login

Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### POST /auth/refresh

Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

## User Endpoints

### GET /user/me

Get current user information.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "role": "user",
  "balance": "50.00",
  "status": "active",
  "created_at": "2025-11-04T10:00:00Z"
}
```

### GET /user/credits

Get user credit balance.

**Response:**
```json
{
  "balance": "50.00",
  "currency": "USD"
}
```

### GET /user/transactions

Get user transaction history.

**Query Parameters:**
- `limit` (optional): Maximum number of transactions (default: 50)
- `offset` (optional): Offset for pagination (default: 0)

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "amount": "10.00",
    "type": "credit",
    "description": "Initial credit",
    "balance_after": "50.00",
    "created_at": "2025-11-04T10:00:00Z"
  }
]
```

## VM Management

### GET /vms

List all VMs for the current user.

**Response:**
```json
{
  "vms": [
    {
      "id": 1,
      "name": "web-server-01",
      "state": "running",
      "cpu_cores": 2,
      "ram_mb": 2048,
      "disk_gb": 20,
      "ip_address": "10.0.0.10",
      "created_at": "2025-11-04T10:00:00Z"
    }
  ],
  "total": 1
}
```

### POST /vms

Create a new VM from template.

**Request Body:**
```json
{
  "template_id": 1,
  "name": "my-server",
  "hostname": "myserver.local",
  "cpu_cores": 2,
  "ram_mb": 2048,
  "disk_gb": 20,
  "notes": "Production web server"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "my-server",
  "state": "creating",
  "template_id": 1,
  "created_at": "2025-11-04T10:00:00Z"
}
```

### GET /vms/{vm_id}

Get VM details.

**Response:**
```json
{
  "id": 1,
  "name": "my-server",
  "state": "running",
  "cpu_cores": 2,
  "ram_mb": 2048,
  "disk_gb": 20,
  "ip_address": "10.0.0.10",
  "total_cost": 150,
  "created_at": "2025-11-04T10:00:00Z"
}
```

### POST /vms/{vm_id}/action

Perform action on VM.

**Request Body:**
```json
{
  "action": "start"  // start, stop, reboot, suspend, resume
}
```

**Response:**
```json
{
  "message": "VM start action initiated",
  "vm_id": 1
}
```

### DELETE /vms/{vm_id}

Delete a VM.

**Response:** 204 No Content

## Templates

### GET /templates

List all available VM templates.

**Query Parameters:**
- `is_public` (optional): Filter public templates (default: true)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Ubuntu 22.04 - Small",
    "description": "Ubuntu 22.04 LTS with 2 CPU cores and 2GB RAM",
    "cpu_cores": 2,
    "ram_mb": 2048,
    "disk_gb": 20,
    "os_type": "linux",
    "os_name": "Ubuntu 22.04 LTS",
    "cost_per_hour": "0.0500",
    "cost_per_day": 1.20,
    "cost_per_month": 36.00,
    "is_active": true
  }
]
```

### GET /templates/{template_id}

Get template details.

## Administration (Admin Only)

### GET /admin/users

List all users.

**Query Parameters:**
- `limit` (optional): Maximum users (default: 100)
- `offset` (optional): Pagination offset (default: 0)

### POST /admin/users/{user_id}/credit

Add credits to user account.

**Request Body:**
```json
{
  "amount": 100.00,
  "reason": "Promotional credit"
}
```

**Response:**
```json
{
  "message": "Credits added successfully",
  "user_id": 5,
  "new_balance": "150.00"
}
```

### POST /admin/users/{user_id}/ban

Ban a user.

**Request Body:**
```json
{
  "reason": "Terms of service violation",
  "ban_until": "2025-12-31T23:59:59Z"  // null for permanent ban
}
```

**Response:**
```json
{
  "message": "User banned (temporary)",
  "user_id": 5,
  "ban_until": "2025-12-31T23:59:59Z"
}
```

### POST /admin/users/{user_id}/unban

Unban a user.

**Request Body:**
```json
{
  "reason": "Appeal approved"
}
```

### GET /admin/servers

List all Proxmox servers.

### POST /admin/servers

Add a new Proxmox server.

**Request Body:**
```json
{
  "name": "Proxmox-01",
  "description": "Primary datacenter server",
  "api_url": "https://proxmox.example.com:8006",
  "port": 8006,
  "api_token": "PVEAPIToken=user@pam!token=secret",
  "verify_ssl": true
}
```

### POST /admin/servers/test-connection

Test Proxmox server connection.

**Request Body:**
```json
{
  "api_url": "https://proxmox.example.com:8006",
  "api_token": "PVEAPIToken=user@pam!token=secret",
  "verify_ssl": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Connection successful",
  "version": "7.4-1"
}
```

### POST /admin/templates

Create a new VM template.

**Request Body:**
```json
{
  "name": "Custom Template",
  "description": "Custom configuration",
  "cpu_cores": 4,
  "ram_mb": 4096,
  "disk_gb": 40,
  "os_type": "linux",
  "os_name": "Ubuntu 22.04 LTS",
  "cost_per_hour": 0.10,
  "is_public": true
}
```

### GET /admin/logs

Get audit logs.

**Query Parameters:**
- `limit` (optional): Maximum logs (default: 100)
- `offset` (optional): Pagination offset (default: 0)

## Monitoring

### GET /monitoring/nodes

Get status of all Proxmox nodes.

### GET /monitoring/node/{node_id}/metrics

Get metrics for a specific node.

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 429 Too Many Requests
```json
{
  "detail": "Too many login attempts. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- Login attempts: 5 per 5 minutes per email address
- Other endpoints: No rate limiting by default (can be configured)

## Webhooks

### POST /payments/webhook

Stripe/PayPal webhook endpoint for payment processing.

**Note:** This endpoint is disabled when `ENABLE_PAYMENTS=false`
