# Руководство разработчика

Это руководство предоставляет информацию для разработчиков, которые хотят расширить, изменить или внести вклад в проект.

## Структура проекта

```
├── tg_bot/                    # Компонент Telegram-бота
│   ├── src/                   # Исходный код
│   │   ├── configs/           # Настройки конфигурации
│   │   ├── db/                # Модели и репозитории базы данных
│   │   ├── rabbit/            # Сервис RabbitMQ
│   │   ├── main.py            # Точка входа
│   │   ├── middlewares.py     # Компоненты промежуточного ПО
│   │   └── timer.py           # Функциональность таймера чата
│   ├── .env.sample            # Шаблон переменных окружения
│   ├── Dockerfile             # Конфигурация Docker
│   └── requirements.txt       # Зависимости Python
│
├── worker/                    # Компонент сервиса-обработчика
│   ├── src/                   # Исходный код
│   │   ├── ai_agent/          # Функциональность ИИ-обработки
│   │   │   ├── models/        # Модели данных
│   │   │   ├── utils/         # Служебные функции
│   │   │   ├── extra_data/    # Справочные данные для ИИ
│   │   │   ├── mistral_client.py  # Клиент Mistral AI
│   │   │   ├── analysis_pipeline.py  # Конвейер анализа
│   │   │   └── text_processing_pipeline.py  # Конвейер обработки текста
│   │   ├── configs/           # Настройки конфигурации
│   │   ├── db/                # Модели и репозитории базы данных
│   │   ├── google_drive/      # Интеграция с Google Drive
│   │   │   ├── api_key/       # Учетные данные Google API
│   │   │   ├── google_drive_uploader.py  # Функциональность загрузки в Drive
│   │   │   └── utils.py       # Служебные функции Drive
│   │   └── main.py            # Точка входа
│   ├── .env.sample            # Шаблон переменных окружения
│   ├── Dockerfile             # Конфигурация Docker
│   └── requirements.txt       # Зависимости Python
│
├── docker-compose.yaml        # Конфигурация Docker Compose
├── Makefile                   # Команды Make
└── README.md                  # Обзор проекта
```

## Настройка среды разработки

### Локальная разработка

1. Клонируйте репозиторий:
   ```bash
   git clone <url-репозитория>
   cd <директория-репозитория>
   ```

2. Настройте виртуальные окружения:
   ```bash
   # Для Telegram-бота
   cd tg_bot
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Для сервиса-обработчика
   cd ../worker
   python -m venv venv
   source venv/bin/activate  # На Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Настройте переменные окружения:
   ```bash
   # Для Telegram-бота
   cp tg_bot/.env.sample tg_bot/src/.env
   # Отредактируйте tg_bot/src/.env с вашим токеном Telegram-бота
   
   # Для сервиса-обработчика
   cp worker/.env.sample worker/src/.env
   # Отредактируйте worker/src/.env с вашим ключом API Mistral AI
   ```

4. Настройте локальные RabbitMQ и PostgreSQL:
   ```bash
   # Запустите сервисы с помощью Docker Compose
   docker-compose up -d rabbitmq postgres
   ```

### Запуск в режиме разработки

Чтобы запустить компоненты в режиме разработки:

**Telegram-бот**:
```bash
cd tg_bot
source venv/bin/activate  # На Windows: venv\Scripts\activate
cd src
python main.py
```

**Сервис-обработчик**:
```bash
cd worker
source venv/bin/activate  # На Windows: venv\Scripts\activate
cd src
python main.py
```

## Общие задачи разработки

### Добавление новой команды бота

1. Откройте `tg_bot/src/main.py`
2. Добавьте новую функцию-обработчик с декоратором `@dp.message()`
3. Реализуйте логику команды
4. Зарегистрируйте обработчик в диспетчере

Пример:
```python
@dp.message(Command("status"))
async def handle_status(message: types.Message, db: AsyncSession) -> None:
    # Реализация логики команды status
    await message.reply("Бот работает!")
```

### Расширение ИИ-анализа

1. Откройте `worker/src/ai_agent/analysis_pipeline.py`
2. Измените функцию `construct_prompt` для добавления новых правил извлечения
3. При необходимости обновите модель `AgriculturalOperation` в `worker/src/ai_agent/models/data_model.py`
4. Добавьте новые примеры в запрос для направления модели

### Добавление новой модели базы данных

1. Создайте или обновите определение модели в `db/models.py`
2. Создайте или обновите методы репозитория в `db/repositories.py`
3. При необходимости обновите схему базы данных

Пример:
```python
# В models.py
class NewEntity(Base):
    __tablename__ = "new_entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    value: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())

# В repositories.py
class NewEntityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_entity(self, name: str, value: float) -> NewEntity:
        entity = NewEntity(name=name, value=value)
        self.session.add(entity)
        await self.session.commit()
        return entity
```

## Тестирование

### Модульные тесты

Добавьте модульные тесты для новой функциональности в директорию `tests`:

```python
# tests/test_analysis_pipeline.py
import pytest
from ai_agent.analysis_pipeline import AnalysisPipeline

def test_analyze_text():
    pipeline = AnalysisPipeline()
    result = pipeline.analyze_text("Тестовое сообщение", message_date=date(2023, 4, 15))
    assert len(result) == 0  # Нет операций в тестовом сообщении
```

### Ручное тестирование

Протестируйте полный поток:
1. Отправьте сообщение боту в чате Telegram
2. Проверьте, что сообщение появляется в очереди RabbitMQ
3. Убедитесь, что обработчик обрабатывает сообщение
4. Проверьте, что документ Word и электронная таблица Excel загружаются в Google Drive
5. Проверьте, что отчет сохраняется в базе данных

## Развертывание

### Обновление в продакшене

1. Загрузите последние изменения:
   ```bash
   git pull origin main
   ```

2. Пересоберите и перезапустите службы:
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

### Добавление новых переменных окружения

1. Обновите файлы `.env.sample` с новыми переменными
2. При необходимости добавьте переменные в файл Docker Compose
3. Обновите документацию, чтобы отразить новые переменные

## Стиль кода и стандарты

- Следуйте рекомендациям PEP 8 для кода Python
- Используйте подсказки типов для параметров функций и возвращаемых значений
- Добавляйте строки документации к классам и функциям
- Поддерживайте функции небольшими и сосредоточенными на одной задаче
- Используйте описательные имена переменных и функций

## Внесение вклада

1. Создайте новую ветку для вашей функции или исправления ошибки
2. Внесите ваши изменения
3. Напишите тесты для ваших изменений
4. Отправьте запрос на включение (pull request)
5. Обновите документацию, чтобы отразить ваши изменения 