.PHONY: install generate run test services down
install:
	python -m pip install -r requirements.txt
generate:
	python -m src.generate_data --date 2026-01-01
run:
	python -m src.pipeline --date 2026-01-01
test:
	pytest -q
services:
	docker compose up -d
down:
	docker compose down
