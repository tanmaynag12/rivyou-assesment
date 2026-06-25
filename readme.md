# Rivyou Backend Assessment

## Overview

This project is my submission for the Rivyou Backend Assessment. It is built using Django, Django REST Framework, and PostgreSQL.

The application provides:

- JWT-based user authentication
- Product CRUD APIs
- CSV product import command
- Tier-based product search
- Automated tests for authentication, CRUD, and search functionality

---

## Tech Stack

- Python 3
- Django
- Django REST Framework
- PostgreSQL
- Simple JWT
- Postman (API testing)

---

## Project Structure

```
accounts/        # Authentication
catalog/         # Product model, CRUD, CSV import
search/          # Search service and API
config/          # Project configuration
data/            # Product CSV
```

---

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd rivyou-assessment
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file using `.env.example`.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=rivyou
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

---

## Database Setup

Run migrations:

```bash
python manage.py migrate
```

Import products from the CSV:

```bash
python manage.py import_products
```

Expected output on first run:

```
Import complete: Created 1000 | Updated 0 | Skipped 0
```

Running the command again updates existing records instead of creating duplicates.

---

## Running the Server

```bash
python manage.py runserver
```

Server:

```
http://127.0.0.1:8000/
```

---

## Authentication Endpoints

| Method | Endpoint             | Description                       |
| ------ | -------------------- | --------------------------------- |
| POST   | `/api/auth/register` | Register a new user               |
| POST   | `/api/auth/login`    | Login and receive JWT tokens      |
| POST   | `/api/auth/logout`   | Logout (blacklists refresh token) |

---

## Product Endpoints

| Method | Endpoint             | Description                |
| ------ | -------------------- | -------------------------- |
| GET    | `/api/products/`     | List all products          |
| POST   | `/api/products/`     | Create a product           |
| GET    | `/api/products/<id>` | Retrieve a product         |
| PUT    | `/api/products/<id>` | Update a product           |
| PATCH  | `/api/products/<id>` | Partially update a product |
| DELETE | `/api/products/<id>` | Delete a product           |

---

## Search Endpoint

```
GET /api/search/?q=<query>
```

Authentication is required.

Search results are ranked using three tiers:

1. Category match
2. Tag match
3. Product name or description match

Each result includes:

- relevance_score
- rank_reason

Products appear only once in the highest matching tier.

---

## Running Tests

Run all tests:

```bash
python manage.py test
```

Run system checks:

```bash
python manage.py check
```

---

## Design Decisions

- Business logic is separated into service modules to keep views simple.
- JWT authentication is implemented using Simple JWT.
- Product data is imported through a custom Django management command.
- Tags are normalized during import and CRUD operations.
- Search uses a tier-based approach where category matches have the highest priority, followed by tag matches, and then product name or description matches.
- Automated tests cover authentication, product CRUD operations, and search functionality.

---

## Notes

- PostgreSQL is required.
- The provided CSV file should be imported before using the search functionality.
- JWT authentication is required for all protected endpoints.
