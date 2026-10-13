# JurisLink - Complete Project Guide

**Project Status**: ✅ Backend Complete & Running | Frontend Integration In Progress  
**Last Updated**: September 3, 2026  
**Tech Stack**: React 18 + Vite | FastAPI + Python 3.9+ | MongoDB + Motor

---

## 📋 Quick Navigation

- **[Getting Started](#getting-started)** - Setup & run in 5 minutes
- **[Architecture](#architecture)** - System design & structure
- **[API Endpoints](#api-endpoints)** - Complete API reference
- **[Development Guide](#development-guide)** - How to build features
- **[Troubleshooting](#troubleshooting)** - Common issues & solutions

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB running locally (or connection string)

### Backend Setup (5 min)

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

**Verify**: Visit http://localhost:8000/docs (Swagger UI)

### Frontend Setup (5 min)

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

**Verify**: Visit http://localhost:3000  
**Test Login**: test@example.com / password123

### MongoDB Setup

```bash
# Start MongoDB
mongod

# Verify connection
mongosh
use jurislink
```

---

## 🏗️ Architecture

### System Overview

```
┌──────────────────────────┐
│   React Frontend         │
│   http://localhost:3000  │
└────────────┬─────────────┘
             │ HTTP/JSON
             ↓
┌──────────────────────────────────────────┐
│   FastAPI Backend                        │
│   http://localhost:8000                  │
│                                          │
│  ├─ Routers (5 files)                   │
│  │  ├─ auth_router.py                   │
│  │  ├─ case_router.py                   │
│  │  ├─ appointment_router.py            │
│  │  ├─ health_router.py                 │
│  │  └─ [5 more routers]                 │
│  │                                      │
│  ├─ Services (10 files)                 │
│  │  ├─ auth_service.py                  │
│  │  ├─ case_service.py                  │
│  │  └─ [8 more services]                │
│  │                                      │
│  └─ Models & Database Layer             │
└────────────┬─────────────────────────────┘
             │ Motor (Async Driver)
             ↓
     ┌───────────────────┐
     │  MongoDB          │
     │  localhost:27017  │
     └───────────────────┘
```

### Project Structure

```
jurislink/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── core/
│   │   │   ├── config.py        # Environment config
│   │   │   └── security.py      # JWT & password utilities
│   │   ├── db/
│   │   │   └── mongodb.py       # Database connection
│   │   ├── models/              # Pydantic schemas (9 files)
│   │   ├── routers/             # API endpoints (10 files)
│   │   └── services/            # Business logic (10 files)
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Route views
│   │   ├── services/            # API wrappers (8+ files)
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── index.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example
│   └── .env
│
├── README.md                    # Main project README
└── PROJECT.md                   # This file

```

### Database Collections (9 Total)

| Collection | Purpose | Fields |
|-----------|---------|--------|
| `users` | User accounts | email, password_hash, full_name, role, created_at |
| `lawyers` | Lawyer profiles | user_id, specialization, bio, hourly_rate, availability |
| `cases` | Legal cases | client_id, title, description, category, status, documents |
| `appointments` | Scheduled appointments | client_id, lawyer_id, case_id, slot_time, status |
| `documents` | Case documents | case_id, file_url, extracted_text, summary |
| `notifications` | User notifications | user_id, message, type, read, created_at |
| `case_updates` | Case history | case_id, old_status, new_status, updated_by, timestamp |
| `legal_cases` | Public legal cases | title, summary, precedent_year, court |
| `legal_qa` | Public Q&A | question, answer, category, helpful_count |

---

## 🔌 API Endpoints

### Authentication (3 endpoints)

#### POST /auth/signup
Register a new user

```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "securepassword",
  "role": "client"  // "client" or "lawyer"
}
```

**Response** (201):
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "client",
  "created_at": "2026-09-03T10:00:00Z"
}
```

#### POST /auth/login
Get JWT token

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response** (200):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "role": "client"
  }
}
```

#### GET /auth/me
Get current user (requires token)

**Response** (200):
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "client"
}
```

---

### Cases (6 endpoints)

#### POST /cases
Create a new case (requires auth)

```json
{
  "title": "Landlord won't return deposit",
  "description": "I moved out on January 1st...",
  "document_url": null
}
```

**Response** (201):
```json
{
  "id": "case_id",
  "client_id": "user_id",
  "title": "Landlord won't return deposit",
  "description": "I moved out on January 1st...",
  "category": "tenancy",  // Auto-classified
  "status": "submitted",
  "created_at": "2026-09-03T10:00:00Z"
}
```

#### GET /cases/{id}
Get case details

**Response** (200):
```json
{
  "id": "case_id",
  "client_id": "user_id",
  "title": "Landlord won't return deposit",
  "category": "tenancy",
  "status": "submitted",
  "lawyer_id": null,
  "documents": [],
  "updates": []
}
```

#### GET /cases/me
List your cases (requires auth)

**Response** (200):
```json
{
  "cases": [
    { "id": "case_1", "title": "Case 1", "status": "submitted" },
    { "id": "case_2", "title": "Case 2", "status": "assigned" }
  ],
  "total": 2
}
```

#### PATCH /cases/{id}/status
Update case status (lawyer/admin only)

```json
{
  "status": "under_review"  // Valid: submitted, under_review, in_progress, resolved, closed
}
```

#### POST /cases/{id}/assign
Assign case to lawyer (admin only)

```json
{
  "lawyer_id": "lawyer_user_id"
}
```

#### GET /cases/lawyer/{id}
Get cases for a lawyer (admin only)

---

### Appointments (5 endpoints)

#### POST /appointments
Book an appointment (auto-detects conflicts)

```json
{
  "case_id": "case_id",
  "lawyer_id": "lawyer_user_id",
  "slot_time": "2026-09-10T14:00:00Z"
}
```

**Response** (201):
```json
{
  "id": "appointment_id",
  "client_id": "user_id",
  "lawyer_id": "lawyer_user_id",
  "case_id": "case_id",
  "slot_time": "2026-09-10T14:00:00Z",
  "status": "scheduled",
  "created_at": "2026-09-03T10:00:00Z"
}
```

#### GET /appointments/{id}
Get appointment details

#### GET /appointments/me
List your appointments

#### PATCH /appointments/{id}
Reschedule appointment

```json
{
  "slot_time": "2026-09-11T15:00:00Z"
}
```

#### POST /appointments/{id}/cancel
Cancel appointment

---

### Health (1 endpoint)

#### GET /health/status
Check system health

**Response** (200):
```json
{
  "backend": "running",
  "database": "connected",
  "timestamp": "2026-09-03T10:00:00Z"
}
```

---

### Additional Endpoints

**Lawyers** (GET /lawyers, GET /lawyers/{id}, POST /lawyers)  
**Documents** (POST, GET, DELETE)  
**Notifications** (GET, PATCH)  
**Legal Search** (GET /legal/search, GET /legal/qa)  
**NLP** (POST /nlp/classify, POST /nlp/summarize)

---

## 🛠️ Development Guide

### Adding a New Feature

#### Step 1: Define the Data Model
Create `backend/app/models/feature_model.py`:

```python
from pydantic import BaseModel
from datetime import datetime

class FeatureCreate(BaseModel):
    name: str
    description: str

class FeatureOut(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
```

#### Step 2: Create the Service
Create `backend/app/services/feature_service.py`:

```python
class FeatureService:
    def __init__(self, db):
        self.db = db
        self.collection = db["features"]
    
    async def create_feature(self, feature_create: FeatureCreate, user_id: str):
        """Create a new feature."""
        feature = {
            **feature_create.dict(),
            "user_id": user_id,
            "created_at": datetime.utcnow()
        }
        result = await self.collection.insert_one(feature)
        return {"id": str(result.inserted_id), **feature}
    
    async def get_feature(self, feature_id: str):
        """Get a feature by ID."""
        from bson import ObjectId
        feature = await self.collection.find_one({"_id": ObjectId(feature_id)})
        if not feature:
            return None
        feature["id"] = str(feature["_id"])
        return feature
```

#### Step 3: Create the Router
Create `backend/app/routers/feature_router.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from app.models.feature_model import FeatureCreate, FeatureOut
from app.services.feature_service import FeatureService
from app.core.security import get_current_user
from app.db.mongodb import get_db

router = APIRouter(prefix="/features", tags=["features"])

@router.post("", response_model=FeatureOut)
async def create_feature(
    feature: FeatureCreate,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new feature."""
    service = FeatureService(db)
    result = await service.create_feature(feature, current_user["id"])
    return result

@router.get("/{feature_id}", response_model=FeatureOut)
async def get_feature(feature_id: str, db = Depends(get_db)):
    """Get a feature by ID."""
    service = FeatureService(db)
    feature = await service.get_feature(feature_id)
    if not feature:
        raise HTTPException(status_code=404, detail="Feature not found")
    return feature
```

#### Step 4: Register the Router
Update `backend/app/main.py`:

```python
from app.routers import feature_router

app.include_router(feature_router.router)
```

#### Step 5: Create Frontend Service Wrapper
Create `frontend/src/services/featureService.js`:

```javascript
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export const featureService = {
  createFeature: async (feature) => {
    const token = localStorage.getItem('token');
    const response = await axios.post(`${API_URL}/features`, feature, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  getFeature: async (featureId) => {
    const response = await axios.get(`${API_URL}/features/${featureId}`);
    return response.data;
  }
};
```

#### Step 6: Create React Component
Create `frontend/src/components/FeatureForm.jsx`:

```javascript
import React, { useState } from 'react';
import { featureService } from '../services/featureService';

export const FeatureForm = () => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const result = await featureService.createFeature({ name, description });
      console.log('Feature created:', result);
      setName('');
      setDescription('');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Feature name"
        required
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Feature'}
      </button>
    </form>
  );
};
```

### Naming Conventions

| Type | Convention | Example |
|------|-----------|---------|
| Python files | snake_case | `user_service.py` |
| Python classes | PascalCase | `UserService` |
| Python variables | snake_case | `user_id` |
| React files | PascalCase | `UserForm.jsx` |
| React components | PascalCase | `export const UserForm` |
| React variables | camelCase | `userId` |
| CSS Modules | Match component | `UserForm.module.css` |
| MongoDB collections | lowercase_plural | `users`, `cases` |
| API routes | /lowercase-hyphenated | `/user-cases` |
| Environment vars | UPPER_SNAKE_CASE | `MONGODB_URI` |

### Code Quality Standards

✅ **Type hints** on all functions  
✅ **Docstrings** for all services  
✅ **Async/await** for all I/O  
✅ **Error handling** with proper HTTP status codes  
✅ **No hardcoded secrets** - use environment variables  
✅ **CSS Modules** for component styles  
✅ **Pydantic models** for all request/response validation

---

## 🔍 Testing API Endpoints

### Using cURL

```bash
# Health check
curl http://localhost:8000/health/status

# Sign up
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "password123",
    "role": "client"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Using Swagger UI

1. Visit: http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Enter parameters
5. Click "Execute"

### Using Postman

1. Create a new collection
2. Add requests for each endpoint
3. Set authorization header: `Authorization: Bearer {token}`
4. Test each endpoint

---

## 📦 Environment Variables

### Backend (.env)

```env
# Database
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=jurislink

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3000

# Environment
ENVIRONMENT=development
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

---

## ❌ Troubleshooting

### Backend won't start

```
Error: "Connection refused"
→ Solution: Start MongoDB (mongod)

Error: "MONGODB_URI not found"
→ Solution: Create .env file from .env.example

Error: "Port 8000 already in use"
→ Solution: Use different port: --port 8001
```

### Frontend can't connect to backend

```
Error: "Failed to fetch"
→ Solution: Check backend is running on http://localhost:8000

Error: "CORS error"
→ Solution: Check FRONTEND_URL in backend .env matches your frontend URL
```

### Database connection failed

```
Error: "Connection timeout"
→ Solution: Make sure MongoDB is running (mongod)

Error: "Authentication failed"
→ Solution: Check MONGODB_URI has correct credentials
```

### Token expired

```
Error: "Invalid or expired token"
→ Solution: Login again to get new token

→ Or: Change ACCESS_TOKEN_EXPIRE_MINUTES to increase timeout
```

---

## 📊 Current Status

### ✅ Complete
- Backend API (all 17 endpoints)
- Database schema & indexes
- Authentication & authorization
- JWT token management
- Frontend test login
- Frontend layout & components
- CORS configuration
- API documentation (Swagger UI)

### ⏳ In Progress
- Frontend API integration
- Form validation & error handling
- Case management UI
- Appointment booking UI
- Lawyer search & filtering

### ❌ Not Yet Started
- ML model training (classification)
- Document classification & summarization
- Legal dataset integration
- Email notifications
- Admin dashboard
- Mobile app

---

## 📞 Support

### Quick Help
1. **API Docs**: http://localhost:8000/docs (Swagger UI)
2. **This Guide**: `PROJECT.md` (comprehensive reference)
3. **Code Examples**: Check `backend/app/routers/` for reference implementations

### If Something Breaks
1. Check `.env` file exists and has MONGODB_URI
2. Verify MongoDB is running
3. Check backend starts without errors
4. Look at error messages in terminal
5. Check this troubleshooting section

### Useful Commands

```bash
# Backend logs
tail -f backend.log

# Frontend logs
npm run dev

# Database inspection
mongosh
use jurislink
db.users.find()

# API testing
curl http://localhost:8000/docs
```

---

## 🎯 Next Steps

### This Week
1. [ ] Integrate frontend with API calls
2. [ ] Add form validation
3. [ ] Test end-to-end workflows
4. [ ] Fix any bugs

### Next Week
1. [ ] Build UI forms for all entities
2. [ ] Add error notifications
3. [ ] Performance optimization
4. [ ] Security review

### Future Enhancements
1. [ ] Train ML models
2. [ ] Add AI classification & summarization
3. [ ] Integrate legal datasets
4. [ ] Email notifications
5. [ ] Mobile app
6. [ ] Analytics dashboard

---

## 📄 License

Academic project for legal aid platform.

**Questions?** Check the documentation files or API documentation at `/docs`.

