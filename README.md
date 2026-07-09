# cloneX — Website Template Extractor

> **Authorized website cloning for redesign & development.**

cloneX is a production-ready SaaS application that crawls websites you own or have permission to clone, downloads their assets, removes proprietary branding, and generates clean, editable project templates.

![cloneX](frontend/public/logo.png)

---

## What cloneX Does

1. **Crawl** — Follows internal links, detects sitemaps, respects `robots.txt`
2. **Download** — Saves HTML, CSS, JS, images, fonts, icons, and media
3. **Rewrite** — Converts absolute URLs to local paths, repairs broken links
4. **Sanitize** — Removes analytics, tracking scripts, and proprietary branding
5. **Export** — Generates a ready-to-edit project with `README.md` and `package.json`

---

## Quick Start (Docker)

The fastest way to run cloneX is with Docker Compose.

### Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/)

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd cloneX
```

### 2. Add your branding images

Place these files in `frontend/public/`:

```text
frontend/public/logo.png   # your site logo
frontend/public/bg.jpg     # your dark background
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env` if needed. The defaults work for local development.

### 4. Start the stack

```bash
docker compose up --build -d
```

Wait ~60–90 seconds for the database, backend, worker, and frontend to start.

### 5. Open the app

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| API Docs | http://localhost:8000/api/docs |
| Health | http://localhost:8000/health |

### 6. Login

Default admin account (created automatically on every startup):

- **Email:** `admin@cloneforge.local`
- **Password:** `admin`

The password is reset to these values every time the backend container starts, so this login is guaranteed to work even if the database already exists.

> **Security tip:** Change `FIRST_SUPERUSER_EMAIL` and `FIRST_SUPERUSER_PASSWORD` in `.env` for production.

---

## Step-by-Step Usage Guide

### Create your first clone project

1. **Open the dashboard** at http://localhost:3000/dashboard
2. Click **Projects** in the sidebar
3. Click **New project**
4. Enter:
   - **Project name:** My Site Clone
   - **Website URL:** `https://example.com` (a site you own or authorize)
5. Click **Create & clone**

### Monitor the crawl

- The crawl starts automatically
- Watch the progress bar on the project detail page
- You can **pause**, **resume**, or **cancel** the job

### Preview the result

Once the crawl completes:

1. Open the project
2. Switch between:
   - **Original preview** — the live source site
   - **Generated preview** — your cloned template
   - **Split screen** — side-by-side comparison

### Download the template

Use the API to download the exported project:

```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@cloneforge.local&password=admin"

# Download as ZIP (replace PROJECT_ID)
curl "http://localhost:8000/api/v1/projects/PROJECT_ID/download?format=zip" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o project.zip
```

The ZIP contains:

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

### Customize placeholders

Open any exported HTML file and replace placeholders:

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
| `SECRET_KEY` | JWT signing key | change in production |
| `DATABASE_URL` | PostgreSQL connection | local Docker |
| `REDIS_URL` | Redis connection | local Docker |
| `STORAGE_TYPE` | `local` or `s3` | `local` |
| `MAX_CRAWL_DEPTH` | Max crawl depth | `5` |
| `ALLOW_PRIVATE_NETWORKS` | Allow local/private targets | `false` |
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

### Backend

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

### Worker

```bash
cd backend
source .venv/bin/activate
celery -A app.workers.celery_app worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## API Documentation

Interactive API docs are available at:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

---

## Security & Authorization

cloneX is designed for legitimate, authorized use only:

- Only `http://` and `https://` URLs are accepted
- Private networks and localhost are blocked by default
- `robots.txt` is respected by default
- Analytics, tracking, and authentication tokens are removed from exports
- Credentials are never included in exported projects

**You must only clone websites you own or have explicit written permission to clone.**

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS, Framer Motion |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL 15 |
| Queue | Redis, Celery |
| Crawler | Playwright, BeautifulSoup, requests |
| DevOps | Docker, Docker Compose, GitHub Actions |

---

## Troubleshooting

### Database is unhealthy

```bash
docker compose down -v
docker compose up --build -d
```

### Port 5432 already in use

```bash
netstat -ano | findstr :5432
```

Stop the conflicting service or change the port in `.env` and `docker-compose.yml`.

### Crawl gets stuck

Check worker logs:

```bash
docker compose logs worker -f
```

Reduce `max_depth` and `max_pages` for faster results.

### Frontend shows broken logo/background

Make sure `logo.png` and `bg.jpg` exist in `frontend/public/`, then rebuild:

```bash
docker compose down
docker compose up --build -d
```

---

## Deploy to Production

1. Change `SECRET_KEY` to a secure random string
2. Use managed PostgreSQL and Redis
3. Configure S3-compatible storage
4. Run migrations with Alembic
5. Use a reverse proxy (nginx/traefik) with TLS
6. Set `NODE_ENV=production` and `DEBUG=false`

---

## License & Disclaimer

cloneX is provided for legitimate website redesign and template extraction on sites you own or are authorized to clone. Users are responsible for complying with applicable laws, terms of service, and `robots.txt` directives.

---

## Support

For issues or feature requests, open a GitHub issue.
