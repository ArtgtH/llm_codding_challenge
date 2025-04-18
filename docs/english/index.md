# Система обработки сельскохозяйственных отчетов

Добро пожаловать в документацию Системы обработки сельскохозяйственных отчетов. Эта система автоматизирует извлечение структурированных данных из сельскохозяйственных отчетов в свободной форме, отправленных через Telegram.

## Содержание документации

### Начало работы
- [Обзор проекта](getting_started/project_overview.md)
- [Установка и настройка](getting_started/setup_and_installation.md)

### Компоненты системы
- [Telegram-бот](components/telegram_bot.md)
- [Сервис-обработчик](components/worker_service.md)

### Техническая документация
- [ИИ-обработка текста](technical/ai_text_processing.md)
- [Интеграция с Google Drive](technical/google_drive_integration.md)
- [Модели данных](technical/data_model.md)
- [API и точки доступа](technical/api_and_endpoints.md)

### Разработка
- [Руководство разработчика](development/development_guide.md)
- [Будущие улучшения](development/future_enhancements.md)

### Справка
- [Устранение неполадок](help/troubleshooting.md)
- [Дополнительные ресурсы](help/additional_resources.md)

## Быстрый старт

Чтобы начать использование системы:

1. Следуйте руководству [Установка и настройка](getting_started/setup_and_installation.md)
2. Настройте переменные окружения для Telegram-бота и сервиса-обработчика
3. Настройте учетные данные Google Drive
4. Запустите службы с помощью Docker Compose

## Архитектура системы

```
┌───────────────┐       ┌────────────┐       ┌────────────────┐
│ Telegram-чат  │       │            │       │                │
│               │──────▶│ Telegram-  │──────▶│                │
└───────────────┘       │ бот        │       │                │
                        └────────────┘       │                │
                              │              │   PostgreSQL   │
                              │              │   База данных  │
                              ▼              │                │
                        ┌────────────┐       │                │
                        │            │       │                │
                        │  RabbitMQ  │       └────────────────┘
                        │            │               ▲
                        └────────────┘               │
                              │                      │
                              │                      │
                              ▼                      │
                        ┌────────────┐       ┌────────────────┐
                        │            │       │                │
                        │  Сервис-   │──────▶│  Google Drive  │
                        │  обработчик│       │                │
                        └────────────┘       └────────────────┘
                              │
                              │
                              ▼
                        ┌────────────┐
                        │            │
                        │ Mistral AI │
                        │            │
                        └────────────┘
```

## Полезные команды

Запуск служб:
```bash
docker-compose up -d
```

Проверка логов сервисов:
```bash
docker-compose logs -f tg_bot
docker-compose logs -f worker
```

Доступ к интерфейсу управления RabbitMQ:
```
http://localhost:15672
``` 