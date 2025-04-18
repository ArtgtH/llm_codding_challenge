# Project Overview

This project is an automated system for processing agricultural reports via Telegram messages. It extracts structured data from free-text agricultural reports, analyzes them using AI, and stores the results in Excel spreadsheets which are then uploaded to Google Drive.

## Architecture

The system consists of two main components:

1. **Telegram Bot (`tg_bot`)**: Receives messages from users in agricultural chat groups
2. **Worker Service (`worker`)**: Processes messages using AI, extracts structured data, and uploads files to Google Drive

These components communicate via RabbitMQ, and use PostgreSQL for data storage.

## Workflow

1. A user sends a message to a Telegram chat where the bot is present
2. The bot captures the message and:
   - Sends it to the RabbitMQ queue
   - Stores it in the PostgreSQL database
   - Resets an inactivity timer for the chat
3. The worker service:
   - Retrieves messages from the RabbitMQ queue
   - Processes the message text using Mistral AI to extract agricultural operations data
   - Saves the original message as a Word document in Google Drive
   - Updates an Excel spreadsheet with the extracted data
   - Uploads the Excel spreadsheet to Google Drive
   - Stores the Excel report in PostgreSQL

## Features

- **Message Processing**: Extracts structured agricultural data from informal text messages
- **Automated Document Generation**: Creates Word documents and Excel spreadsheets from message content
- **Google Drive Integration**: Automatically uploads and organizes documents in team folders
- **Inactivity Detection**: Monitors chat activity and can take actions after periods of inactivity
- **Database Storage**: Maintains records of messages and generated reports
- **Scalable Architecture**: Microservices design with containerized components 