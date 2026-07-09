<div align="center">

<img src="frontend/public/logo.png" alt="cloneX logo" width="120" />

# cloneX

**Authorized website cloning for redesign & development.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license--disclaimer)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED?logo=docker&logoColor=white)](#quick-start-docker)
[![Next.js](https://img.shields.io/badge/frontend-Next.js%2014-000000?logo=next.js&logoColor=white)](#tech-stack)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi&logoColor=white)](#tech-stack)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL%2015-4169E1?logo=postgresql&logoColor=white)](#tech-stack)

cloneX crawls websites you own or have permission to clone, downloads their assets, strips proprietary branding, and hands you back a clean, editable project template — ready for your own redesign.

</div>

---

## Table of Contents

- [What cloneX Does](#what-clonex-does)
- [Quick Start (Docker)](#quick-start-docker)
- [Step-by-Step Usage Guide](#step-by-step-usage-guide)
- [Configuration](#configuration)
- [Local Development](#local-development)
- [API Documentation](#api-documentation)
- [Security & Authorization](#security--authorization)
- [Tech Stack](#tech-stack)
- [Troubleshooting](#troubleshooting)
- [Deploy to Production](#deploy-to-production)
- [License & Disclaimer](#license--disclaimer)
- [Support](#support)

---

## What cloneX Does

cloneX turns any authorized website into a ready-to-edit local project in five steps:

| Step | Description |
|:----:|-------------|
| 🕷️ **Crawl** | Follows internal links, detects sitemaps, respects `robots.txt` |
| 📥 **Download** | Saves HTML, CSS, JS, images, fonts, icons, and media |
| 🔗 **Rewrite** | Converts absolute URLs to local paths and repairs broken links |
| 🧹 **Sanitize** | Strips analytics, tracking scripts, and proprietary branding |
| 📦 **Export** | Generates a ready-to-edit project with `README.md` and `package.json` |

---

## Quick Start (Docker)

The fastest way to run cloneX is with Docker Compose.

### Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

### 1. Clone the repository

```bash
git clone https://github.com/hakkachhamza/cloneX.git
cd cloneX
```

### 2. Configure environment

```bash
cp .env.example .env
```

The defaults work for local development — edit `.env` only if you need to customize something.

### 3. Start the stack

```bash
docker compose up --build -d
```

Give it **~60–90 seconds** for the database, backend, worker, and frontend to spin up.

### 4. Open the app

| Service | URL |
|---------|-----|
| 🖥️ Frontend | http://localhost:3000 |
| 📚 API Docs | http://localhost:8000/api/docs |
| ❤️ Health | http://localhost:8000/health |

### 5. Log in

A default admin account is created automatically on every startup:

| Field | Value |
|-------|-------|
| Email | `admin@cloneforge.local` |
| Password | `admin` |

> ⚠️ **Note:** This password is reset on every backend restart, so the login always works — even against an existing database. **Change it immediately in any shared or production environment.**

---

## Step-by-Step Usage Guide

### 1. Create your first clone project

1. Open the dashboard at **http://localhost:3000/dashboard**
2. Click **Projects** in the sidebar
3. Click **New project**
4. Enter:
   - **Project name:** `My Site Clone`
   - **Website URL:** `https://example.com` *(a site you own or are authorized to clone)*
5. Click **Create & clone**

### 2. Monitor the crawl

- The crawl starts automatically
- Track progress on the project detail page
- **Pause**, **resume**, or **cancel** the job at any time

### 3. Preview the result

Once the crawl completes, open the project and switch between:

- **Original preview** — the live source site
- **Generated preview** — your cloned template
- **Split screen** — side-by-side comparison

### 4. Download the template

```bash
# Log in and get a token
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@cloneforge.local&password=admin"

# Download the project as a ZIP (replace PROJECT_ID)
curl "http://localhost:8000/api/v1/projects/PROJECT_ID/download?format=zip" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o project.zip
```

The exported ZIP is structured as:

```text
project/
├── pages/          # Crawled HTML pages
├── assets/
│   ├── css/        # Stylesheets
│   ├── js/         # JavaScript files
│   ├── images/     # Image assets
│   └── fonts/      # Font files
├── README.md
└── package.json
```

### 5. Customize placeholders

Open any exported HTML file and replace the placeholders with your own content:

- `{{COMPANY_NAME}}`
- `{{EMAIL}}`
- `{{PHONE}}`
- `{{ADDRESS}}`
- `{{COPYRIGHT}}`

---

## Configuration

Key environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key | *change in production* |
| `DATABASE_URL` | PostgreSQL connection string | local Docker |
| `REDIS_URL` | Redis connection string | local Docker |
| `STORAGE_TYPE` | `local` or `s3` | `local` |
| `MAX_CRAWL_DEPTH` | Maximum crawl depth | `5` |
| `ALLOW_PRIVATE_NETWORKS` | Allow local/private crawl targets | `false` |
| `FIRST_SUPERUSER_EMAIL` | Seed admin email | `admin@cloneforge.local` |
| `FIRST_SUPERUSER_PASSWORD` | Seed admin password | `admin` |

For S3-compatible storage, also set:

```env
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=...
S3_BUCKET_NAME=...
S3_ENDPOINT_URL=...
```

---

## Local Development

<details>
<summary><strong>Backend</strong></summary>

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
alembic upgrade head
python -m app.initial_data
uvicorn app.main:app --reload --port 8000
```

</details>

<details>
<summary><strong>Worker</strong></summary>

```bash
cd backend
source .venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info
```

</details>

<details>
<summary><strong>Frontend</strong></summary>

```bash
cd frontend
npm install
npm run dev
```

</details>

---

## API Documentation

Interactive API docs are available once the backend is running:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

---

## Security & Authorization

cloneX is designed for legitimate, authorized use only:

- ✅ Only `http://` and `https://` URLs are accepted
- ✅ Private networks and localhost are blocked by default
- ✅ `robots.txt` is respected by default
- ✅ Analytics, tracking, and authentication tokens are stripped from exports
- ✅ Credentials are never included in exported projects

> **You must only clone websites you own or have explicit written permission to clone.**

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | Next.js 14 · React 18 · TypeScript · Tailwind CSS · Framer Motion |
| **Backend** | FastAPI · SQLAlchemy · Pydantic |
| **Database** | PostgreSQL 15 |
| **Queue** | Redis · Celery |
| **Crawler** | Playwright · BeautifulSoup · requests |
| **DevOps** | Docker · Docker Compose · GitHub Actions |

---

## Troubleshooting

<details>
<summary><strong>Database is unhealthy</strong></summary>

```bash
docker compose down -v
docker compose up --build -d
```

</details>

<details>
<summary><strong>Port 5432 already in use</strong></summary>

```bash
netstat -ano | findstr :5432
```

Stop the conflicting service, or change the port in `.env` and `docker-compose.yml`.

</details>

<details>
<summary><strong>Crawl gets stuck</strong></summary>

Check the worker logs:

```bash
docker compose logs worker -f
```

Then reduce `max_depth` and `max_pages` for faster results.

</details>

<details>
<summary><strong>Full reset</strong></summary>

```bash
docker compose down
docker compose up --build -d
```

</details>

---

## Deploy to Production

1. Change `SECRET_KEY` to a secure random string
2. Use managed PostgreSQL and Redis
3. Configure S3-compatible storage
4. Run migrations with Alembic
5. Put a reverse proxy (nginx/traefik) with TLS in front of the app
6. Set `NODE_ENV=production` and `DEBUG=false`

---

## License & Disclaimer

cloneX is provided for legitimate website redesign and template extraction on sites you own or are authorized to clone. Users are responsible for complying with applicable laws, terms of service, and `robots.txt` directives.

---

## Support

Found a bug or have a feature request? [Open a GitHub issue](https://github.com/hakkachhamza/cloneX/issues).

<div align="center">

Made with ⚙️ by [hakkachhamza](https://github.com/hakkachhamza)

</div>
