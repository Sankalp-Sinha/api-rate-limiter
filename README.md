# RateGuard

RateGuard is a multi-tenant, hosted rate-limiting decision service for backend applications.

Developers create projects, generate integration keys, configure per-endpoint rate-limit policies, and call a centralized `/v1/check` API before executing protected operations.

The core rate-limiting path uses Redis and an atomic Lua token-bucket implementation, while PostgreSQL stores persistent configuration, project ownership, request logs, and analytics.

---

## Live Demo

### Frontend

`<YOUR_VERCEL_FRONTEND_URL>`

### Backend

`https://rateguard-backend-production.up.railway.app`

### Health

`https://rateguard-backend-production.up.railway.app/health/live`

> Replace the frontend placeholder with the actual deployed Vercel URL.

---

## What Problem Does RateGuard Solve?

Applications often need limits such as:

- 5 AI resume generations per minute
- 100 API calls per hour
- 10 OTP requests per minute
- 50 search requests per second

Implementing distributed rate limiting independently in every backend creates duplicated logic and inconsistent behavior.

RateGuard centralizes this decision.

A backend sends:

```http
POST /v1/check
Authorization: Bearer rg_project_...
Content-Type: application/json