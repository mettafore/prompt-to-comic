test:
	cd .. && uv run pytest backend/tests -v

run:
	uv run uvicorn app.main:app --reload

generate:
	curl -X POST "http://localhost:8000/generate" \
		-H "Content-Type: application/json" \
		-d '{"text": "Two kids in a spaceship arguing about pizza", "style": "Manga", "panels": 3}'

status:
	curl "http://localhost:8000/status/dummy123"

health:
	curl "http://localhost:8000/health"

docs:
	curl "http://localhost:8000/docs" 