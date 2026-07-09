# cloneX Makefile
# Requires Docker + Docker Compose for full stack

.PHONY: up down build logs shell-backend shell-worker shell-frontend test-backend test-frontend lint clean

# Full stack
up:
	docker compose up -d

up-build:
	docker compose up --build -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

# Shell access
shell-backend:
	docker compose exec backend /bin/sh

shell-worker:
	docker compose exec worker /bin/sh

shell-frontend:
	docker compose exec frontend /bin/sh

# Database
migrate:
	docker compose exec backend alembic upgrade head

seed:
	docker compose exec backend python -m app.initial_data

# Testing
test-backend:
	cd backend && pytest

test-frontend:
	cd frontend && npm run lint && npm run build

lint:
	cd backend && ruff check . || true
	cd frontend && npm run lint || true

# Cleanup
clean:
	docker compose down -v
	docker system prune -f
