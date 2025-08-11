import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 
        'sqlite:///' + os.path.join(basedir, 'wine_tracker.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(basedir, os.environ.get('UPLOAD_FOLDER', 'uploads'))
    THUMBNAIL_FOLDER = os.path.join(basedir, os.environ.get('THUMBNAIL_FOLDER', 'uploads/thumbnails'))
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 10 * 1024 * 1024))  # Default 10MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic', 'heif'}
    
    # Image Processing Configuration
    IMAGE_MAX_WIDTH = int(os.environ.get('IMAGE_MAX_WIDTH', 1200))
    IMAGE_MAX_HEIGHT = int(os.environ.get('IMAGE_MAX_HEIGHT', 1200))
    THUMBNAIL_WIDTH = int(os.environ.get('THUMBNAIL_WIDTH', 300))
    THUMBNAIL_HEIGHT = int(os.environ.get('THUMBNAIL_HEIGHT', 300))
    IMAGE_QUALITY = int(os.environ.get('IMAGE_QUALITY', 85))
    THUMBNAIL_QUALITY = int(os.environ.get('THUMBNAIL_QUALITY', 75))
    
    # Computed properties
    THUMBNAIL_SIZE = (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT)
    IMAGE_SIZE = (IMAGE_MAX_WIDTH, IMAGE_MAX_HEIGHT)
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(
        days=int(os.environ.get('PERMANENT_SESSION_LIFETIME_DAYS', 7))
    )
    
    # CSRF Configuration
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = None
    
    # Pagination
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', 20))
    
    @staticmethod
    def init_app(app):
        # Create upload directories if they don't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    UPLOAD_FOLDER = os.path.join(basedir, 'test_uploads')
    THUMBNAIL_FOLDER = os.path.join(basedir, 'test_uploads', 'thumbnails')


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/wine_tracker'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}