"""
Production configuration for Flask application
"""

import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-secret-key-in-production'
    DEBUG = False
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Add production-specific settings here
    # Database URLs, Redis, etc.

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

# Select configuration based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}

