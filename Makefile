install:
	uv sync

project:
	uv run project

run:
	uv run database

build:
	uv build

lint:
	uv run ruff check .
