# Todo Application Backend

FastAPI backend for Phase 2 Todo Application with JWT authentication and PostgreSQL database.

## Tech Stack

- **Framework**: FastAPI 0.115.5
- **ORM**: SQLModel 0.0.22
- **Database**: PostgreSQL (via Neon)
- **Authentication**: JWT with Better Auth compatibility
- **Server**: Uvicorn (ASGI)

## Setup

### Prerequisites

- Python 3.13+
- PostgreSQL database (Neon recommended)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (see Environment Variables section)

5. Initialize database:
```bash
python init_db.py
```

6. Run development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database

# Authentication
BETTER_AUTH_SECRET=your-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRY_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Configuration management
│   ├── database.py          # Database connection
│   ├── dependencies.py      # Reusable dependencies
│   ├── models.py            # SQLModel database models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   └── tasks.py         # Task CRUD endpoints
├── init_db.py               # Database initialization script
├── requirements.txt         # Python dependencies
├── pyproject.toml           # Project configuration
└── .env                     # Environment variables (not committed)
```

## API Endpoints

### Health Check
- `GET /` - API health check

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT)

### Tasks (Protected)
- `GET /api/tasks` - List user's tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get specific task
- `PUT /api/tasks/{id}` - Update task
- `PATCH /api/tasks/{id}/complete` - Toggle completion
- `DELETE /api/tasks/{id}` - Delete task

## Development

### Run with auto-reload:
```bash
uvicorn app.main:app --reload
```

### API Documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Manual testing via curl or Postman is sufficient per project constitution.

### Example: Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass","name":"John Doe"}'
```

### Example: Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"securepass"}'
```

## Security

- Passwords hashed with bcrypt
- JWT tokens with 7-day expiry
- User isolation enforced (users can only access their own tasks)
- CORS configured for frontend origin only
- Environment variables for sensitive data

## Deployment

See deployment documentation in `/specs/001-fullstack-todo-app/` for production deployment instructions.
