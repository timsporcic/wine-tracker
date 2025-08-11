import pytest
from datetime import datetime
from models import Wine
from extensions import db


class TestWineModel:
    """Test Wine model functionality."""
    
    def test_wine_creation(self, app, sample_wine_data):
        """Test creating a wine instance."""
        with app.app_context():
            wine = Wine(**sample_wine_data)
            assert wine.wine_name == sample_wine_data['wine_name']
            assert wine.vineyard_name == sample_wine_data['vineyard_name']
            assert wine.vintage_year == sample_wine_data['vintage_year']
            assert wine.rating == sample_wine_data['rating']
            assert wine.notes == sample_wine_data['notes']
            assert wine.image_path == sample_wine_data['image_path']
            assert wine.thumbnail_path == sample_wine_data['thumbnail_path']
            assert isinstance(wine.date_added, datetime)
            assert isinstance(wine.date_modified, datetime)
    
    def test_wine_save_to_db(self, app, sample_wine_data):
        """Test saving a wine to the database."""
        with app.app_context():
            wine = Wine(**sample_wine_data)
            db.session.add(wine)
            db.session.commit()
            
            saved_wine = Wine.query.first()
            assert saved_wine is not None
            assert saved_wine.wine_name == sample_wine_data['wine_name']
            assert saved_wine.id is not None
    
    def test_wine_to_dict(self, app, sample_wine_data):
        """Test converting wine to dictionary."""
        with app.app_context():
            wine = Wine(**sample_wine_data)
            db.session.add(wine)
            db.session.commit()
            
            wine_dict = wine.to_dict()
            assert wine_dict['wine_name'] == sample_wine_data['wine_name']
            assert wine_dict['vineyard_name'] == sample_wine_data['vineyard_name']
            assert wine_dict['vintage_year'] == sample_wine_data['vintage_year']
            assert wine_dict['rating'] == sample_wine_data['rating']
            assert wine_dict['notes'] == sample_wine_data['notes']
            assert wine_dict['id'] is not None
            assert wine_dict['date_added'] is not None
            assert wine_dict['date_modified'] is not None
    
    def test_wine_update(self, app, sample_wine):
        """Test updating wine attributes."""
        with app.app_context():
            wine = Wine.query.first()
            original_modified = wine.date_modified
            
            wine.update(
                wine_name='Updated Wine',
                rating=3,
                notes='Updated notes'
            )
            db.session.commit()
            
            updated_wine = Wine.query.first()
            assert updated_wine.wine_name == 'Updated Wine'
            assert updated_wine.rating == 3
            assert updated_wine.notes == 'Updated notes'
            assert updated_wine.date_modified > original_modified
    
    def test_wine_validate_valid(self, app, sample_wine_data):
        """Test validation with valid data."""
        with app.app_context():
            wine = Wine(**sample_wine_data)
            errors = wine.validate()
            assert len(errors) == 0
    
    def test_wine_validate_missing_name(self, app, sample_wine_data):
        """Test validation with missing wine name."""
        with app.app_context():
            sample_wine_data['wine_name'] = ''
            wine = Wine(**sample_wine_data)
            errors = wine.validate()
            assert len(errors) > 0
            assert any('Wine name is required' in error for error in errors)
    
    def test_wine_validate_long_name(self, app, sample_wine_data):
        """Test validation with wine name too long."""
        with app.app_context():
            sample_wine_data['wine_name'] = 'a' * 101
            wine = Wine(**sample_wine_data)
            errors = wine.validate()
            assert len(errors) > 0
            assert any('100 characters or less' in error for error in errors)
    
    def test_wine_validate_missing_vineyard(self, app, sample_wine_data):
        """Test validation with missing vineyard name."""
        with app.app_context():
            sample_wine_data['vineyard_name'] = ''
            wine = Wine(**sample_wine_data)
            errors = wine.validate()
            assert len(errors) > 0
            assert any('Vineyard name is required' in error for error in errors)
    
    def test_wine_validate_invalid_year(self, app, sample_wine_data):
        """Test validation with invalid vintage year."""
        with app.app_context():
            # Test year too old
            sample_wine_data['vintage_year'] = 1799
            wine = Wine(**sample_wine_data)
            errors = wine.validate()
            assert len(errors) > 0
            assert any('between 1800' in error for error in errors)
            
            # Test future year
            sample_wine_data['vintage_year'] = datetime.now().year + 1
            wine = Wine(**sample_wine_data)
            errors = wine.validate()
            assert len(errors) > 0
            assert any('between 1800' in error for error in errors)
    
    def test_wine_validate_invalid_rating(self, app, sample_wine_data):
        """Test validation with invalid rating."""
        with app.app_context():
            # Test rating too low
            sample_wine_data['rating'] = 0
            wine = Wine(**sample_wine_data)
            errors = wine.validate()
            assert len(errors) > 0
            assert any('between 1 and 5' in error for error in errors)
            
            # Test rating too high
            sample_wine_data['rating'] = 6
            wine = Wine(**sample_wine_data)
            errors = wine.validate()
            assert len(errors) > 0
            assert any('between 1 and 5' in error for error in errors)
    
    def test_wine_validate_long_notes(self, app, sample_wine_data):
        """Test validation with notes too long."""
        with app.app_context():
            sample_wine_data['notes'] = 'a' * 501
            wine = Wine(**sample_wine_data)
            errors = wine.validate()
            assert len(errors) > 0
            assert any('500 characters or less' in error for error in errors)
    
    def test_wine_validate_missing_image_path(self, app, sample_wine_data):
        """Test validation with missing image path."""
        with app.app_context():
            sample_wine_data['image_path'] = ''
            wine = Wine(**sample_wine_data)
            errors = wine.validate()
            assert len(errors) > 0
            assert any('Image path is required' in error for error in errors)
    
    def test_wine_validate_missing_thumbnail_path(self, app, sample_wine_data):
        """Test validation with missing thumbnail path."""
        with app.app_context():
            sample_wine_data['thumbnail_path'] = ''
            wine = Wine(**sample_wine_data)
            errors = wine.validate()
            assert len(errors) > 0
            assert any('Thumbnail path is required' in error for error in errors)
    
    def test_wine_repr(self, app, sample_wine_data):
        """Test wine string representation."""
        with app.app_context():
            wine = Wine(**sample_wine_data)
            repr_str = repr(wine)
            assert 'Château Margaux' in repr_str
            assert 'Margaux Estate' in repr_str
            assert '2018' in repr_str
    
    def test_wine_query_by_name(self, app, multiple_wines):
        """Test querying wines by name."""
        with app.app_context():
            wines = Wine.query.filter(Wine.wine_name.ilike('%oak%')).all()
            assert len(wines) == 1
            assert wines[0].wine_name == 'Silver Oak'
    
    def test_wine_query_by_vineyard(self, app, multiple_wines):
        """Test querying wines by vineyard."""
        with app.app_context():
            wines = Wine.query.filter(Wine.vineyard_name.ilike('%caymus%')).all()
            assert len(wines) == 1
            assert wines[0].vineyard_name == 'Caymus Vineyards'
    
    def test_wine_query_by_rating(self, app, multiple_wines):
        """Test querying wines by rating."""
        with app.app_context():
            wines = Wine.query.filter(Wine.rating == 5).all()
            assert len(wines) == 2
            
            wines = Wine.query.filter(Wine.rating >= 4).all()
            assert len(wines) == 4
    
    def test_wine_query_by_year_range(self, app, multiple_wines):
        """Test querying wines by year range."""
        with app.app_context():
            wines = Wine.query.filter(
                Wine.vintage_year.between(2018, 2020)
            ).all()
            assert len(wines) == 2
    
    def test_wine_order_by_date(self, app, multiple_wines):
        """Test ordering wines by date added."""
        with app.app_context():
            wines = Wine.query.order_by(Wine.date_added.desc()).all()
            assert len(wines) == 5
            # Last added should be first
            assert wines[0].wine_name == 'Cloudy Bay'
    
    def test_wine_pagination(self, app, multiple_wines):
        """Test wine pagination."""
        with app.app_context():
            page1 = Wine.query.paginate(page=1, per_page=3)
            assert len(page1.items) == 3
            assert page1.total == 5
            assert page1.pages == 2
            assert page1.has_next == True
            assert page1.has_prev == False
            
            page2 = Wine.query.paginate(page=2, per_page=3)
            assert len(page2.items) == 2
            assert page2.has_next == False
            assert page2.has_prev == True