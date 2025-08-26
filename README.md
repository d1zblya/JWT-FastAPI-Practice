# JWTAuthFastAPI

Проект backend на FastAPI с JWT-аутентификацией, PostgreSQL и миграциями Alembic.  
Запускается через Docker Compose.

---

## Требования

- Docker & Docker Compose
- Python 3.12 (локально, если хочешь запускать без Docker)
- Файлы сертификатов в `certs/` (`jwt-private.pem` и `jwt-public.pem`)
- Файл `.env` с настройками БД и другими переменными

---

## Генерация RSA ключей

Для работы JWT аутентификации необходима пара RSA ключей — приватный и публичный.

---

```bash
# Сгенерировать приватный RSA ключ размером 2048 бит
openssl genrsa -out jwt-private.pem 2048
```

```bash
# Извлечь публичный ключ из приватного
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```

После этого помести оба файла (jwt-private.pem и jwt-public.pem) в папку certs/ проекта.

## Установка и запуск

1. Клонируй репозиторий:

```bash
git clone <repo-url>
cd JWTAuthFastAPI
```

2. Создай файл .env (если ещё нет) с содержимым:

```dotenv
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
```

3. Помести сертификаты в папку certs/
4. Запусти сервисы через Docker Compose:

```bash
docker-compose up --build
```

5. Открой http://localhost:8000/docs — Swagger UI твоего API.