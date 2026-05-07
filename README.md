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

Create a `.env` file in the root directory.

Example:

```env
DEBUG=True

SECRET_KEY=your-secret-key

DATABASE_NAME=idlie_db
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432

```

---

# PostgreSQL + PostGIS Setup

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