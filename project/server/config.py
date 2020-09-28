# project/server/config.py

import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_LOCAL_BASE = os.getenv('POSTGRES_LOCAL_BASE')
DATABASE_NAME = 'flask_jwt_auth'
MNTS_FOR_TOKEN_EXPR = 30


class BaseConfig:
    """Base configuration."""
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'default')


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = POSTGRES_LOCAL_BASE + DATABASE_NAME


class TestingConfig(BaseConfig):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    BCRYPT_LOG_ROUNDS = 4
    SQLALCHEMY_DATABASE_URI = POSTGRES_LOCAL_BASE + DATABASE_NAME + '_test'
    PRESERVE_CONTEXT_ON_EXCEPTION = False


class ProductionConfig(BaseConfig):
    """Production configuration."""
    SECRET_KEY = 'my_precious'
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'postgresql:///example'
