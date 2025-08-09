# User Service API - Quick Reference

## Authentication
```
Authorization: Bearer <token>
X-App-ID: readrocket-web
```

## Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/health` | Health check | No |
| POST | `/user/register` | Register new user | No |
| POST | `/user/login` | User login | No |
| GET | `/user/profile/{user_id}` | Get user profile | Yes |
| PUT | `/user/profile/{user_id}` | Update user profile | Yes |
| GET | `/admin/users/{app_id}` | Get all users for app | No* |

*Admin endpoint - should have admin auth in production

## Valid App IDs

- `readrocket-web`
- `readrocket-mobile`
- `readrocket-admin`
- `aijobpro-web`

**Note**: Configurable via `ALLOWED_APP_IDS` environment variable

## Key Request/Response Examples

### Register User
```bash
POST /user/register
{
  "email": "user@example.com",
  "password": "password123",
  "app_id": "readrocket-web",
  "firstName": "John",      // optional
  "lastName": "Doe",        // optional
  "userName": "johndoe",    // optional
  "avatar": "https://..."   // optional
}

Response: 201
{
  "user_id": "uid123",
  "app_id": "readrocket-web",
  "message": "User registered successfully"
}
```

### Login
```bash
POST /user/login
{
  "email": "user@example.com",
  "password": "password123",
  "app_id": "readrocket-web"
}

Response: 200
{
  "token": "firebase_token",
  "user_id": "uid123",
  "app_id": "readrocket-web"
}
```

### Get Profile
```bash
GET /user/profile/uid123
Headers: 
  Authorization: Bearer <token>
  X-App-ID: readrocket-web

Response: 200
{
  "email": "user@example.com",
  "app_id": "readrocket-web",
  "subscription_status": "free",
  "preferences": { "modification_mode": "suggestion" },
  "firstName": "John",
  "lastName": "Doe",
  "userName": "johndoe"
}
```

### Update Profile
```bash
PUT /user/profile/uid123
Headers: 
  Authorization: Bearer <token>
  X-App-ID: readrocket-web
  Content-Type: application/json

{
  "preferences": {
    "modification_mode": "direct",
    "theme": "dark"
  }
}

Response: 200
{
  "message": "Profile updated successfully"
}
```

## Error Format
All errors return:
```json
{
  "error": "Error message"
}
```

Common status codes: 400 (Bad Request), 401 (Unauthorized), 404 (Not Found)

## Frontend Integration Notes
1. Store token securely after login
2. Include app_id in all requests
3. Handle token expiration (re-authenticate)
4. User multi-tenancy (each app isolated by app_id)
5. Include Authorization header for protected endpoints
