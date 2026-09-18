# Simple Makefile for LexVision Legal Tech Platform
# Beginner-friendly developer tasks

.PHONY: help install run test migrate docker-up docker-down

help:
	@echo "LexVision - Developer Commands"
	@echo "  make install      Install Python dependencies"
	@echo "  make migrate      Run Django database migrations"
	@echo "  make run          Start local Django development server"
	@echo "  make test         Run automated unit tests"
	@echo "  make docker-up    Build and start Docker containerized application"
	@echo "  make docker-down  Stop running Docker containers"

install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm || true

migrate:
	python manage.py makemigrations
	python manage.py migrate

run:
	python manage.py runserver 0.0.0.0:8000

test:
	python manage.py test apps.analysis apps.documents apps.accounts

docker-up:
	docker compose up --build

docker-down:
	docker compose down
