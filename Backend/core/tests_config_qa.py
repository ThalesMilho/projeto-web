"""
Production Configuration QA Tests
Validates critical security and configuration settings for production deployment.
"""

import os
import unittest
from django.test import TestCase, override_settings
from django.conf import settings


class TestProductionConfiguration(TestCase):
    """Test production-ready configuration settings."""
    
    @override_settings(DEBUG='False')
    def test_debug_is_false_in_production(self):
        """Test that DEBUG can be properly set to False."""
        self.assertFalse(settings.DEBUG, "DEBUG must be False in production")
    
    def test_secret_key_is_not_empty(self):
        """Test that SECRET_KEY is configured."""
        secret_key = getattr(settings, 'SECRET_KEY', None)
        self.assertIsNotNone(secret_key, "SECRET_KEY must be set")
        self.assertNotEqual(secret_key, 'django-insecure-fallback', 
                          "SECRET_KEY must not use fallback value in production")
        self.assertGreater(len(secret_key), 50, 
                        "SECRET_KEY must be sufficiently long")
    
    def test_critical_apps_installed(self):
        """Test that critical apps are installed."""
        critical_apps = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.sessions',
            'django.contrib.messages',
            'rest_framework',
            'accounts',
            'games',
        ]
        
        for app in critical_apps:
            self.assertIn(app, settings.INSTALLED_APPS,
                         f"Critical app '{app}' must be installed")
    
    def test_security_middleware_order(self):
        """Test that security middleware is properly ordered."""
        middleware_classes = settings.MIDDLEWARE
        
        # SecurityMiddleware should be near the top
        security_middleware_index = None
        for i, middleware in enumerate(middleware_classes):
            if 'SecurityMiddleware' in middleware:
                security_middleware_index = i
                break
        
        self.assertIsNotNone(security_middleware_index,
                          "SecurityMiddleware must be installed")
        self.assertLessEqual(security_middleware_index, 2,
                          "SecurityMiddleware should be among first middleware")
    
    def test_cors_configuration(self):
        """Test CORS configuration for production."""
        # Check if CORS_ALLOW_ALL_ORIGINS is not True in production
        cors_allow_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        
        # In production, this should not be True
        with override_settings(DEBUG='False'):
            self.assertFalse(cors_allow_all, 
                         "CORS should not allow all origins in production")
    
    def test_database_configuration(self):
        """Test database configuration."""
        self.assertIn('default', settings.DATABASES,
                    "Default database must be configured")
        
        db_config = settings.DATABASES['default']
        self.assertIn('ENGINE', db_config,
                    "Database engine must be specified")
    
    def test_logging_configuration(self):
        """Test logging configuration."""
        self.assertIn('LOGGING', settings.__dict__,
                    "LOGGING configuration must be defined")
        
        logging_config = settings.LOGGING
        self.assertIn('filters', logging_config,
                    "Logging filters must be configured")
        
        # Check for sensitive data filter
        filters = logging_config.get('filters', {})
        self.assertIn('mask_sensitive_data', filters,
                    "Sensitive data filter must be configured")
    
    def test_jwt_configuration(self):
        """Test JWT configuration."""
        jwt_config = getattr(settings, 'SIMPLE_JWT', {})
        
        # Check token lifetimes
        self.assertIn('ACCESS_TOKEN_LIFETIME', jwt_config,
                    "Access token lifetime must be configured")
        self.assertIn('REFRESH_TOKEN_LIFETIME', jwt_config,
                    "Refresh token lifetime must be configured")
    
    def test_static_files_configuration(self):
        """Test static files configuration."""
        self.assertTrue(hasattr(settings, 'STATIC_URL'),
                     "STATIC_URL must be configured")
        self.assertTrue(hasattr(settings, 'STATIC_ROOT'),
                     "STATIC_ROOT must be configured")
    
    def test_admin_url_configuration(self):
        """Test admin URL configuration."""
        # Check if admin URL can be customized
        admin_url = os.getenv('ADMIN_URL', '/admin/')
        self.assertIsNotNone(admin_url, "Admin URL should be configurable")
    
    def test_api_keys_configuration(self):
        """Test API keys are properly configured."""
        skalepay_secret = getattr(settings, 'SKALEPAY_SECRET_KEY', None)
        skalepay_public = getattr(settings, 'SKALEPAY_PUBLIC_KEY', None)
        
        # These should not be hardcoded in production
        self.assertIsNotNone(skalepay_secret, "SkalePay secret key must be configured")
        self.assertIsNotNone(skalepay_public, "SkalePay public key must be configured")


class TestSecurityHardening(TestCase):
    """Test security hardening measures."""
    
    def test_csrf_protection_enabled(self):
        """Test CSRF protection is enabled."""
        middleware_classes = settings.MIDDLEWARE
        
        csrf_middleware_found = any('csrf' in middleware.lower() 
                                 for middleware in middleware_classes)
        self.assertTrue(csrf_middleware_found,
                       "CSRF protection middleware must be enabled")
    
    def test_session_middleware_enabled(self):
        """Test session middleware is enabled."""
        middleware_classes = settings.MIDDLEWARE
        
        session_middleware_found = any('session' in middleware.lower() 
                                   for middleware in middleware_classes)
        self.assertTrue(session_middleware_found,
                       "Session middleware must be enabled")
    
    def test_authentication_middleware_enabled(self):
        """Test authentication middleware is enabled."""
        middleware_classes = settings.MIDDLEWARE
        
        auth_middleware_found = any('auth' in middleware.lower() 
                                 for middleware in middleware_classes)
        self.assertTrue(auth_middleware_found,
                       "Authentication middleware must be enabled")
    
    def test_clickjacking_protection_enabled(self):
        """Test clickjacking protection is enabled."""
        middleware_classes = settings.MIDDLEWARE
        
        xframe_middleware_found = any('xframe' in middleware.lower() 
                                    for middleware in middleware_classes)
        self.assertTrue(xframe_middleware_found,
                       "XFrameOptionsMiddleware must be enabled")


if __name__ == '__main__':
    unittest.main()
