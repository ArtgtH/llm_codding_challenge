# Установка и настройка

Это руководство проведет вас через процесс установки и запуска приложения.

## Предварительные требования

- Docker и Docker Compose
- Токен Telegram-бота (от [BotFather](https://t.me/botfather))
- API-ключ Mistral AI (с [платформы Mistral AI](https://console.mistral.ai/))
- Учетные данные Google Drive API

## Настройка окружения

1. Клонируйте репозиторий:
   ```bash
   git clone <url-репозитория>
   cd <директория-репозитория>
   ```

2. Создайте файлы окружения:
   ```bash
   # Для Telegram-бота
   cp tg_bot/.env.sample tg_bot/src/.env
   
   # Для сервиса-обработчика
   cp worker/.env.sample worker/src/.env
   ```

3. Отредактируйте файлы `.env`:
   
   **tg_bot/src/.env**:
   ```
   BOT_TOKEN=ваш_токен_telegram_бота
   ```
   
   **worker/src/.env**:
   ```
   MISTRAL_API_KEY=ваш_ключ_api_mistral_ai
   ```

4. Настройте учетные данные Google Drive API:
   - Создайте проект в [консоли Google Cloud](https://console.cloud.google.com/)
   - Включите Google Drive API
   - Создайте учетные данные OAuth 2.0 (сервисный аккаунт)
   - Загрузите файл учетных данных JSON
   - Поместите файл учетных данных в `worker/src/google_drive/api_key/`
   - Обновите путь к файлу в `worker/src/google_drive/google_drive_uploader.py` (строка 21)

## Запуск приложения

Запустите все службы с помощью Docker Compose:

```bash
docker-compose up -d
```

Это запустит следующие службы:
- Telegram-бот
- Сервис-обработчик
- База данных PostgreSQL
- RabbitMQ

## Мониторинг

- Следите за интерфейсом управления RabbitMQ по адресу http://localhost:15672 (имя пользователя: guest, пароль: guest)
- Проверяйте логи приложения:
  ```bash
  docker-compose logs -f tg_bot
  docker-compose logs -f worker
  ```

## Устранение неполадок

### Проблемы с подключением к базе данных
- Убедитесь, что PostgreSQL запущен и работает: `docker-compose ps postgres`
- Проверьте параметры подключения к базе данных в переменных окружения

### Проблемы с подключением к RabbitMQ
- Убедитесь, что RabbitMQ запущен и работает: `docker-compose ps rabbitmq`
- Проверьте параметры подключения к RabbitMQ в переменных окружения

### Проблемы с загрузкой в Google Drive
- Убедитесь, что JSON-файл учетных данных правильно размещен и настроен
- Проверьте, что сервисный аккаунт имеет необходимые разрешения для целевой папки 