.ONESHELL:
.DEFAULT_GOAL: all

source_dir := rarible_marketplace_indexer
unit_tests_dir := tests

install:
	poetry install `if [ "${DEV}" = "0" ]; then echo "--no-dev"; fi`

isort:
	poetry run isort $(source_dir) $(unit_tests_dir)

ssort:
	poetry run ssort $(source_dir) $(unit_tests_dir)

black:
	poetry run black $(source_dir) $(unit_tests_dir)

flake:
	poetry run flakeheaven lint $(source_dir) $(unit_tests_dir)

mypy:
	poetry run mypy $(source_dir) $(unit_tests_dir)

lint: isort ssort black flake

prepare_services:
	docker-compose up -d --remove-orphans db hasura kafdrop kafka0 zookeeper0

up: prepare_services
	docker-compose up --build --remove-orphans --force-recreate --no-deps --abort-on-container-exit indexer

down:
	docker-compose down --volumes
