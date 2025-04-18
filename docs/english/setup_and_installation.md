# Setup and Installation

This guide will walk you through setting up and running the application.

## Prerequisites

- Docker and Docker Compose
- Telegram Bot Token (from [BotFather](https://t.me/botfather))
- Mistral AI API Key (from [Mistral AI Platform](https://console.mistral.ai/))
- Google Drive API credentials

## Environment Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create environment files:
   ```bash
   # For the Telegram bot
   cp tg_bot/.env.sample tg_bot/src/.env
   
   # For the worker service
   cp worker/.env.sample worker/src/.env
   ```

3. Edit the `.env` files:
   
   **tg_bot/src/.env**:
   ```
   BOT_TOKEN=your_telegram_bot_token
   ```
   
   **worker/src/.env**:
   ```
   MISTRAL_API_KEY=your_mistral_ai_api_key
   ```

4. Set up Google Drive API credentials:
   - Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
   - Enable the Google Drive API
   - Create OAuth 2.0 credentials (service account)
   - Download the JSON credentials file
   - Place the credentials file in `worker/src/google_drive/api_key/`
   - Update the file path in `worker/src/google_drive/google_drive_uploader.py` (line 21)

## Running the Application

Start all services using Docker Compose:

```bash
docker-compose up -d
```

This will start the following services:
- Telegram Bot
- Worker Service
- PostgreSQL Database
- RabbitMQ

## Monitoring

- Monitor the RabbitMQ management interface at http://localhost:15672 (username: guest, password: guest)
- Check application logs:
  ```bash
  docker-compose logs -f tg_bot
  docker-compose logs -f worker
  ```

## Troubleshooting

### Database Connection Issues
- Ensure PostgreSQL is up and running: `docker-compose ps postgres`
- Check the database connection parameters in the environment variables

### RabbitMQ Connection Issues
- Ensure RabbitMQ is up and running: `docker-compose ps rabbitmq`
- Check the RabbitMQ connection parameters in the environment variables

### Google Drive Upload Issues
- Verify the JSON credentials file is correctly placed and configured
- Check that the service account has appropriate permissions on the target folder 