import pytest
import tempfile
import os
from app import create_app
from extensions import db
from models import Wine
from datetime import datetime


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def sample_wine_data():
    """Sample wine data for testing."""
    return {
        'wine_name': 'Château Margaux',
        'vineyard_name': 'Margaux Estate',
        'vintage_year': 2018,
        'rating': 5,
        'notes': 'Exceptional vintage with notes of blackcurrant and cedar',
        'image_path': 'uploads/test_image.jpg',
        'thumbnail_path': 'uploads/thumbnails/thumb_test_image.jpg'
    }


@pytest.fixture
def sample_wine(app, sample_wine_data):
    """Create a sample wine in the database."""
    with app.app_context():
        wine = Wine(**sample_wine_data)
        db.session.add(wine)
        db.session.commit()
        db.session.refresh(wine)
        return wine


@pytest.fixture
def multiple_wines(app):
    """Create multiple wines for testing."""
    wines_data = [
        {
            'wine_name': 'Opus One',
            'vineyard_name': 'Opus One Winery',
            'vintage_year': 2019,
            'rating': 5,
            'notes': 'Bold and complex',
            'image_path': 'uploads/opus.jpg',
            'thumbnail_path': 'uploads/thumbnails/thumb_opus.jpg'
        },
        {
            'wine_name': 'Caymus Cabernet',
            'vineyard_name': 'Caymus Vineyards',
            'vintage_year': 2020,
            'rating': 4,
            'notes': 'Rich and smooth',
            'image_path': 'uploads/caymus.jpg',
            'thumbnail_path': 'uploads/thumbnails/thumb_caymus.jpg'
        },
        {
            'wine_name': 'Silver Oak',
            'vineyard_name': 'Silver Oak Cellars',
            'vintage_year': 2017,
            'rating': 4,
            'notes': 'Classic Napa Cab',
            'image_path': 'uploads/silver.jpg',
            'thumbnail_path': 'uploads/thumbnails/thumb_silver.jpg'
        },
        {
            'wine_name': 'Penfolds Grange',
            'vineyard_name': 'Penfolds',
            'vintage_year': 2016,
            'rating': 5,
            'notes': 'Australian icon',
            'image_path': 'uploads/penfolds.jpg',
            'thumbnail_path': 'uploads/thumbnails/thumb_penfolds.jpg'
        },
        {
            'wine_name': 'Cloudy Bay',
            'vineyard_name': 'Cloudy Bay Vineyards',
            'vintage_year': 2021,
            'rating': 3,
            'notes': 'Crisp Sauvignon Blanc',
            'image_path': 'uploads/cloudy.jpg',
            'thumbnail_path': 'uploads/thumbnails/thumb_cloudy.jpg'
        }
    ]
    
    with app.app_context():
        wines = []
        for wine_data in wines_data:
            wine = Wine(**wine_data)
            db.session.add(wine)
            wines.append(wine)
        db.session.commit()
        return wines


@pytest.fixture
def temp_upload_dir(app):
    """Create temporary upload directories for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        upload_dir = os.path.join(tmpdir, 'uploads')
        thumbnail_dir = os.path.join(tmpdir, 'uploads', 'thumbnails')
        os.makedirs(upload_dir)
        os.makedirs(thumbnail_dir)
        
        with app.app_context():
            app.config['UPLOAD_FOLDER'] = upload_dir
            app.config['THUMBNAIL_FOLDER'] = thumbnail_dir
            yield upload_dir


@pytest.fixture
def sample_image_file():
    """Create a sample image file for testing."""
    from PIL import Image
    import io
    
    img = Image.new('RGB', (100, 100), color='red')
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)
    return img_io