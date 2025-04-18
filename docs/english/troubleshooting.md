# Troubleshooting Guide

This guide covers common issues you might encounter while running the system and provides solutions.

## Telegram Bot Issues

### Bot Not Responding to Messages

**Symptoms**:
- The bot is in the chat but doesn't respond to messages
- No messages appear in the worker service logs

**Possible Solutions**:
1. Check if the bot is running: `docker-compose ps tg_bot`
2. Verify the bot token is correct in `tg_bot/src/.env`
3. Check the bot logs: `docker-compose logs -f tg_bot`
4. Ensure the bot has permission to read messages in the chat

### Bot Not Starting

**Symptoms**:
- The bot service keeps restarting
- Error messages in the logs about connection failures

**Possible Solutions**:
1. Check if RabbitMQ is running: `docker-compose ps rabbitmq`
2. Verify the RabbitMQ connection URL in the environment variables
3. Ensure PostgreSQL is running: `docker-compose ps postgres`
4. Check the PostgreSQL connection parameters in the environment variables

## Worker Service Issues

### Worker Not Processing Messages

**Symptoms**:
- Messages are sent to the Telegram bot but not processed
- No Excel files are generated or uploaded to Google Drive

**Possible Solutions**:
1. Check if the worker service is running: `docker-compose ps worker`
2. Verify the RabbitMQ connection URL in the environment variables
3. Check the worker logs: `docker-compose logs -f worker`
4. Ensure the Mistral AI API key is correctly set

### Mistral AI Analysis Failing

**Symptoms**:
- Error messages about Mistral API in the worker logs
- Messages are received but no structured data is extracted

**Possible Solutions**:
1. Verify the Mistral AI API key in `worker/src/.env`
2. Check for rate limiting issues (too many API calls)
3. Inspect the worker logs for detailed error messages
4. Try processing messages with simpler text content for testing

## Google Drive Issues

### Files Not Being Uploaded

**Symptoms**:
- Messages are processed but no files appear in Google Drive
- Error messages about Google Drive in the worker logs

**Possible Solutions**:
1. Verify the Google Drive API credentials file exists in the correct location
2. Check that the service account has permission to access the target folders
3. Inspect the worker logs for detailed Google Drive error messages
4. Verify the file path in `worker/src/google_drive/google_drive_uploader.py`

### Incorrect File Organization

**Symptoms**:
- Files are uploaded but not in the expected folders
- Team-specific files are mixed together

**Possible Solutions**:
1. Check the folder URL configuration in the GoogleDriveUploader class
2. Verify the team name is being correctly extracted from messages
3. Inspect the folder creation logic in `google_drive_uploader.py`

## Database Issues

### Database Connection Failures

**Symptoms**:
- Error messages about database connections in the logs
- Bot or worker services restarting repeatedly

**Possible Solutions**:
1. Verify PostgreSQL is running: `docker-compose ps postgres`
2. Check the database connection parameters in the environment variables
3. Try connecting to the database manually to verify credentials
4. Inspect the database logs: `docker-compose logs -f postgres`

### Database Migration Issues

**Symptoms**:
- Error messages about missing tables or columns
- Services failing to start or process messages

**Possible Solutions**:
1. Check if the database schema is correctly initialized
2. Verify that the database models match the database schema
3. Run database migrations if applicable

## RabbitMQ Issues

### Queue Connectivity Problems

**Symptoms**:
- Services can't connect to RabbitMQ
- Error messages about AMQP connections

**Possible Solutions**:
1. Verify RabbitMQ is running: `docker-compose ps rabbitmq`
2. Check the RabbitMQ connection URL in the environment variables
3. Inspect the RabbitMQ logs: `docker-compose logs -f rabbitmq`
4. Try accessing the RabbitMQ management interface (http://localhost:15672)

### Messages Not Being Processed

**Symptoms**:
- Messages appear in the RabbitMQ queue but aren't consumed
- Queue size keeps growing

**Possible Solutions**:
1. Check if the worker service is running: `docker-compose ps worker`
2. Verify the queue name in the environment variables
3. Inspect the worker logs for consumer-related error messages
4. Check the RabbitMQ management interface for queue status 