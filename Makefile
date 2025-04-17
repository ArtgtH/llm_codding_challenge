up:
	docker compose up --build

up-app:
	docker compose up --build tg_bot worker

up-infra:
	docker compose up --build postgres rabbitmq