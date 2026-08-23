# IDLIE Backend

Backend service for the **IDLIE** food discovery platform built using Django, Django REST Framework, PostgreSQL/PostGIS, Redis, and Celery.

---

# Overview

IDLIE Backend powers the core APIs and services for the food discovery platform, including:

- User management
- Food spot management
- Feed generation
- Posts and media handling
- Background task processing
- Geospatial queries using PostGIS

---

# Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.12+ | Programming Language |
| Django | Web Framework |
| Django REST Framework | API Development |
| PostgreSQL | Primary Database |
| PostGIS | Geospatial Extensions |
| uv | Dependency Management |

---

# Project Structure

```text
idlie-backend/
├── config/                 # Django project configuration
├── core/                   # Shared utilities and base configurations
├── feed/                   # Feed module
├── foodspot/               # Food spot module
├── post/                   # Post module
├── user/                   # User module
├── manage.py
├── pyproject.toml
├── uv.lock
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# Prerequisites

Before starting, ensure the following are installed:

- Python 3.12+
- PostgreSQL
- PostGIS
- Redis
- Git
- uv

---

# Installation Guide

## 1. Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:

```bash
uv --version
```

---

## 2. Clone Repository

```bash
git clone <your-repository-url>
cd idlie-backend
```

---

## 3. Create Virtual Environment

```bash
uv venv
```

---

## 4. Activate Virtual Environment

### macOS/Linux

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

---

## 5. Install Dependencies

```bash
uv sync
```

---

# Environment Configuration

Copy the example file and fill it in — these are the exact keys `config/settings.py` reads via `os.getenv(...)`:

```bash
cp .env.example .env
```

```env
# Database (used directly by settings.py DATABASES config)
DB_NAME=idlie_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=your-secret-key   # also used as the JWT signing secret
DEBUG=True

# Media storage — only required if USE_S3=True
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=
AWS_QUERYSTRING_AUTH=
AWS_DEFAULT_ACL=
AWS_S3_SIGNATURE_VERSION=
```

> Leave `USE_S3=False` for local development unless you're testing avatar/media uploads — the AWS variables are only needed once it's `True`. Signup/login OTPs are stubbed in `authentication/services/otp_services.py` (always `221180`), so no SMS provider is needed locally.

---

# PostgreSQL + PostGIS Setup

You need a Postgres instance with the PostGIS extension available. Pick one:

## Option A — Docker (recommended, matches production)

```bash
docker compose up -d db
```

This starts the `postgis/postgis:16-3.4` image on `localhost:5433` using the same `.env` file, and creates the volume automatically. Point `DB_HOST` at your Docker host (`localhost`) and `DB_PORT` at `5433` if you use this option instead of a local Postgres install.

## Option B — Local Postgres install

Login to PostgreSQL:

```bash
psql postgres
```

Create database:

```sql
CREATE DATABASE idlie_db;
```

Connect to database:

```sql
\c idlie_db
```

Enable PostGIS extension:

```sql
CREATE EXTENSION postgis;
```

> The app also links against GDAL/GEOS at the Python level (`django.contrib.gis`, `djangorestframework-gis`) for the `Hotel.location` field. On Linux, install the native libraries first: `sudo apt-get install binutils libproj-dev gdal-bin libgdal-dev` (see `Dockerfile` for the full list). This step isn't needed with Option A, since the app container already has them.

---

# Run Database Migrations

```bash
python manage.py migrate
```

---

# Create Superuser

```bash
python manage.py createsuperuser
```

---

# Run Development Server

```bash
python manage.py runserver
```

Server will run at:

```text
http://127.0.0.1:8000/
```

## Optional: Celery / Redis

Background tasks (`celery`) are configured against `redis://localhost:6379/0` (see `config/settings.py`). You only need Redis and a worker running if you're exercising async task code:

```bash
redis-server
celery -A config worker -l info
```

For a plain API dev loop, `runserver` alone is enough — Celery isn't required to boot the app.


# Useful Commands

## Create New Django App

```bash
python manage.py startapp <app_name>
```

## Create Migrations

```bash
python manage.py makemigrations
```

## Apply Migrations

```bash
python manage.py migrate
```

## Collect Static Files

```bash
python manage.py collectstatic
```

## Run Tests

```bash
python manage.py test
```

---

# Development Workflow

```text
Feature Branch → Development → Testing → Production
```

Suggested branch naming:

```text
feature/<feature-name>
bugfix/<bug-name>
hotfix/<issue-name>
```

---

# Recommended .gitignore

```gitignore
# Virtual Environment
.venv/

# Environment Variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class

# Django
db.sqlite3
media/
staticfiles/

# IDE
.vscode/
.idea/

# OS Files
.DS_Store
Thumbs.db
```

---

# Future Improvements

- Docker support
- CI/CD pipeline
- API documentation with Swagger/OpenAPI
- JWT Authentication
- Kubernetes deployment
- Monitoring & Logging
- Rate limiting
- Automated testing pipeline

---

# License

This project is licensed under the MIT License.

---

# Contributors

- Devn