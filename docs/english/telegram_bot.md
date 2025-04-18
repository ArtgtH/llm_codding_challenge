# Telegram Bot Component

The Telegram Bot component is responsible for capturing messages from agricultural chats, storing them in the database, and forwarding them to the worker service for processing.

## Architecture

The bot is built using the `aiogram` framework and follows a middleware-based architecture. It consists of the following key components:

- **Main Bot Application**: Initializes and runs the Telegram bot
- **RabbitMQ Service**: Handles message publishing to the RabbitMQ queue
- **Database Repository**: Manages message storage in the PostgreSQL database
- **Chat Timers**: Tracks chat inactivity and manages timer-based actions

## Key Files

- `main.py`: Entry point for the bot application
- `rabbit/service.py`: RabbitMQ integration service
- `db/repositories.py`: Database repository for message storage
- `middlewares.py`: Middleware components for bot message handling
- `timer.py`: Chat inactivity timer functionality
- `configs/config.py`: Configuration settings

## Configuration

The bot is configured through environment variables in the `.env` file:

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram Bot API token |
| `DB_HOST` | PostgreSQL database host |
| `DB_PORT` | PostgreSQL database port |
| `DB_USER` | PostgreSQL database username |
| `DB_PASSWORD` | PostgreSQL database password |
| `DB_NAME` | PostgreSQL database name |
| `RABBITMQ_URL` | RabbitMQ connection URL |
| `RABBITMQ_MESSAGE_QUEUE` | RabbitMQ queue name |

## Workflow

1. The bot starts and connects to the Telegram API, PostgreSQL database, and RabbitMQ
2. When a message is received in a chat, the bot:
   - Logs the message and its metadata
   - Sends the message data to RabbitMQ using the `RabbitMQService`
   - Stores the message in the database using the `MessageRepository`
   - Resets the inactivity timer for the chat

## Inactivity Timer

The bot includes a timer system that tracks inactivity in each chat. This can be used to trigger actions after a period of inactivity, such as:

- Sending summary reports
- Reminding users to provide updates
- Generating analytics for the quiet period

The timer is reset each time a new message is received in the chat.

## Adding the Bot to a New Chat

To add the bot to a new agricultural chat:
1. Invite the bot user to the Telegram group
2. Grant the bot permission to read messages
3. The bot will automatically start processing messages 