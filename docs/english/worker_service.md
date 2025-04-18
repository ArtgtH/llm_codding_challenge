# Worker Service Component

The Worker Service is responsible for processing agricultural messages, extracting structured data using AI, and saving the results to both Google Drive and PostgreSQL.

## Architecture

The worker consists of the following key components:

- **Message Consumer**: Receives messages from RabbitMQ
- **AI Agent**: Processes message text using Mistral AI to extract agricultural operations
- **Google Drive Uploader**: Saves documents to Google Drive
- **Database Repository**: Stores reports in PostgreSQL

## Key Files

- `main.py`: Entry point for the worker service
- `ai_agent/text_processing_pipeline.py`: Main text processing pipeline
- `ai_agent/analysis_pipeline.py`: AI-based text analysis using Mistral AI
- `ai_agent/mistral_client.py`: Client for the Mistral AI API
- `ai_agent/models/data_model.py`: Data models for agricultural operations
- `google_drive/google_drive_uploader.py`: Google Drive upload functionality
- `db/repositories.py`: Database repository for report storage

## Configuration

The worker is configured through environment variables in the `.env` file:

| Variable | Description |
|----------|-------------|
| `MISTRAL_API_KEY` | Mistral AI API key |
| `DB_HOST` | PostgreSQL database host |
| `DB_PORT` | PostgreSQL database port |
| `DB_USER` | PostgreSQL database username |
| `DB_PASSWORD` | PostgreSQL database password |
| `DB_NAME` | PostgreSQL database name |
| `RABBITMQ_URL` | RabbitMQ connection URL |
| `RABBITMQ_MESSAGE_QUEUE` | RabbitMQ queue name |

## Message Processing Workflow

1. The worker receives a message from the RabbitMQ queue
2. For each message:
   - The original text is saved as a Word document in Google Drive
   - The message is analyzed using the AI agent to extract agricultural operations
   - The extracted data is saved to an Excel spreadsheet
   - The Excel spreadsheet is uploaded to Google Drive
   - The Excel report is stored in the PostgreSQL database

## AI Agent

The AI agent uses the Mistral AI service to extract structured data from informal agricultural reports. The process involves:

1. Formatting a prompt with the message text and schema information
2. Sending the prompt to Mistral AI for analysis
3. Parsing and validating the returned JSON data
4. Converting the data into `AgriculturalOperation` objects

The AI agent can extract the following information:
- Date of operations
- Farm subdivision
- Agricultural operation type
- Crop type
- Daily area processed
- Total area processed
- Daily yield
- Total yield

## Google Drive Integration

The worker saves two types of documents to Google Drive:

1. **Word Documents**: The original message text
2. **Excel Spreadsheets**: The structured data extracted from messages

Documents are organized by team in folders and subfolders. 