# JurisLink

A legal aid platform for people who can't afford private lawyers. It enables clients to describe legal issues, upload documents for automatic classification and summarization, match with lawyers, book appointments, and track cases end-to-end.

This is an academic full-stack project with clean, well-organized, and well-documented code.

## Tech Stack

- **Frontend**: React 18 + React Router + Vite (plain CSS with CSS Modules)
- **Backend**: Python + FastAPI (async, single service)
- **Database**: MongoDB (Motor for async operations)
- **NLP**: scikit-learn for classification, sumy for document summarization
- **Auth**: JWT tokens with bcrypt password hashing

## Project Structure

```
jurislink/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── core/
│   │   │   ├── config.py        # Settings from environment
│   │   │   └── security.py      # JWT & password utilities
│   │   ├── db/
│   │   │   └── mongodb.py       # Database connection setup
│   │   ├── models/              # Pydantic request/response schemas
│   │   │   ├── user_model.py
│   │   │   ├── case_model.py
│   │   │   └── appointment_model.py
│   │   ├── routers/             # One file per resource
│   │   │   ├── health_router.py
│   │   │   ├── auth_router.py
│   │   │   ├── case_router.py
│   │   │   ├── appointment_router.py
│   │   │   └── nlp_router.py
│   │   └── services/            # Business logic
│   │       ├── classification_service.py
│   │       ├── summarization_service.py
│   │       ├── case_service.py
│   │       └── appointment_service.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── HealthIndicator.jsx
│   │   │   └── HealthIndicator.module.css
│   │   ├── pages/               # Route-level views (to be added)
│   │   ├── services/            # API call wrappers
│   │   │   ├── healthService.js
│   │   │   ├── authService.js
│   │   │   ├── caseService.js
│   │   │   └── appointmentService.js
│   │   ├── styles/
│   │   │   └── variables.css    # CSS variables & global styles
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.jsx
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── .env.example
└── README.md
```

## Naming Conventions

- **Python files/functions/variables**: `snake_case`
- **Python classes/Pydantic models**: `PascalCase`
- **React components/files**: `PascalCase`
- **React variables/functions**: `camelCase`
- **CSS Modules**: Match component name (e.g., `CaseTracker.module.css`)
- **MongoDB collections**: `lowercase_plural` (e.g., `users`, `cases`, `appointments`)
- **API routes**: `/lowercase-hyphenated` (e.g., `/cases/{case_id}`)
- **Environment variables**: `UPPER_SNAKE_CASE`

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB running locally or connection string available

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your MongoDB connection string and other settings.

5. Run the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```
   
   The backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```
   
   The frontend will be available at `http://localhost:3000`

### Verify Connectivity

Once both servers are running:
1. Open `http://localhost:3000` in your browser
2. You should see the JurisLink welcome page
3. The **System Status** indicator should show:
   - Backend: `running` (green)
   - Database: `connected` (green) — if MongoDB is configured and running

## Architecture Rules

### Router Layer
- Routers handle HTTP request/response only
- All business logic delegated to services
- Every request/response must have a Pydantic model in `models/`

### Service Layer
- Contains all business logic
- Each service function has a docstring explaining its purpose
- Async/await for database operations (Motor)
- Services are instantiated in routers

### Database Layer
- `db/mongodb.py` handles connection lifecycle
- Connected on app startup, closed on shutdown
- Async operations using Motor

### Frontend Services
- API wrappers in `src/services/` — one file per resource
- Components import and call these services
- Services handle token management (JWT)
- Components focus on rendering, not API calls

## Features to Build (In Order)

1. **Auth Module** → user registration, login, JWT tokens
2. **Case Intake** → clients describe issues, upload documents
3. **Classification** → NLP classifies issues automatically
4. **Summarization** → documents summarized and key phrases extracted
5. **Lawyer Matching** → match cases to available lawyers
6. **Appointment Booking** → schedule appointments
7. **Case Tracking** → real-time status updates
8. **Admin Dashboard** → manage cases, monitor system

## Code Quality Standards

- Every service function has a docstring
- Type hints on all function parameters and returns
- Async/await for all I/O operations
- Error handling with appropriate HTTP status codes
- No hardcoded secrets or URIs — all through environment variables
- CSS Modules for component-scoped styles, variables.css for shared theming
- Clean separation of concerns (routes → services → models)

## Environment Variables

### Backend (.env)
```
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=jurislink
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_PORT=8000
BACKEND_HOST=0.0.0.0
FRONTEND_URL=http://localhost:3000
ENVIRONMENT=development
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
```

## Development Workflow

1. Create a new feature branch from main
2. For each new feature:
   - Add models in `backend/app/models/`
   - Implement service logic in `backend/app/services/`
   - Create router in `backend/app/routers/`
   - Add API service wrapper in `frontend/src/services/`
   - Create React components in `frontend/src/components/` or `frontend/src/pages/`
3. Test feature end-to-end
4. Create pull request with clear description

## Troubleshooting

### Backend won't start
- Check MongoDB connection: `mongosh`
- Verify .env file exists and has correct MongoDB URI
- Check Python version: `python --version` (should be 3.9+)

### Frontend can't connect to backend
- Verify backend is running on http://localhost:8000
- Check CORS configuration in `backend/app/main.py`
- Check frontend API URL in `.env`: `REACT_APP_API_URL=http://localhost:8000`

### Health check shows database disconnected
- Ensure MongoDB is running
- Update MONGODB_URI in backend `.env`
- Verify MongoDB user credentials if using auth

## License

Academic project for legal aid education.
