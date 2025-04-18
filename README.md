# Начало работы

1) Необходимо скопировать .env.sample ```cp .env.sample src/.env``` для worker и tg_bot
2) В .env tg_bot ставим токен бота ТГ
3) В .env worker ставим токен для MistralAI
4) В worker/src/google_drive/api_key/ кладем .json с клиентом для драйва
5) Прописываем название json-файла в [путь к .json](https://github.com/ArtgtH/llm_codding_challenge/blob/621518c33d35e3e5efaaf108e4bafb0b8bf28b73/worker/src/google_drive/google_drive_uploader.py#L21)
6) Запускаем
