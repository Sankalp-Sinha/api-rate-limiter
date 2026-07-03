# Distributed API Rate Limiter & API Protection Gateway

A production-grade API rate limiter built using FastAPI, Redis, and the Token Bucket algorithm.

## Current Features

- FastAPI backend
- Redis-backed token bucket rate limiter
- Atomic Redis Lua script for race-condition-free token updates
- Rate limiting by client IP and route
- Proper HTTP 429 response
- Rate limit headers:
  - X-RateLimit-Limit
  - X-RateLimit-Remaining
  - X-RateLimit-Reset
  - Retry-After
- Redis health check endpoint
- Docker Compose setup for Redis

## Tech Stack

- Python
- FastAPI
- Redis
- Docker
- Lua scripting

## API Endpoints

```txt
GET /
GET /health/redis
GET /api/public
GET /api/protected