# Модели данных

В этом документе описываются ключевые модели данных, используемые во всем приложении.

## AgriculturalOperation (Сельскохозяйственная операция)

Модель `AgriculturalOperation` представляет структурированные данные о сельскохозяйственных операциях, извлеченные из сообщений.

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

### Поля

| Поле | Тип | Описание |
|-------|------|-------------|
| `date` | `date` | Дата выполнения операции |
| `subdivision` | `str` | Сельскохозяйственное подразделение или фермерская единица |
| `operation` | `str` | Тип сельскохозяйственной операции (например, "Пахота", "Сев") |
| `crop` | `str` | Обрабатываемая культура (например, "Пшеница озимая товарная") |
| `daily_area` | `float` | Площадь, обработанная в отчетный день (в гектарах) |
| `total_area` | `float` | Совокупная обработанная площадь (в гектарах) |
| `daily_yield` | `float` | Урожай, собранный в отчетный день (в центнерах) |
| `total_yield` | `float` | Совокупный собранный урожай (в центнерах) |

## MessageDTO (DTO сообщения)

Модель `MessageDTO` представляет данные сообщений, передаваемые между Telegram-ботом и сервисом-обработчиком.

```python
@dataclass
class MessageDTO:
    chat_id: str
    chat_title: str
    user: str
    message_text: str
    time: str
```

### Поля

| Поле | Тип | Описание |
|-------|------|-------------|
| `chat_id` | `str` | Идентификатор чата Telegram |
| `chat_title` | `str` | Название чата Telegram |
| `user` | `str` | Полное имя пользователя, отправившего сообщение |
| `message_text` | `str` | Содержание сообщения |
| `time` | `str` | Временная метка сообщения (формат: "DD/MM/YYYY, HH:MM:SS") |

## Модели базы данных

### Message (Сообщение)

Представляет сообщение, хранящееся в базе данных:

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

### DailyReport (Ежедневный отчет)

Представляет ежедневный сельскохозяйственный отчет, хранящийся в базе данных:

```python
class DailyReport(Base):
    __tablename__ = "daily_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[str] = mapped_column(String)
    date: Mapped[date] = mapped_column(Date)
    report: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
``` 