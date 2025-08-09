# User Service Project Structure

```
user-service/
├── app.py                     # Main Flask application
├── auth_simple.py             # Authentication logic
├── auth_utils.py              # Password validation utilities  
├── auth.py                    # Alternative auth module
├── firebase_init.py           # Firebase initialization
├── logging_config.py          # Logging configuration
├── models.py                  # Data models
├── deploy.sh                  # Deployment script
├── rrkt-firebase-adminsdk.json # Firebase service account key
│
├── config/                    # Configuration files
│   ├── .env                   # Local environment variables
│   ├── .env.example           # Environment template
│   ├── .env.yaml              # Cloud Run environment config
│   ├── .dockerignore          # Docker ignore rules
│   ├── dockerfile             # Container configuration
│   └── requirements.txt       # Python dependencies
│
├── docs/                      # Documentation
│   ├── API_DOCUMENTATION.md   # Complete API documentation
│   ├── API_QUICK_REFERENCE.md # Quick reference guide
│   ├── CLOUD_RUN_SETUP.md     # Deployment guide
│   └── CONFIGURATION.md       # Configuration guide
│
├── tests/                     # Test files
│   ├── test_api.py            # API endpoint tests
│   ├── test_auth_fixes.py     # Authentication tests
│   ├── test_deployment.py     # Deployment tests
│   ├── test_endpoints.py      # Endpoint tests
│   ├── test_local.py          # Local testing
│   ├── test_login_flow.py     # Login flow tests
│   └── test_simple.py         # Simple tests
│
└── logs/                      # Generated logs (local only)
    └── user-service.log       # Application logs
```

## Key Features

### 🔐 Authentication
- Multi-tenant support with app_id validation
- Password verification via Firebase Auth REST API
- Comprehensive security logging
- Token-based authentication

### 📊 Logging & Monitoring
- Structured logging with performance metrics
- Security event tracking
- Request/response logging
- Error handling and debugging

### 🚀 Deployment
- Single deployment script (`deploy.sh`)
- Automatic service account permission setup
- Environment variable configuration
- Health checks and validation

### 📚 Documentation
- Complete API documentation
- Setup and configuration guides
- Quick reference for developers

### 🧪 Testing
- Comprehensive test suite
- Authentication flow testing
- API endpoint validation
- Deployment verification

## Quick Start

1. **Setup Environment**:
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your settings
   ```

2. **Local Development**:
   ```bash
   python app.py
   ```

3. **Deploy to Cloud Run**:
   ```bash
   ./deploy.sh
   ```

4. **Run Tests**:
   ```bash
   python tests/test_auth_fixes.py
   ```
