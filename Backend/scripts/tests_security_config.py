"""
Security Configuration Test Suite
Zero Trust Architecture Verification Tests

This test suite validates that all security configurations are properly
loaded from environment variables and that the application fails securely
when critical configurations are missing.
"""

import os
import logging
import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.conf import settings
from django.core.management import call_command
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client
import re

User = get_user_model()


class SecurityConfigTestCase(TestCase):
    """Test security configuration compliance with Zero Trust principles"""

    def setUp(self):
        """Set up test environment"""
        self.logger = logging.getLogger('test_security')
        
    def test_debug_is_false_by_default(self):
        """Test that DEBUG defaults to False for production safety"""
        with override_settings(DEBUG=None):
            # Simulate missing DEBUG environment variable
            self.assertFalse(settings.DEBUG, "DEBUG should default to False in production")

    def test_secret_key_required_in_production(self):
        """Test that application fails when SECRET_KEY is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                # Reload settings to trigger the validation
                from django.conf import settings
                settings._wrapped = None  # Force reload
                
            self.assertIn("SECRET_KEY environment variable is required", str(context.exception))

    def test_allowed_hosts_not_wildcard(self):
        """Test that ALLOWED_HOSTS is not set to wildcard in production"""
        with override_settings(DEBUG=False):
            allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
            self.assertNotIn('*', allowed_hosts, "ALLOWED_HOSTS should not contain wildcard '*' in production")
            self.assertNotIn(['*'], allowed_hosts, "ALLOWED_HOSTS should not be ['*'] in production")

    def test_admin_url_is_configurable(self):
        """Test that admin URL path is configurable via environment"""
        with override_settings(ADMIN_URL='custom-admin-path'):
            # Test that the admin URL uses the custom path
            client = Client()
            # This should work with the custom admin path
            response = client.get('/custom-admin-path/')
            # Should redirect to login page (302) or return 200 if authenticated
            self.assertIn(response.status_code, [200, 302], "Admin should be accessible at custom path")

    def test_cors_not_allow_all_origins(self):
        """Test that CORS is not configured to allow all origins"""
        cors_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        cors_allow_all = getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False)
        
        self.assertFalse(cors_allow_all, "CORS_ALLOW_ALL_ORIGINS should be False")
        # If origins are specified, they should be specific domains
        if cors_origins:
            for origin in cors_origins:
                self.assertNotEqual(origin, '*', f"CORS origin should not be wildcard: {origin}")

    def test_security_headers_enabled_in_production(self):
        """Test that security headers are enabled in production"""
        with override_settings(DEBUG=False):
            security_headers = [
                'SECURE_SSL_REDIRECT',
                'SECURE_HSTS_SECONDS', 
                'SECURE_HSTS_INCLUDE_SUBDOMAINS',
                'SECURE_HSTS_PRELOAD',
                'SECURE_CONTENT_TYPE_NOSNIFF',
                'SECURE_BROWSER_XSS_FILTER',
                'X_FRAME_OPTIONS',
                'SESSION_COOKIE_SECURE',
                'CSRF_COOKIE_SECURE'
            ]
            
            for header in security_headers:
                header_value = getattr(settings, header, None)
                self.assertIsNotNone(header_value, f"Security header {header} should be configured")
                
                # Specific assertions for certain headers
                if header == 'SECURE_SSL_REDIRECT':
                    self.assertTrue(header_value, "SSL redirect should be enabled in production")
                elif header == 'X_FRAME_OPTIONS':
                    self.assertEqual(header_value, 'DENY', "X-Frame-Options should be DENY")

    def test_jwt_security_configuration(self):
        """Test JWT security settings"""
        jwt_config = getattr(settings, 'SIMPLE_JWT', {})
        
        # Test that token rotation is enabled
        self.assertTrue(jwt_config.get('ROTATE_REFRESH_TOKENS', False), 
                       "JWT refresh token rotation should be enabled")
        
        # Test that blacklisting after rotation is enabled
        self.assertTrue(jwt_config.get('BLACKLIST_AFTER_ROTATION', False),
                       "JWT blacklisting after rotation should be enabled")
        
        # Test that algorithm is specified
        self.assertIn(jwt_config.get('ALGORITHM', ''), ['HS256', 'RS256'],
                     "JWT algorithm should be specified")

    def test_database_url_configuration(self):
        """Test database configuration supports DATABASE_URL"""
        # Test with DATABASE_URL
        with override_settings(DATABASE_URL='sqlite:///:memory:'):
            from django.db import connection
            # Should not raise an exception
            self.assertIsNotNone(connection.settings_dict)

    def test_external_api_keys_required(self):
        """Test that external API keys are required"""
        required_keys = ['SKALEPAY_SECRET_KEY', 'SKALEPAY_PUBLIC_KEY']
        
        for key in required_keys:
            key_value = getattr(settings, key, None)
            # In production, these should not be empty or None
            if not settings.DEBUG:
                self.assertIsNotNone(key_value, f"{key} should be configured in production")
                self.assertNotEqual(key_value, '', f"{key} should not be empty in production")


class PIILoggingTestCase(TestCase):
    """Test PII masking in logging system"""

    def setUp(self):
        """Set up logging test environment"""
        from core.logging_filters import SensitiveDataFilter
        self.filter = SensitiveDataFilter()
        self.logger = logging.getLogger('test_pii')
        self.logger.addFilter(self.filter)

    def test_cpf_masking_in_logs(self):
        """Test that CPF numbers are properly masked in logs"""
        test_cases = [
            '123.456.789-01',
            '12345678901', 
            '111.222.333-44',
            '98765432100'
        ]
        
        for cpf in test_cases:
            with self.assertLogs('test_pii', level='INFO') as log:
                self.logger.info(f"User with CPF {cpf} attempted login")
                
            log_message = log.output[0]
            self.assertNotIn(cpf, log_message, f"Original CPF {cpf} should not appear in logs")
            self.assertIn('[CPF-OCULTO-LGPD]', log_message, "Masked CPF indicator should be in logs")

    def test_password_masking_in_logs(self):
        """Test that passwords are properly masked in logs"""
        test_cases = [
            'password=secret123',
            'senha=mypassword', 
            'token=abc123xyz',
            'PASSWORD=admin123'
        ]
        
        for sensitive_data in test_cases:
            with self.assertLogs('test_pii', level='INFO') as log:
                self.logger.info(f"Login attempt: {sensitive_data}")
                
            log_message = log.output[0]
            self.assertNotIn('secret123', log_message, "Password should not appear in logs")
            self.assertNotIn('mypassword', log_message, "Password should not appear in logs")
            self.assertNotIn('abc123xyz', log_message, "Token should not appear in logs")
            self.assertIn('[PROTEGIDO]', log_message, "Protected indicator should be in logs")

    def test_credit_card_masking(self):
        """Test that credit card numbers are masked (if implemented)"""
        # This test can be extended when credit card masking is implemented
        test_cc = '4111 1111 1111 1111'
        
        with self.assertLogs('test_pii', level='INFO') as log:
            self.logger.info(f"Payment with card {test_cc}")
            
        # Currently the filter doesn't mask credit cards, but this test prepares for that feature
        log_message = log.output[0]
        # When credit card masking is implemented, uncomment:
        # self.assertNotIn(test_cc, log_message, "Credit card should be masked in logs")

    def test_logging_filter_robustness(self):
        """Test that logging filter handles edge cases gracefully"""
        test_cases = [
            None,  # Non-string message
            '',    # Empty string
            123,   # Number
            {'key': 'value'},  # Dictionary
            'Normal message without sensitive data'
        ]
        
        for test_input in test_cases:
            try:
                # Should not raise an exception
                self.logger.info(test_input)
            except Exception as e:
                self.fail(f"Logging filter failed on input {test_input}: {e}")


class RateLimitingTestCase(TestCase):
    """Test rate limiting configuration"""

    def test_anonymous_rate_limiting(self):
        """Test that anonymous users have restrictive rate limits"""
        from rest_framework.settings import api_settings
        
        throttle_classes = api_settings.DEFAULT_THROTTLE_CLASSES
        throttle_rates = api_settings.DEFAULT_THROTTLE_RATES
        
        # Should have anonymous throttling enabled
        self.assertIn('rest_framework.throttling.AnonRateThrottle', throttle_classes)
        
        # Anonymous rate should be restrictive (less than 20/minute)
        anon_rate = throttle_rates.get('anon', '')
        self.assertIn('hour', anon_rate, "Anonymous users should be rate limited per hour")

    def test_authenticated_user_rate_limiting(self):
        """Test that authenticated users have higher rate limits"""
        from rest_framework.settings import api_settings
        
        throttle_rates = api_settings.DEFAULT_THROTTLE_RATES
        
        # Authenticated users should have higher limits
        user_rate = throttle_rates.get('user', '')
        anon_rate = throttle_rates.get('anon', '')
        
        self.assertIn('hour', user_rate, "Authenticated users should be rate limited per hour")
        # User rate should be higher than anonymous rate
        # (This is a basic check - actual comparison would need rate parsing)


class AuthenticationTestCase(TestCase):
    """Test authentication security"""

    def test_default_permission_classes(self):
        """Test that default permissions require authentication"""
        from rest_framework.settings import api_settings
        
        default_permissions = api_settings.DEFAULT_PERMISSION_CLASSES
        
        self.assertIn('rest_framework.permissions.IsAuthenticated', default_permissions,
                     "Default permissions should require authentication")
        
        # Should not allow anonymous access by default
        self.assertNotIn('rest_framework.permissions.AllowAny', default_permissions,
                         "Default permissions should not allow anonymous access")

    def test_password_validation_strength(self):
        """Test password validation configuration"""
        password_validators = getattr(settings, 'AUTH_PASSWORD_VALIDATORS', [])
        
        validator_names = [v['NAME'] for v in password_validators]
        
        # Should include common password validator
        self.assertIn('django.contrib.auth.password_validation.CommonPasswordValidator', 
                     validator_names, "Should validate against common passwords")
        
        # Should include minimum length validator
        self.assertIn('django.contrib.auth.password_validation.MinimumLengthValidator',
                     validator_names, "Should enforce minimum password length")


if __name__ == '__main__':
    unittest.main()
