# Prompt-to-Comic App

.PHONY: help run run-docker test clean

help:
	@echo "🎨 Prompt-to-Comic Commands:"
	@echo "  make run        - Run locally (backend + frontend)"
	@echo "  make run-docker - Run with docker-compose"
	@echo "  make test       - Run backend tests"
	@echo "  make clean      - Clean generated files"

run:
	@echo "🚀 Starting app locally..."
	@python run_app.py

run-docker:
	@echo "🐳 Starting app with docker..."
	docker-compose up -d 

test:
	@echo "🧪 Running tests..."
	cd backend && uv run pytest tests/ -v

clean:
	@echo "🧹 Cleaning up..."
	rm -rf backend/output/debug_*
	rm -rf backend/output/comics/*
	@echo "✅ Cleaned!" \

build:
	@echo "🔄 Building without cache..."
	docker-compose build --no-cache