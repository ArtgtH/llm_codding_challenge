# Development Guide

This guide provides information for developers who want to extend, modify, or contribute to the project.

## Project Structure

```
├── tg_bot/                    # Telegram bot component
│   ├── src/                   # Source code
│   │   ├── configs/           # Configuration settings
│   │   ├── db/                # Database models and repositories
│   │   ├── rabbit/            # RabbitMQ service
│   │   ├── main.py            # Entry point
│   │   ├── middlewares.py     # Middleware components
│   │   └── timer.py           # Chat timer functionality
│   ├── .env.sample            # Environment variables template
│   ├── Dockerfile             # Docker configuration
│   └── requirements.txt       # Python dependencies
│
├── worker/                    # Worker service component
│   ├── src/                   # Source code
│   │   ├── ai_agent/          # AI processing functionality
│   │   │   ├── models/        # Data models
│   │   │   ├── utils/         # Utility functions
│   │   │   ├── extra_data/    # Reference data for AI
│   │   │   ├── mistral_client.py  # Mistral AI client
│   │   │   ├── analysis_pipeline.py  # Analysis pipeline
│   │   │   └── text_processing_pipeline.py  # Text processing pipeline
│   │   ├── configs/           # Configuration settings
│   │   ├── db/                # Database models and repositories
│   │   ├── google_drive/      # Google Drive integration
│   │   │   ├── api_key/       # Google API credentials
│   │   │   ├── google_drive_uploader.py  # Drive upload functionality
│   │   │   └── utils.py       # Drive utility functions
│   │   └── main.py            # Entry point
│   ├── .env.sample            # Environment variables template
│   ├── Dockerfile             # Docker configuration
│   └── requirements.txt       # Python dependencies
│
├── docker-compose.yaml        # Docker Compose configuration
├── Makefile                   # Make commands
└── README.md                  # Project overview
```

## Development Environment Setup

### Local Development

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Set up virtual environments:
   ```bash
   # For the Telegram bot
   cd tg_bot
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # For the worker service
   cd ../worker
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   # For the Telegram bot
   cp tg_bot/.env.sample tg_bot/src/.env
   # Edit tg_bot/src/.env with your Telegram bot token
   
   # For the worker service
   cp worker/.env.sample worker/src/.env
   # Edit worker/src/.env with your Mistral AI API key
   ```

4. Set up local RabbitMQ and PostgreSQL:
   ```bash
   # Start services with Docker Compose
   docker-compose up -d rabbitmq postgres
   ```

### Running in Development Mode

To run the components in development mode:

**Telegram Bot**:
```bash
cd tg_bot
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd src
python main.py
```

**Worker Service**:
```bash
cd worker
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd src
python main.py
```

## Common Development Tasks

### Adding a New Bot Command

1. Open `tg_bot/src/main.py`
2. Add a new handler function with the `@dp.message()` decorator
3. Implement the command logic
4. Register the handler with the dispatcher

Example:
```python
@dp.message(Command("status"))
async def handle_status(message: types.Message, db: AsyncSession) -> None:
    # Implement status command logic
    await message.reply("Bot is operational!")
```

### Extending the AI Analysis

1. Open `worker/src/ai_agent/analysis_pipeline.py`
2. Modify the `construct_prompt` function to add new extraction rules
3. Update the `AgriculturalOperation` model in `worker/src/ai_agent/models/data_model.py` if needed
4. Add new example cases to the prompt to guide the model

### Adding a New Database Model

1. Create or update the model definition in `db/models.py`
2. Create or update the repository methods in `db/repositories.py`
3. Update the database schema if needed

Example:
```python
# In models.py
class NewEntity(Base):
    __tablename__ = "new_entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    value: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

# In repositories.py
class NewEntityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_entity(self, name: str, value: float) -> NewEntity:
        entity = NewEntity(name=name, value=value)
        self.session.add(entity)
        await self.session.commit()
        return entity
```

## Testing

### Unit Tests

Add unit tests for new functionality in a `tests` directory:

```python
# tests/test_analysis_pipeline.py
import pytest
from ai_agent.analysis_pipeline import AnalysisPipeline

def test_analyze_text():
    pipeline = AnalysisPipeline()
    result = pipeline.analyze_text("Test message", message_date=date(2023, 4, 15))
    assert len(result) == 0  # No operations in a test message
```

### Manual Testing

Test the complete flow:
1. Send a message to the bot in a Telegram chat
2. Check that the message appears in the RabbitMQ queue
3. Verify that the worker processes the message
4. Check that the Word document and Excel spreadsheet are uploaded to Google Drive
5. Verify that the report is stored in the database

## Deployment

### Updating in Production

1. Pull the latest changes:
   ```bash
   git pull origin main
   ```

2. Rebuild and restart the services:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

### Adding New Environment Variables

1. Update the `.env.sample` files with the new variables
2. Add the variables to the Docker Compose file if needed
3. Update the documentation to reflect the new variables

## Code Style and Standards

- Follow PEP 8 guidelines for Python code
- Use type hints for function parameters and return values
- Add docstrings to classes and functions
- Keep functions small and focused on a single responsibility
- Use descriptive variable and function names

## Contributing

1. Create a new branch for your feature or bugfix
2. Make your changes
3. Write tests for your changes
4. Submit a pull request
5. Update documentation to reflect your changes 