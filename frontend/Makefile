# Makefile for Prompt-to-Comic Frontend

VENV_ACTIVATE = source .venv/bin/activate

install:
	uv sync

run:
	uv run streamlit run app.py

format:
	uv run black .

lint:
	uv run ruff .

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .streamlit

venv:
	uv venv

# Frontend Testing Targets
ui:
	curl "http://localhost:8501"

health:
	curl "http://localhost:8501/_stcore/health"

.PHONY: install run format lint clean venv ui health
