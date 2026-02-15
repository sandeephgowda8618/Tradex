.PHONY: help install install-dev format lint test test-cov run-api run-worker run-frontend docker-up docker-down

help:
	@echo "Targets:"
	@echo "  install       Install runtime dependencies"
	@echo "  install-dev   Install dev dependencies"
	@echo "  format        Format code (black)"
	@echo "  lint          Lint code (ruff)"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  run-api       Run FastAPI locally"
	@echo "  run-worker    Run Celery worker locally"
	@echo "  run-frontend  Run Vite frontend locally"
	@echo "  docker-up     Start docker-compose stack"
	@echo "  docker-down   Stop docker-compose stack"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

format:
	black app tests

lint:
	ruff check app tests

PYTHONPATH=.

test:
	PYTHONPATH=. pytest tests -v

test-cov:
	PYTHONPATH=. pytest --cov=app tests -v

run-api:
	uvicorn app.main:app --host 0.0.0.0 --port 8000

run-worker:
	celery -A app.celery_app.celery_app worker --loglevel=info

run-frontend:
	cd frontend && npm install && npm run dev

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
