# APIs and Endpoints

This document describes the APIs and endpoints used in the application.

## RabbitMQ Message Queue

RabbitMQ is used as the message broker between the Telegram bot and the worker service.

### Queue Configuration

| Parameter | Value |
|-----------|-------|
| Queue Name | Configured via `RABBITMQ_MESSAGE_QUEUE` environment variable |
| Durability | `durable=True` |
| Auto-delete | `False` |
| Exclusive | `False` |

### Message Format

Messages are sent as JSON objects with the following structure:

```json
{
  "chat_id": "123456789",
  "chat_title": "Agricultural Reports Group",
  "user": "John Doe",
  "message_text": "The actual message content...",
  "time": "15/04/2023, 14:30:45"
}
```

### Producer (Telegram Bot)

The Telegram bot publishes messages to the queue in the following cases:
- When a new message is received in a chat
- The message is published using the `RabbitMQService.send_message()` method

### Consumer (Worker Service)

The worker service consumes messages from the queue:
- It uses a blocking connection with channel-based consumption
- Messages are acknowledged after successful processing
- The consumer uses the standard `pika` library for RabbitMQ interaction

## Mistral AI API

The worker service uses the Mistral AI API for text analysis.

### API Configuration

| Parameter | Value |
|-----------|-------|
| API Key | Configured via `MISTRAL_API_KEY` environment variable |
| Model | "mistral-medium" |
| Temperature | 0.3 |
| Max Tokens | 2048 |

### Request Format

Requests to the Mistral AI API include:
- A carefully constructed prompt with instructions and examples
- The message text to be analyzed
- Model parameters (temperature, max tokens, etc.)

### Response Format

Responses from the Mistral AI API contain:
- A structured JSON list of agricultural operations
- Each operation is mapped to an `AgriculturalOperation` object

## PostgreSQL Database

The application uses PostgreSQL for data storage.

### Connection Configuration

| Parameter | Value |
|-----------|-------|
| Host | Configured via `DB_HOST` environment variable |
| Port | Configured via `DB_PORT` environment variable |
| Username | Configured via `DB_USER` environment variable |
| Password | Configured via `DB_PASSWORD` environment variable |
| Database Name | Configured via `DB_NAME` environment variable |

### Tables

The database has the following tables:

1. `messages`: Stores all messages received by the Telegram bot
2. `daily_reports`: Stores the Excel reports generated by the worker service 