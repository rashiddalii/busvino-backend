# Bus Tracking SaaS API

A comprehensive FastAPI-based backend for a bus tracking SaaS application with Auth0 integration and Supabase database.

## 🚀 Features

### ✅ Completed Features
- **User Authentication**: Registration and login with Auth0
- **Role-Based Access Control**: Student, Employee, Driver, Admin roles
- **Admin User Management**: Complete CRUD operations for user management
- **Professional API Structure**: Scalable, modular architecture
- **Vercel Deployment Ready**: Optimized for serverless deployment

### 🚧 In Progress
- Bus Management (Week 2)
- Route Management (Week 3)
- Schedule Management (Week 4)
- Live Tracking (Week 6)

## 🏗️ Architecture

```
fastApi/
├── api/
│   └── index.py              # Main FastAPI application
├── app/
│   ├── config/               # Configuration management
│   │   ├── settings.py       # App settings with pydantic
│   │   └── database.py       # Supabase client configuration
│   ├── core/                 # Core functionality
│   │   ├── auth.py          # Authentication & authorization
│   │   └── database.py      # Database dependencies
│   ├── models/              # Pydantic data models
│   │   ├── user.py          # User models with roles & status
│   │   ├── bus.py           # Bus models (placeholder)
│   │   ├── route.py         # Route models (placeholder)
│   │   └── schedule.py      # Schedule models (placeholder)
│   ├── schemas/             # API request/response schemas
│   │   ├── common.py        # Common response schemas
│   │   └── auth.py          # Auth-specific schemas
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py  # Authentication service
│   │   └── user_service.py  # User management service
│   ├── utils/               # Utility functions
│   │   └── handlers.py      # Exception handlers
│   └── api/v1/              # API version 1
│       ├── auth.py          # Authentication endpoints
│       └── users.py         # User management endpoints
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel deployment config
└── README.md               # This file
```

## 🔧 Setup

### Prerequisites
- Python 3.8+
- Supabase account
- Auth0 account

### Environment Variables
Create a `.env` file:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
AUTH0_DOMAIN=your_auth0_domain
AUTH0_CLIENT_ID=your_auth0_client_id
AUTH0_CLIENT_SECRET=your_auth0_client_secret
```

### Installation
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn api.index:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth0_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    location VARCHAR(200),
    role VARCHAR(20) NOT NULL DEFAULT 'student' 
        CHECK (role IN ('student', 'employee', 'driver', 'admin')),
    status VARCHAR(20) NOT NULL DEFAULT 'active' 
        CHECK (status IN ('active', 'inactive', 'suspended')),
    organization_id VARCHAR(255),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### User Audit Log
```sql
CREATE TABLE user_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    admin_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    field_name VARCHAR(50),
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔐 Authentication

### User Roles
- **Student**: Basic access to view routes and schedules
- **Employee**: Can view and manage schedules
- **Driver**: Can update bus location and trip status
- **Admin**: Full access to all features including user management

### Authentication Flow
1. User registers/logs in via Auth0
2. Auth0 returns JWT token
3. API validates token and fetches user from Supabase
4. Role-based access control applied to endpoints

## 📡 API Endpoints

### Authentication
```
POST /register              # User registration
POST /login                 # User login
GET  /protected             # Protected route example
GET  /api/v1/auth/me       # Get current user
```

### User Management (Admin Only)
```
GET    /api/v1/users/                    # List users with filtering
POST   /api/v1/users/                    # Create new user
GET    /api/v1/users/{user_id}           # Get specific user
PUT    /api/v1/users/{user_id}           # Update user
DELETE /api/v1/users/{user_id}           # Delete user (soft delete)
PATCH  /api/v1/users/{user_id}/role      # Assign role to user
GET    /api/v1/users/roles/available     # Get available roles
GET    /api/v1/users/statuses/available  # Get available statuses
```

### Query Parameters for User Listing
- `role`: Filter by user role (student, employee, driver, admin)
- `status`: Filter by user status (active, inactive, suspended)
- `search`: Search by name or email
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

## 🧪 Testing

### Basic API Tests
```bash
python test_new_api.py
```

### User Management Tests
```bash
python test_user_management.py
```

## 🚀 Deployment

### Vercel Deployment
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Environment Variables for Vercel
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
AUTH0_DOMAIN=your_auth0_domain
AUTH0_CLIENT_ID=your_auth0_client_id
AUTH0_CLIENT_SECRET=your_auth0_client_secret
```

## 📋 API Examples

### Create User (Admin)
```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "name": "New User",
    "phone": "+1234567890",
    "location": "City Name",
    "role": "student",
    "status": "active",
    "password": "SecurePassword123!"
  }'
```

### List Users with Filtering
```bash
curl -X GET "http://localhost:8000/api/v1/users/?role=student&status=active&page=1&per_page=10" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Assign Role
```bash
curl -X PATCH "http://localhost:8000/api/v1/users/USER_ID/role?role=employee" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 🔒 Security Features

- **JWT Token Validation**: All protected endpoints validate Auth0 tokens
- **Role-Based Access Control**: Endpoints restricted by user role
- **Soft Delete**: Users are marked inactive rather than deleted
- **Audit Logging**: All user changes are logged with admin tracking
- **Input Validation**: All inputs validated with Pydantic models

## 📈 Performance Optimizations

- **Lazy Loading**: Supabase client initialized on-demand
- **Database Indexes**: Optimized queries with proper indexing
- **Pagination**: Large datasets handled efficiently
- **Caching**: Ready for Redis integration

## 🛠️ Development

### Adding New Features
1. Create models in `app/models/`
2. Add services in `app/services/`
3. Create API routes in `app/api/v1/`
4. Update database schema
5. Add tests
6. Update documentation

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings
- Write comprehensive tests

## 📞 Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the test files for usage examples
3. Check the database schema for data structure

## 🎯 Roadmap

### Week 1 ✅
- [x] User Registration/Login
- [x] User Management (Admin)

### Week 2 🚧
- [ ] Bus Management
- [ ] Register Buses
- [ ] Assign Drivers & Capacity

### Week 3 📋
- [ ] Route Management
- [ ] Define Routes & Stops
- [ ] Route Details & Schedules

### Week 4 📋
- [ ] Schedule Management
- [ ] User Dashboard

### Week 5 📋
- [ ] Announcements
- [ ] Trip Start/End Toggle

### Week 6 📋
- [ ] Live Bus Tracking
- [ ] ETA Calculations
- [ ] Real-Time Location Sharing

### Week 7 📋
- [ ] Route Guidance
- [ ] Turn-by-turn Navigation

### Week 8 📋
- [ ] Emergency Communication
- [ ] Basic Analytics
- [ ] AI Integration
