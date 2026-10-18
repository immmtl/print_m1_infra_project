# Проверка паролей

Учебный проект на FastAPI для проверки надёжности паролей и генерации случайных паролей.
На текущем этапе доступны `/health` и `/version`.

## Запуск

Нужен Python 3.10 или новее. Команды для macOS и Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app_final:app --reload
```

Документация API: http://127.0.0.1:8000/docs

Для запуска без автоматической перезагрузки:

```bash
python -m uvicorn app_final:app
```

## Проверка работы

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/version
```

Ожидаемые ответы: `{"status":"ok"}` и `{"version":"0.1.0"}`.
Uvicorn выводит сообщения о запуске и HTTP-запросах в терминал.
