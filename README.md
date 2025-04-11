# Contacts API

REST API для зберігання та управління контактами, розроблене з використанням FastAPI та SQLAlchemy.

## Особливості

-   CRUD операції для контактів
-   Пошук контактів за ім'ям, прізвищем або email
-   Отримання списку контактів з днями народження на найближчі N днів
-   Документація API (Swagger)
-   Валідація даних за допомогою Pydantic
-   Аутентифікація та авторизація користувачів з JWT
-   Верифікація електронної пошти користувачів
-   Обмеження кількості запитів
-   Підтримка завантаження аватарів до Cloudinary

## Стек технологій

-   FastAPI
-   SQLAlchemy
-   PostgreSQL
-   Alembic (міграції)
-   Pydantic
-   asyncpg
-   JWT
-   Cloudinary
-   Docker & Docker Compose

## Встановлення та запуск

### Попередні вимоги

-   Python 3.10+
-   PostgreSQL
-   Poetry
-   Docker та Docker Compose (опціонально)

### Налаштування змінних середовища

1. Скопіюйте файл `.env.example` в `.env`:
```bash
cp .env.example .env
```

2. Відредагуйте `.env` файл, встановивши відповідні значення:
   - Налаштування бази даних
   - Секретний ключ для JWT
   - Налаштування SMTP сервера для відправки пошти
   - Ключі доступу до Cloudinary

### Встановлення залежностей

```bash
poetry install --no-root
```

### Запуск з Docker Compose

Найпростіший спосіб запустити проект:

```bash
docker-compose up -d
```

Застосування міграцій в Docker:

```bash
docker-compose exec app alembic upgrade head
```

### Запуск без Docker

#### Запуск бази даних

```bash
docker run --name some-postgres -p 5433:5432 -e POSTGRES_PASSWORD=567234 -d postgres
```

#### Створення бази даних

1. Підключіться до PostgreSQL за допомогою будь-якого клієнта (наприклад, DBeaver)
2. Створіть базу даних з іменем `contacts_app`

#### Застосування міграцій

```bash
poetry run alembic upgrade head
```

#### Запуск API

```bash
poetry run python main.py
```

Сервер буде доступний за адресою: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Документація Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## API Endpoints

### Аутентифікація

-   `POST /api/auth/register` - Реєстрація нового користувача
-   `POST /api/auth/login` - Вхід в систему та отримання JWT токена
-   `GET /api/auth/confirmed_email/{token}` - Підтвердження email
-   `POST /api/auth/request_email` - Запит на повторну відправку листа для підтвердження email

### Користувачі

-   `GET /api/users/me` - Отримати інформацію про поточного користувача
-   `PATCH /api/users/avatar` - Оновити аватар користувача

### Контакти

-   `GET /api/contacts` - Отримати список усіх контактів
-   `GET /api/contacts/{contact_id}` - Отримати контакт за ID
-   `POST /api/contacts` - Створити новий контакт
-   `PUT /api/contacts/{contact_id}` - Оновити існуючий контакт
-   `DELETE /api/contacts/{contact_id}` - Видалити контакт

### Додаткові функції

-   `GET /api/contacts/search?query={search_term}` - Пошук контактів за ім'ям, прізвищем або email
-   `GET /api/contacts/birthdays?days={days}` - Отримати контакти з днями народження в найближчі N днів

### Утиліти

-   `GET /api/healthchecker` - Перевірка працездатності API та з'єднання з базою даних

docker-compose up
