up:
	docker compose up --build

up-bot:
	docker compose up --build tg_bot worker

up-worker:
	docke compose down worker
	docker compose up --build worker

up-infra:
	docker compose up --build postgres rabbitmq