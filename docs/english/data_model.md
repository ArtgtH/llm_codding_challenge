# Data Models

This document describes the key data models used throughout the application.

## AgriculturalOperation

The `AgriculturalOperation` model represents structured agricultural operation data extracted from messages.

```python
class AgriculturalOperation(BaseModel):
    date: Optional[date] = None
    subdivision: Optional[str] = None
    operation: Optional[str] = None
    crop: Optional[str] = None
    daily_area: Optional[float] = None
    total_area: Optional[float] = None
    daily_yield: Optional[float] = None
    total_yield: Optional[float] = None
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `date` | `date` | Date when the operation was performed |
| `subdivision` | `str` | Agricultural subdivision or farm unit |
| `operation` | `str` | Type of agricultural operation (e.g., "Пахота", "Сев") |
| `crop` | `str` | Crop being processed (e.g., "Пшеница озимая товарная") |
| `daily_area` | `float` | Area processed on the reported day (in hectares) |
| `total_area` | `float` | Cumulative area processed (in hectares) |
| `daily_yield` | `float` | Yield collected on the reported day (in centners) |
| `total_yield` | `float` | Cumulative yield collected (in centners) |

## MessageDTO

The `MessageDTO` model represents message data transferred between the Telegram bot and worker service.

```python
@dataclass
class MessageDTO:
    chat_id: str
    chat_title: str
    user: str
    message_text: str
    time: str
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `chat_id` | `str` | Telegram chat ID |
| `chat_title` | `str` | Title of the Telegram chat |
| `user` | `str` | Full name of the user who sent the message |
| `message_text` | `str` | Content of the message |
| `time` | `str` | Timestamp of the message (format: "DD/MM/YYYY, HH:MM:SS") |

## Database Models

### Message

Represents a message stored in the database:

```python
class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger)
    chat_title: Mapped[str] = mapped_column(String)
    user_id: Mapped[int] = mapped_column(BigInteger)
    user_name: Mapped[str] = mapped_column(String)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
```

### DailyReport

Represents a daily agricultural report stored in the database:

```python
class DailyReport(Base):
    __tablename__ = "daily_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[str] = mapped_column(String)
    date: Mapped[date] = mapped_column(Date)
    report: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
``` 