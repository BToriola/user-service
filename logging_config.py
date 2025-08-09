# logging_config.py
import logging
import logging.handlers
import os
import sys
from datetime import datetime, timezone

def setup_logging(app_name="user-service", log_level=None):
    """
    Set up comprehensive logging configuration for the application
    """
    
    # Determine log level
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler (always present)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (only in development or when explicitly enabled)
    if not os.getenv('GOOGLE_CLOUD_PROJECT') or os.getenv('ENABLE_FILE_LOGGING', 'false').lower() == 'true':
        log_file = f"{app_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        print(f"Logging to file: {log_file}")
    
    # Set specific loggers to appropriate levels
    logging.getLogger('werkzeug').setLevel(logging.WARNING)  # Reduce Flask request logs
    logging.getLogger('urllib3').setLevel(logging.WARNING)   # Reduce HTTP library logs
    logging.getLogger('google').setLevel(logging.WARNING)    # Reduce Google client library logs
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {log_level}, App: {app_name}")
    logger.info(f"Environment: {'Cloud' if os.getenv('GOOGLE_CLOUD_PROJECT') else 'Local'}")
    
    return logger

def log_environment_info():
    """Log important environment information for debugging"""
    logger = logging.getLogger(__name__)
    
    env_vars = [
        'GOOGLE_CLOUD_PROJECT',
        'GAE_ENV', 
        'ALLOWED_APP_IDS',
        'FIREBASE_CREDENTIALS_PATH',
        'PORT',
        'LOG_LEVEL'
    ]
    
    logger.info("=== Environment Configuration ===")
    for var in env_vars:
        value = os.getenv(var, 'Not set')
        # Mask sensitive information
        if 'CREDENTIALS' in var or 'KEY' in var:
            value = '[MASKED]' if value != 'Not set' else 'Not set'
        logger.info(f"{var}: {value}")
    logger.info("=== End Environment Configuration ===")

def log_request_context(request, user_id=None, app_id=None):
    """Helper function to log request context consistently"""
    logger = logging.getLogger('request_context')
    
    context = {
        'method': request.method,
        'path': request.path,
        'remote_addr': request.remote_addr,
        'user_agent': str(request.user_agent)[:100],  # Truncate long user agents
        'user_id': user_id,
        'app_id': app_id,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    logger.info(f"Request context: {context}")
    return context

def log_performance_metrics(operation_name, duration_ms, success=True, additional_data=None):
    """Log performance metrics in a structured format"""
    logger = logging.getLogger('performance')
    
    metrics = {
        'operation': operation_name,
        'duration_ms': round(duration_ms, 2),
        'success': success,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    if additional_data:
        metrics.update(additional_data)
    
    log_level = logging.INFO if success else logging.WARNING
    logger.log(log_level, f"Performance: {metrics}")
    
    return metrics

def log_security_event(event_type, user_id=None, app_id=None, details=None, severity='INFO'):
    """Log security-related events"""
    logger = logging.getLogger('security')
    
    event = {
        'event_type': event_type,
        'user_id': user_id,
        'app_id': app_id,
        'severity': severity,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'details': details or {}
    }
    
    log_level = getattr(logging, severity.upper(), logging.INFO)
    logger.log(log_level, f"Security event: {event}")
    
    return event

# Example usage and testing
if __name__ == "__main__":
    # Test the logging configuration
    setup_logging("test-app", "DEBUG")
    log_environment_info()
    
    logger = logging.getLogger(__name__)
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test performance logging
    import time
    start = time.time()
    time.sleep(0.1)
    duration = (time.time() - start) * 1000
    log_performance_metrics("test_operation", duration, True, {"test_data": "value"})
    
    # Test security logging
    log_security_event("login_attempt", "test_user", "test_app", {"ip": "127.0.0.1"}, "INFO")
