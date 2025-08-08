# User Service API Documentation

## Base URL
- **Development**: `http://localhost:8080`
- **Production**: `https://your-cloud-run-service-url.com`

## Authentication
Most endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <token>
```

Some endpoints also require an `app_id` parameter to support multi-tenancy.

---

## Endpoints

### 1. Health Check
**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "userservice"
}
```

---

### 2. User Registration
**POST** `/user/register`

Register a new user with optional profile information.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "app_id": "readrocket-web",
  "firstName": "John",          // Optional
  "lastName": "Doe",            // Optional
  "userName": "johndoe",        // Optional
  "avatar": "https://..."       // Optional
}
```

**Success Response (201):**
```json
{
  "user_id": "firebase_user_uid",
  "app_id": "readrocket-web",
  "message": "User registered successfully with complete profile"
}
```

**Error Response (400):**
```json
{
  "error": "Error message describing what went wrong"
}
```

---

### 3. User Login
**POST** `/user/login`

Authenticate a user and get an access token.

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "app_id": "readrocket-web"
}
```

**Success Response (200):**
```json
{
  "token": "firebase_custom_token",
  "user_id": "firebase_user_uid",
  "app_id": "readrocket-web"
}
```

**Error Response (400):**
```json
{
  "error": "Authentication failed: User not found"
}
```

---

### 4. Get User Profile
**GET** `/user/profile/{user_id}`

Retrieve user profile information.

**Headers:**
```
Authorization: Bearer <token>
X-App-ID: readrocket-web
```

**URL Parameters:**
- `user_id` (string): The Firebase user ID

**Query Parameters (Alternative):**
- `app_id` (string): Application ID if not provided in header

**Success Response (200):**
```json
{
  "email": "user@example.com",
  "app_id": "readrocket-web",
  "subscription_status": "free",
  "preferences": {
    "modification_mode": "suggestion"
  },
  "firstName": "John",
  "lastName": "Doe",
  "userName": "johndoe",
  "avatar": "https://...",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

**Error Response (401):**
```json
{
  "error": "Missing or invalid token"
}
```

**Error Response (400):**
```json
{
  "error": "app_id is required"
}
```

---

### 5. Update User Profile
**PUT** `/user/profile/{user_id}`

Update user preferences and profile information.

**Headers:**
```
Authorization: Bearer <token>
X-App-ID: readrocket-web
Content-Type: application/json
```

**URL Parameters:**
- `user_id` (string): The Firebase user ID

**Request Body:**
```json
{
  "preferences": {
    "modification_mode": "direct",
    "theme": "dark",
    "notifications": true
  }
}
```

**Success Response (200):**
```json
{
  "message": "Profile updated successfully"
}
```

**Error Response (401):**
```json
{
  "error": "Missing or invalid token"
}
```

**Error Response (400):**
```json
{
  "error": "Failed to update profile: User not authorized for this application"
}
```

---

### 6. Get Users by App (Admin)
**GET** `/admin/users/{app_id}`

Retrieve all users for a specific application (Admin endpoint).

**URL Parameters:**
- `app_id` (string): Application ID

**Success Response (200):**
```json
{
  "app_id": "readrocket-web",
  "users": [
    {
      "uid": "firebase_user_uid_1",
      "email": "user1@example.com",
      "app_id": "readrocket-web",
      "subscription_status": "free",
      "preferences": {
        "modification_mode": "suggestion"
      },
      "firstName": "John",
      "lastName": "Doe",
      "userName": "johndoe",
      "avatar": "https://...",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "count": 1
}
```

**Error Response (400):**
```json
{
  "error": "Invalid app_id: unknown-app"
}
```

---

## App IDs
The following app IDs are supported:
- `readrocket-web`
- `readrocket-mobile`
- `readrocket-admin`
- `your-other-app`

---

## Error Handling

All endpoints return consistent error responses with appropriate HTTP status codes:

- **400 Bad Request**: Invalid input, missing required fields, or business logic errors
- **401 Unauthorized**: Missing, invalid, or expired authentication token
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server-side errors

Error response format:
```json
{
  "error": "Descriptive error message"
}
```

---

## Rate Limiting
Currently no rate limiting is implemented, but consider implementing it for production use.

---

## CORS
The service should be configured to allow requests from your frontend domains.

---

## Example Usage

### JavaScript/TypeScript Example
```javascript
// Registration
const registerUser = async (userData) => {
  const response = await fetch('/user/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email: userData.email,
      password: userData.password,
      app_id: 'readrocket-web',
      firstName: userData.firstName,
      lastName: userData.lastName
    })
  });
  
  return response.json();
};

// Login
const loginUser = async (email, password) => {
  const response = await fetch('/user/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
      app_id: 'readrocket-web'
    })
  });
  
  return response.json();
};

// Get Profile
const getUserProfile = async (userId, token) => {
  const response = await fetch(`/user/profile/${userId}`, {
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-App-ID': 'readrocket-web'
    }
  });
  
  return response.json();
};

// Update Profile
const updateUserProfile = async (userId, token, preferences) => {
  const response = await fetch(`/user/profile/${userId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'X-App-ID': 'readrocket-web',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ preferences })
  });
  
  return response.json();
};
```

---

## Notes for Frontend Team

1. **Token Management**: Store the token securely (e.g., in httpOnly cookies or secure localStorage)
2. **App ID**: Always include the correct app_id for your application
3. **Error Handling**: Always check response status codes and handle errors appropriately
4. **User ID**: The user_id returned from registration/login should be stored for profile operations
5. **Token Expiration**: Implement token refresh logic or re-authentication when tokens expire
6. **Multi-tenancy**: Each app (web, mobile, admin) is isolated by app_id
