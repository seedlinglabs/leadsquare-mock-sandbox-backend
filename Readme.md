# LeadSquared Mock Backend

A mock CRM backend API for managing users and leads, built with FastAPI and PostgreSQL.

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Create a `.env` file from the example:
```bash
cp .env.example .env
```

3. Update the database URL in `.env` with your PostgreSQL credentials.

4. Run the application:
```bash
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### Users
- `POST /api/v1/users/` - Create a user
- `GET /api/v1/users/` - List all users
- `GET /api/v1/users/{id}` - Get a user by ID
- `PUT /api/v1/users/{id}` - Update a user
- `DELETE /api/v1/users/{id}` - Delete a user

### Leads
- `POST /api/v1/leads/` - Create a lead
- `GET /api/v1/leads/` - List all leads (with optional filters)
- `GET /api/v1/leads/{id}` - Get a lead by ID
- `PUT /api/v1/leads/{id}` - Update a lead
- `PATCH /api/v1/leads/{id}/status` - Update lead status
- `DELETE /api/v1/leads/{id}` - Delete a lead

## Project Structure

```
app/
├── main.py              # Application entry point
├── core/
│   ├── config.py        # Settings and configuration
│   └── database.py      # Database connection
├── models/
│   ├── user.py          # User SQLAlchemy model
│   └── lead.py          # Lead SQLAlchemy model
├── schemas/
│   ├── user.py          # User Pydantic schemas
│   └── lead.py          # Lead Pydantic schemas
├── crud/
│   ├── user.py          # User CRUD operations
│   └── lead.py          # Lead CRUD operations
└── api/routes/
    ├── users.py         # User API routes
    └── leads.py         # Lead API routes
```
