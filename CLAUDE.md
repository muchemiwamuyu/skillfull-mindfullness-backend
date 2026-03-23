# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django 6.0 REST API backend for Urbantrends — a service ordering, project management, and blogging platform. Uses Django REST Framework 3.16 with JWT authentication (Simple JWT).

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run dev server
python manage.py runserver

# Run with Docker (PostgreSQL 16 on port 5433)
docker-compose up

# Run migrations
python manage.py migrate

# Run tests
python manage.py test

# Run tests for a specific app
python manage.py test urbantrends_orders

# Collect static files
python manage.py collectstatic
```

## Architecture

### Django Apps

- **urbantrends_authentication** — User registration, JWT login, Google OAuth, password reset
- **urbantrends_services** — Service catalog: Categories → ServiceItems → ServiceTiers (with pricing)
- **urbantrends_orders** — Order creation with OrderItems referencing ServiceItem + ServiceTier
- **urbantrends_projects** — Developer portfolio projects
- **urbantrends_blogs** — Blog posts (slug-based URLs), comments, likes (toggle)
- **urbantrends_brands** — Brand foundation with M2M Module associations
- **client_projects** — Client project submissions with approval workflow (pending/approved/rejected)
- **dashboard_services** — User dashboard for projects and team management

### Settings & Config

Single `urbantrends_backend/settings.py`. Environment variables loaded via `python-dotenv`. Database configured through `dj_database_url`.

Required env vars: `SECRET_KEY`, `DATABASE_URL`, `GOOGLE_CLIENT_ID`, `SENDGRID_API_KEY`, `PRIVATE_EMAIL_PASSWORD`.

### URL Routing

Root URLs in `urbantrends_backend/urls.py`:
- `/auth/` → authentication
- `/services/` → service catalog
- `/orders/` → orders
- `/dev_projects/` → developer projects
- `/blogs/` → blog posts
- `/brands/` → brands
- `/clients/` → client projects
- `/dash/projects/` → dashboard

### Authentication

JWT tokens via Simple JWT. Access token: 60 min, Refresh token: 1 day. Auth header: `Bearer <token>`. Google OAuth via custom `verify_google_token()` utility.

### API Patterns

- ViewSets with DRF routers for standard CRUD
- Public read-only endpoints for services, blogs, and project browsing
- Authenticated endpoints for user-owned resources
- Staff-only endpoints for admin operations
- Custom actions via `@action` decorator (e.g., `like`, `comment` on blog posts)
- `IsOwnerOrReadOnly` custom permission for blog posts
- Rate throttling: 5/min login, 10/min anonymous, 100/min authenticated

### Deployment

Docker with Gunicorn (gthread workers, 3 workers × 3 threads). PostgreSQL 16 in Docker Compose. CORS configured for `urbantrends.dev` and `localhost:5173`.

### Media Handling

File uploads use Django's `ImageField` with upload paths like `blog_images/`, `brand_images/`, `project_images/`. Served at `/media/`.
