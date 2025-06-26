test:
	cd .. && uv run pytest backend/tests -v

test-real-ai:
	@echo "Testing real AI pipeline (requires OPENAI_API_KEY)"
	uv run python test_real_ai.py

run:
	uv run uvicorn app.main:app --reload --port 8001

generate:
	curl -X POST "http://localhost:8001/generate" \
		-H "Content-Type: application/json" \
		-d '{"text": "Two kids in a spaceship arguing about pizza", "style": "Manga", "panels": 3}'

status:
	curl "http://localhost:8001/status/dummy123"

health:
	curl "http://localhost:8001/health"

docs:
	curl "http://localhost:8001/docs" 