
import os  # nuevo


class BaseConfig:
    """Configuración Base"""
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # nuevo


class DevelopmentConfig(BaseConfig):
    """Configuración de deasarrollo """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True  # nuevo
 

class TestingConfig(BaseConfig):
    """Configuración de pruebas """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')  # nuevo


class ProductionConfig(BaseConfig):
    """Configuración para producción """
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # nuevo
