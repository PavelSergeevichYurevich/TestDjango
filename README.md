# Instagram Sync Service (Django + DRF)

Тестовое задание: сервис синхронизирует посты из Instagram Graph API в локальную БД и позволяет создавать комментарии через API.

## Стек
- Python 3.13
- Django 5.2.11
- Django REST Framework 3.16.1
- PostgreSQL 16
- Docker / Docker Compose

## Запуск проекта
1. Скопировать переменные окружения:
```bash
cp .env.example .env
```

2. Запустить приложение и БД:
```bash
docker compose up --build -d
```

3. Применить миграции:
```bash
docker compose exec web python manage.py migrate
```

4. Проверка health endpoint:
```bash
curl http://localhost:8000/api/health/
```

Ожидаемый ответ:
```json
{"status":"ok"}
```

## Переменные окружения
Файл `.env.example`:

```env
DEBUG=1
SECRET_KEY=change-me
ALLOWED_HOSTS=127.0.0.1,localhost

POSTGRES_DB=testdjango
POSTGRES_USER=testdjango
POSTGRES_PASSWORD=testdjango
POSTGRES_HOST=db
POSTGRES_PORT=5432

INSTAGRAM_ACCESS_TOKEN=
INSTAGRAM_USER_ID=
```

Обязательные для бизнес-эндпоинтов:
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_USER_ID`

## API endpoints
- `GET /api/health/` - проверка доступности API и БД.
- `POST /api/sync/` - синхронизация всех постов Instagram в локальную БД (с пагинацией по `next`, upsert).
- `GET /api/posts/` - список постов из локальной БД (`CursorPagination`).
- `POST /api/posts/{id}/comment/` - создать комментарий к посту (где `{id}` - локальный PK поста).

### Примеры запросов
Синхронизация:
```bash
curl -X POST http://localhost:8000/api/sync/
```

Список постов:
```bash
curl http://localhost:8000/api/posts/
```

Комментарий:
```bash
curl -X POST http://localhost:8000/api/posts/1/comment/ \
  -H "Content-Type: application/json" \
  -d '{"text":"hello from api"}'
```

## Тесты
Реализованы интеграционные тесты для `POST /api/posts/{id}/comment/`:
1. успешное создание комментария;
2. локальный пост не найден;
3. пост есть локально, но не найден в Instagram.

В тестах нет реальных HTTP-запросов к Instagram (используется мокирование).

Запуск:
```bash
docker compose exec web python manage.py test posts -v 2
```

## Архитектура
- `posts/services/instagram_client.py` - HTTP-клиент Instagram API.
- `posts/services/instagram_service.py` - бизнес-логика синхронизации и комментирования.
- `posts/views.py` - тонкий API-слой DRF.

## Known limitations
- Нет OAuth-флоу (по ТЗ используется готовый токен).
- Нет rate-limit/retry/backoff для Instagram API.
- Нет отдельного structured logging.
- Нет CI-конфига в репозитории.

## Чеклист перед сдачей
1. `docker compose up --build -d` выполняется без ошибок.
2. `docker compose exec web python manage.py migrate` проходит.
3. `docker compose exec web python manage.py test posts -v 2` - все тесты зелёные.
4. Проверены endpoint-ы:
   - `GET /api/health/`
   - `POST /api/sync/`
   - `GET /api/posts/`
   - `POST /api/posts/{id}/comment/`
5. В `.env` заполнены `INSTAGRAM_ACCESS_TOKEN` и `INSTAGRAM_USER_ID`.

