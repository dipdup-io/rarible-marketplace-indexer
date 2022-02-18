.ONESHELL:
.DEFAULT_GOAL: all

source_dir := rarible_marketplace_indexer

install:
	poetry install `if [ "${DEV}" = "0" ]; then echo "--no-dev"; fi`

isort:
	poetry run isort $(source_dir)

black:
	poetry run black $(source_dir)

flake:
	poetry run flakeheaven lint $(source_dir)

mypy:
	poetry run mypy $(source_dir)

lint: isort black flake mypy

up:
	docker-compose up -d

down:
	docker-compose down -v
