# Authentication System Documentation

## Overview

AutoDealGenie uses a JWT (JSON Web Token) based authentication system with HTTP-only cookies for secure token storage. The system includes:

- User signup and login
- JWT access and refresh tokens
- HTTP-only cookies for frontend-backend communication
- Protected API endpoints
- React context for auth state management

## Architecture

### Backend (FastAPI)

**Key Components:**

1. **Security Module** (`backend/app/core/security.py`)
   - Password hashing with bcrypt
   - JWT token generation and validation
   - Access tokens (30 minutes expiry)
   - Refresh tokens (7 days expiry)

2. **Authentication Endpoints** (`backend/app/api/v1/endpoints/auth.py`)
   - `POST /api/v1/auth/signup` - Create new user account
   - `POST /api/v1/auth/login` - Login and receive tokens
   - `POST /api/v1/auth/refresh` - Refresh access token
   - `POST /api/v1/auth/logout` - Logout and clear cookies
   - `GET /api/v1/auth/me` - Get current user info

3. **Dependencies** (`backend/app/api/dependencies.py`)
   - `get_current_user` - Extract and validate user from cookie
   - `get_current_active_superuser` - Check for superuser permissions

4. **User Repository** (`backend/app/repositories/user_repository.py`)
   - Database operations for user management
   - User authentication logic

### Frontend (Next.js)

**Key Components:**

1. **AuthProvider** (`frontend/lib/auth/AuthProvider.tsx`)
   - React context for authentication state
   - User state management
   - Login, signup, logout functions
   - Automatic authentication check on mount

2. **useAuth Hook** (`frontend/lib/auth/index.ts`)
   - Easy access to auth context
   - Type-safe authentication operations

3. **API Client** (`frontend/lib/api.ts`)
   - Automatic cookie inclusion
   - Centralized API communication

## Usage

### Backend: Protecting Endpoints

To protect an endpoint, add the `get_current_user` dependency:

```python
from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.models.models import User

router = APIRouter()

@router.get("/protected")
def protected_endpoint(current_user: User = Depends(get_current_user)):
    """This endpoint requires authentication"""
    return {"message": f"Hello {current_user.username}!"}
```

For superuser-only endpoints:

```python
from app.api.dependencies import get_current_active_superuser

@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser)
):
    """Only superusers can delete users"""
    # Delete user logic
    pass
```

### Frontend: Using Authentication

#### 1. Wrap Your App with AuthProvider

The `AuthProvider` is already integrated in `frontend/app/layout.tsx`:

```tsx
import { AuthProvider } from '@/lib/auth';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

#### 2. Use the useAuth Hook

```tsx
'use client';

import { useAuth } from '@/lib/auth';

export default function ProfilePage() {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <h1>Welcome, {user.username}!</h1>
      <p>Email: {user.email}</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

#### 3. Login Form Example

```tsx
'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      router.push('/dashboard');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      {error && <p>{error}</p>}
      <button type="submit">Login</button>
    </form>
  );
}
```

#### 4. Signup Form Example

```tsx
'use client';

import { useState } from 'react';
import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';

export default function SignupPage() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const { signup } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await signup(email, username, password, fullName);
      router.push('/dashboard');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <input
        type="text"
        value={fullName}
        onChange={(e) => setFullName(e.target.value)}
        placeholder="Full Name (optional)"
      />
      {error && <p>{error}</p>}
      <button type="submit">Sign Up</button>
    </form>
  );
}
```

#### 5. Protected Route Component

```tsx
'use client';

import { useAuth } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
```

## API Endpoints

### Authentication Endpoints

#### POST /api/v1/auth/signup

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

#### POST /api/v1/auth/login

Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Cookies Set:**
- `access_token` (HttpOnly, 30 minutes)
- `refresh_token` (HttpOnly, 7 days)

#### POST /api/v1/auth/refresh

Refresh the access token using a refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/logout

Logout and clear authentication cookies.

**Response (200 OK):**
```json
{
  "message": "Successfully logged out"
}
```

#### GET /api/v1/auth/me

Get current authenticated user information.

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

## Security Features

1. **Password Hashing**: Passwords are hashed using bcrypt before storage
2. **HTTP-only Cookies**: Tokens stored in HTTP-only cookies prevent XSS attacks
3. **JWT Tokens**: Stateless authentication with expiration times
4. **Token Types**: Separate access and refresh tokens for added security
5. **CORS Protection**: Configured CORS middleware in backend
6. **Secure Cookie Options**: SameSite=Lax and Secure flags in production

## Environment Variables

### Backend (.env)

```env
SECRET_KEY=your-secret-key-min-32-characters-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Testing

Run the authentication tests:

```bash
cd backend
pytest tests/test_auth.py -v
```

## Troubleshooting

### "Not authenticated" error

- Ensure cookies are being sent with requests (`credentials: 'include'`)
- Check that `NEXT_PUBLIC_API_URL` matches your backend URL
- Verify the access token hasn't expired (check cookie expiration)

### CORS errors

- Ensure frontend URL is in `BACKEND_CORS_ORIGINS` in backend settings
- Check that `credentials: 'include'` is set in fetch requests

### Token validation errors

- Verify `SECRET_KEY` is set in backend environment
- Ensure clock synchronization between frontend and backend servers

## Migration from Firebase

This system replaces Firebase Authentication with a self-hosted JWT solution:

**Before (Firebase):**
```tsx
import { getAuth, signInWithEmailAndPassword } from 'firebase/auth';

const auth = getAuth();
await signInWithEmailAndPassword(auth, email, password);
```

**After (JWT):**
```tsx
import { useAuth } from '@/lib/auth';

const { login } = useAuth();
await login(email, password);
```

## Best Practices

1. **Always use HTTPS in production** to secure cookie transmission
2. **Set strong SECRET_KEY** (32+ characters, random)
3. **Implement refresh token rotation** for enhanced security
4. **Add rate limiting** to authentication endpoints
5. **Use middleware** for consistent authentication checks
6. **Log authentication events** for security monitoring
7. **Implement password reset** functionality
8. **Add email verification** for new accounts

## Future Enhancements

- [ ] Implement password reset functionality
- [ ] Add email verification
- [ ] Implement OAuth providers (Google, GitHub)
- [ ] Add two-factor authentication (2FA)
- [ ] Implement refresh token rotation
- [ ] Add rate limiting to auth endpoints
- [ ] Session management dashboard
- [ ] Login history tracking
