# Contacts API

REST API for storing and managing contacts, developed using FastAPI and SQLAlchemy.

## Features

-   CRUD operations for contacts
-   Search contacts by name, surname, or email
-   Get a list of contacts with birthdays in the next N days
-   API documentation (Swagger)
-   Data validation using Pydantic
-   User authentication and authorization with JWT
-   Email verification for users
-   Rate limiting
-   Support for uploading avatars to Cloudinary
-   User data caching with Redis

## Technology Stack

-   FastAPI
-   SQLAlchemy
-   PostgreSQL
-   Alembic (migrations)
-   Pydantic
-   asyncpg
-   JWT
-   Cloudinary
-   Redis (caching)
-   Docker & Docker Compose

## Installation and Running

### Prerequisites

-   Python 3.10+
-   PostgreSQL
-   Redis
-   Poetry
-   Docker and Docker Compose (optional)

### Environment Variables Setup

1. Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```

2. Edit the `.env` file, setting appropriate values:
   - Database configuration
   - JWT secret key
   - SMTP server settings for sending emails
   - Cloudinary access keys
   - Redis configuration for caching

### Installing Dependencies

```bash
poetry install --no-root
```

### Running with Docker Compose

The easiest way to start the project:

```bash
docker-compose up -d
```

Applying migrations in Docker:

```bash
docker-compose exec app alembic upgrade head
```

### Running without Docker

#### Starting the database

```bash
docker run --name some-postgres -p 5433:5432 -e POSTGRES_PASSWORD=567234 -d postgres
```

#### Creating the database

1. Connect to PostgreSQL using any client (e.g., DBeaver)
2. Create a database named `contacts_app`

#### Applying migrations

```bash
poetry run alembic upgrade head
```

#### Running API

```bash
poetry run python main.py
```

The server will be available at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Swagger documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## New Features

### Password Reset Mechanism

API now supports secure password reset functionality:

1. User requests password reset by sending their email to the `/api/auth/request-password-reset` endpoint.
2. System sends an email to the user with a special reset token.
3. User inputs a new password and sends a request with the token to the `/api/auth/reset-password` endpoint.
4. System verifies the token and updates the user's password.

### User Roles and Access

Two user roles are now implemented in the system:
- `user` (default role)
- `admin` (enhanced rights)

Access restrictions:
- Only admins can change their avatar via the `/api/users/avatar` endpoint.
- Regular users will receive a 403 error when trying to access endpoints requiring admin rights.

## API Endpoints

### Authentication

-   `POST /api/auth/register` - Register a new user
-   `POST /api/auth/login` - Login to the system and get JWT token
-   `GET /api/auth/confirmed_email/{token}` - Confirm email
-   `POST /api/auth/request_email` - Request to resend email confirmation

#### Password Reset Request
```
POST /api/auth/request-password-reset
```
Request body:
```json
{
    "email": "user@example.com"
}
```
Response:
```json
{
    "message": "If your email is registered in the system, you will receive an instruction to reset your password"
}
```

#### Resetting password with token
```
POST /api/auth/reset-password
```
Request body:
```json
{
    "token": "your-reset-token",
    "password": "your-new-password"
}
```
Response:
```json
{
    "message": "Password successfully changed"
}
```

### Users

-   `GET /api/users/me` - Get information about the current user
-   `PATCH /api/users/avatar` - Update user avatar

#### Updating user avatar (only for admins)
```
PATCH /api/users/avatar
```
Request body: `form-data` with `file` field (image)

Response:
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "avatar": "https://example.com/avatar.jpg",
    "role": "admin"
}
```

### Contacts

-   `GET /api/contacts` - Get a list of all contacts
-   `GET /api/contacts/{contact_id}` - Get a contact by ID
-   `POST /api/contacts` - Create a new contact
-   `PUT /api/contacts/{contact_id}` - Update an existing contact
-   `DELETE /api/contacts/{contact_id}` - Delete a contact

### Additional Features

-   `GET /api/contacts/search?query={search_term}` - Search contacts by name, surname, or email
-   `GET /api/contacts/birthdays?days={days}` - Get contacts with birthdays in the next N days

### Utilities

-   `GET /api/healthchecker` - Check API functionality and database connection

docker-compose up
