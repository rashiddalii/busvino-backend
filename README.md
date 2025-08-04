# Bus Tracking API

A comprehensive FastAPI-based backend for a bus tracking and management system. This API provides endpoints for user management, bus tracking, route management, schedule management, and real-time location updates.

## Features

### User Features
- **User Registration/Login**: Secure authentication with Auth0 integration
- **Live Bus Tracking**: Real-time location updates
- **Estimated Time of Arrival (ETA)**: Calculate arrival times
- **Route Details & Schedules**: View route information and timetables
- **Basic Dashboard**: User's selected route/bus details and announcements

### Admin Features
- **User Management**: Add/remove users, assign roles (student, employee, driver, admin)
- **Bus Management**: Register buses with license plate, capacity, driver assignment
- **Route Management**: Define routes with stops and sequence
- **Schedule Management**: Set departure/arrival times for each route
- **Announcements**: Broadcast delays, holidays, or policy changes
- **Basic Analytics**: Monitor bus punctuality and route adherence

### Driver Features
- **Real-Time Location Sharing**: GPS-enabled location updates
- **Trip Start/End**: Toggle to indicate when trips begin/end
- **Basic Communication**: Emergency button to notify admins
- **Route Guidance**: Turn-by-turn navigation integration

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Supabase**: Backend-as-a-Service with PostgreSQL database
- **Auth0**: Authentication and authorization service
- **JWT**: JSON Web Tokens for secure authentication
- **Pydantic**: Data validation and serialization
- **Python**: Core programming language

## Quick Start

### Prerequisites

1. Python 3.8+
2. Supabase account and project
3. Auth0 account and application

### Environment Setup

Create a `.env` file in the root directory:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Auth0 Configuration
AUTH0_DOMAIN=your_auth0_domain
AUTH0_CLIENT_ID=your_auth0_client_id
AUTH0_CLIENT_SECRET=your_auth0_client_secret
API_AUDIENCE=your_api_audience

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key
```

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd bus-tracking-api
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Supabase database tables (see Database Setup section)

5. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## Database Setup

### Supabase Tables

Create the following tables in your Supabase project:

#### Users Table
```sql
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    auth0_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    location TEXT,
    role TEXT DEFAULT 'student' CHECK (role IN ('student', 'employee', 'driver', 'admin')),
    organization_id TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Buses Table
```sql
CREATE TABLE buses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    license_plate TEXT UNIQUE NOT NULL,
    capacity INTEGER NOT NULL,
    model TEXT,
    year INTEGER,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'maintenance', 'inactive')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Bus Driver Assignments Table
```sql
CREATE TABLE bus_driver_assignments (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    bus_id UUID REFERENCES buses(id) ON DELETE CASCADE,
    driver_id UUID REFERENCES users(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);
```

#### Stops Table
```sql
CREATE TABLE stops (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Routes Table
```sql
CREATE TABLE routes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Route Stops Table
```sql
CREATE TABLE route_stops (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    route_id UUID REFERENCES routes(id) ON DELETE CASCADE,
    stop_id UUID REFERENCES stops(id) ON DELETE CASCADE,
    sequence_order INTEGER NOT NULL,
    estimated_time INTEGER, -- minutes from route start
    UNIQUE(route_id, stop_id)
);
```

#### Schedules Table
```sql
CREATE TABLE schedules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    route_id UUID REFERENCES routes(id) ON DELETE CASCADE,
    bus_id UUID REFERENCES buses(id) ON DELETE CASCADE,
    driver_id UUID REFERENCES users(id) ON DELETE CASCADE,
    departure_time TIMESTAMP WITH TIME ZONE NOT NULL,
    arrival_time TIMESTAMP WITH TIME ZONE NOT NULL,
    days_of_week INTEGER[] NOT NULL, -- 0=Monday, 6=Sunday
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Trips Table
```sql
CREATE TABLE trips (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    schedule_id UUID REFERENCES schedules(id) ON DELETE CASCADE,
    bus_id UUID REFERENCES buses(id) ON DELETE CASCADE,
    driver_id UUID REFERENCES users(id) ON DELETE CASCADE,
    route_id UUID REFERENCES routes(id) ON DELETE CASCADE,
    departure_time TIMESTAMP WITH TIME ZONE NOT NULL,
    estimated_arrival_time TIMESTAMP WITH TIME ZONE NOT NULL,
    actual_departure_time TIMESTAMP WITH TIME ZONE,
    actual_arrival_time TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'in_progress', 'completed', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Bus Locations Table
```sql
CREATE TABLE bus_locations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    bus_id UUID REFERENCES buses(id) ON DELETE CASCADE,
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    speed DOUBLE PRECISION,
    heading DOUBLE PRECISION,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Announcements Table
```sql
CREATE TABLE announcements (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL, -- delay, holiday, policy, general
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### User Favorite Routes Table
```sql
CREATE TABLE user_favorite_routes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    route_id UUID REFERENCES routes(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, route_id)
);
```

## API Documentation

Once the server is running, you can access:

- **Interactive API Documentation**: `http://localhost:8000/docs`
- **Alternative API Documentation**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/register` | Register new user | Public |
| POST | `/login` | User login | Public |
| POST | `/refresh` | Refresh access token | Authenticated |
| GET | `/me` | Get current user info | Authenticated |
| POST | `/logout` | Logout user | Authenticated |

### User Management (`/api/auth/admin`)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/users` | Get all users | Admin |
| GET | `/users/{user_id}` | Get specific user | Admin |
| PUT | `/users/{user_id}` | Update user | Admin |
| DELETE | `/users/{user_id}` | Delete user | Admin |
| PUT | `/users/{user_id}/role` | Update user role | Admin |
| PUT | `/users/{user_id}/toggle-status` | Toggle user status | Admin |

### Bus Management (`/api/buses`)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/` | Get all buses | Authenticated |
| POST | `/` | Create new bus | Admin |
| GET | `/{bus_id}` | Get specific bus | Authenticated |
| PUT | `/{bus_id}` | Update bus | Admin |
| DELETE | `/{bus_id}` | Delete bus | Admin |
| POST | `/{bus_id}/assign-driver` | Assign driver to bus | Admin |
| GET | `/{bus_id}/driver` | Get bus driver | Authenticated |
| PUT | `/{bus_id}/status` | Update bus status | Admin |

### Route Management (`/api/routes`)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/` | Get all routes | Authenticated |
| POST | `/` | Create new route | Admin |
| GET | `/{route_id}` | Get specific route | Authenticated |
| PUT | `/{route_id}` | Update route | Admin |
| DELETE | `/{route_id}` | Delete route | Admin |
| GET | `/{route_id}/details` | Get route details | Authenticated |

### Stop Management (`/api/routes/stops`)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/` | Get all stops | Authenticated |
| POST | `/` | Create new stop | Admin |
| GET | `/{stop_id}` | Get specific stop | Authenticated |
| PUT | `/{stop_id}` | Update stop | Admin |
| DELETE | `/{stop_id}` | Delete stop | Admin |

### Route Stops Management (`/api/routes/{route_id}/stops`)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/` | Get route stops | Authenticated |
| POST | `/` | Add stop to route | Admin |
| PUT | `/{stop_id}` | Update route stop | Admin |
| DELETE | `/{stop_id}` | Remove stop from route | Admin |

### Schedule Management (`/api/schedules`)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/` | Get all schedules | Authenticated |
| POST | `/` | Create new schedule | Admin |
| GET | `/{schedule_id}` | Get specific schedule | Authenticated |
| PUT | `/{schedule_id}` | Update schedule | Admin |
| DELETE | `/{schedule_id}` | Delete schedule | Admin |

### User Dashboard (`/api/schedules/user`)

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/dashboard` | Get user dashboard | Authenticated |
| GET | `/favorite-routes` | Get user's favorite routes | Authenticated |
| POST | `/favorite-routes/{route_id}` | Add route to favorites | Authenticated |
| DELETE | `/favorite-routes/{route_id}` | Remove route from favorites | Authenticated |

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access Control**: Different permissions for different user roles
- **Password Hashing**: Secure password storage with bcrypt
- **CORS Support**: Cross-origin resource sharing configuration
- **Input Validation**: Pydantic models for request/response validation

## Development Guidelines

### Code Structure

```
bus-tracking-api/
├── main.py                 # FastAPI application entry point
├── database.py             # Supabase client configuration
├── auth.py                 # Authentication and authorization logic
├── models.py               # Pydantic models for data validation
├── auth_routes.py          # Authentication and user management routes
├── bus_routes.py           # Bus management routes
├── route_routes.py         # Route and stop management routes
├── schedule_routes.py      # Schedule and dashboard routes
├── supabase_client.py      # Supabase client setup
├── requirements.txt        # Python dependencies
├── test_api.py            # API testing script
└── README.md              # Project documentation
```

### Adding New Features

1. **Create Pydantic models** in `models.py` for request/response validation
2. **Add database operations** using Supabase client in `database.py`
3. **Create route handlers** in appropriate route files
4. **Add authentication/authorization** using dependencies from `auth.py`
5. **Update tests** in `test_api.py`

### Testing

Run the test suite:

```bash
python test_api.py
```

## Deployment

### Environment Variables

Ensure all required environment variables are set in your deployment environment:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `AUTH0_DOMAIN`
- `AUTH0_CLIENT_ID`
- `AUTH0_CLIENT_SECRET`
- `API_AUDIENCE`
- `JWT_SECRET_KEY`

### Production Considerations

1. **Security**: Use strong JWT secrets and secure environment variables
2. **CORS**: Configure CORS properly for your frontend domain
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Logging**: Add comprehensive logging for monitoring
5. **Error Handling**: Implement proper error handling and monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue in the repository.
