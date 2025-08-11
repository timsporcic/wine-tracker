import pytest
import json
from io import BytesIO
from models import Wine
from extensions import db


class TestMainRoutes:
    """Test main route endpoints."""
    
    def test_index_route(self, client):
        """Test home page route."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Your Personal Wine Journal' in response.data
    
    def test_index_with_wines(self, client, multiple_wines):
        """Test home page with wines in database."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Recently Added' in response.data
        assert b'Total Wines' in response.data
    
    def test_search_page(self, client):
        """Test search page route."""
        response = client.get('/search')
        assert response.status_code == 200
        assert b'Search Wines' in response.data
    
    def test_gallery_page(self, client):
        """Test gallery page route."""
        response = client.get('/gallery')
        assert response.status_code == 200
        assert b'gallery-container' in response.data
    
    def test_gallery_with_wines(self, client, multiple_wines):
        """Test gallery page with wines."""
        response = client.get('/gallery')
        assert response.status_code == 200
        assert b'gallery-slides' in response.data
        assert b'Opus One' in response.data
    
    def test_about_page(self, client):
        """Test about page route."""
        response = client.get('/about')
        assert response.status_code == 200
        assert b'About Wine Tracker' in response.data


class TestWineRoutes:
    """Test wine CRUD routes."""
    
    def test_list_wines_empty(self, client):
        """Test wine list page with no wines."""
        response = client.get('/wines/')
        assert response.status_code == 200
        assert b'No wines in your collection yet' in response.data
    
    def test_list_wines_with_data(self, client, multiple_wines):
        """Test wine list page with wines."""
        response = client.get('/wines/')
        assert response.status_code == 200
        assert b'My Wine Collection' in response.data
        assert b'Opus One' in response.data
    
    def test_add_wine_get(self, client):
        """Test add wine form page."""
        response = client.get('/wines/add')
        assert response.status_code == 200
        assert b'Add New Wine' in response.data
        assert b'Wine Name*' in response.data
    
    def test_add_wine_post_no_image(self, client):
        """Test adding wine without image."""
        data = {
            'wine_name': 'Test Wine',
            'vineyard_name': 'Test Vineyard',
            'vintage_year': 2020,
            'rating': 4,
            'notes': 'Test notes'
        }
        response = client.post('/wines/add', data=data, follow_redirects=True)
        assert b'No image file provided' in response.data
    
    def test_view_wine(self, client, sample_wine):
        """Test viewing a specific wine."""
        response = client.get(f'/wines/{sample_wine.id}')
        assert response.status_code == 200
        assert 'Château Margaux'.encode('utf-8') in response.data
        assert b'Margaux Estate' in response.data
    
    def test_view_wine_not_found(self, client):
        """Test viewing non-existent wine."""
        response = client.get('/wines/999')
        assert response.status_code == 404
    
    def test_edit_wine_get(self, client, sample_wine):
        """Test edit wine form page."""
        response = client.get(f'/wines/{sample_wine.id}/edit')
        assert response.status_code == 200
        assert b'Edit Wine' in response.data
        assert 'Château Margaux'.encode('utf-8') in response.data
    
    def test_edit_wine_post(self, client, sample_wine):
        """Test editing wine details."""
        data = {
            'wine_name': 'Updated Wine',
            'vineyard_name': 'Updated Vineyard',
            'vintage_year': 2019,
            'rating': 3,
            'notes': 'Updated notes'
        }
        response = client.post(f'/wines/{sample_wine.id}/edit', 
                              data=data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Updated Wine' in response.data
    
    def test_delete_wine(self, client, sample_wine):
        """Test deleting a wine."""
        response = client.post(f'/wines/{sample_wine.id}/delete', 
                              follow_redirects=True)
        assert response.status_code == 200
        
        # Verify wine is deleted
        with client.application.app_context():
            wine = Wine.query.get(sample_wine.id)
            assert wine is None


class TestAPIRoutes:
    """Test API endpoints."""
    
    def test_api_search_empty(self, client):
        """Test search API with no results."""
        response = client.get('/api/search?q=nonexistent')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 0
        assert len(data['wines']) == 0
    
    def test_api_search_by_name(self, client, multiple_wines):
        """Test search API by wine name."""
        response = client.get('/api/search?q=opus')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 1
        assert data['wines'][0]['wine_name'] == 'Opus One'
    
    def test_api_search_by_vineyard(self, client, multiple_wines):
        """Test search API by vineyard name."""
        response = client.get('/api/search?q=caymus')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 1
        assert data['wines'][0]['vineyard_name'] == 'Caymus Vineyards'
    
    def test_api_search_with_rating_filter(self, client, multiple_wines):
        """Test search API with rating filter."""
        response = client.get('/api/search?rating=5')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 2
    
    def test_api_search_with_year_filter(self, client, multiple_wines):
        """Test search API with year filter."""
        response = client.get('/api/search?year_from=2019&year_to=2020')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 2
    
    def test_api_search_pagination(self, client, multiple_wines):
        """Test search API pagination."""
        response = client.get('/api/search?per_page=2&page=1')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['wines']) == 2
        assert data['pages'] == 3
    
    def test_api_get_wine(self, client, sample_wine):
        """Test get single wine API."""
        response = client.get(f'/api/wines/{sample_wine.id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['wine_name'] == 'Château Margaux'
        assert data['id'] == sample_wine.id
    
    def test_api_get_wine_not_found(self, client):
        """Test get non-existent wine API."""
        response = client.get('/api/wines/999')
        assert response.status_code == 404
    
    def test_api_get_wines_list(self, client, multiple_wines):
        """Test get wines list API."""
        response = client.get('/api/wines')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total'] == 5
        assert len(data['wines']) == 5
    
    def test_api_get_wines_sorted(self, client, multiple_wines):
        """Test get wines list with sorting."""
        response = client.get('/api/wines?sort_by=wine_name&order=asc')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['wines'][0]['wine_name'] == 'Caymus Cabernet'
    
    def test_api_suggestions_empty(self, client):
        """Test suggestions API with no query."""
        response = client.get('/api/wines/suggestions')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['suggestions']) == 0
    
    def test_api_suggestions_with_query(self, client, multiple_wines):
        """Test suggestions API with query."""
        response = client.get('/api/wines/suggestions?q=ca')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['suggestions']) > 0
        
        # Check for wine and vineyard suggestions
        wine_suggestions = [s for s in data['suggestions'] if s['type'] == 'wine']
        vineyard_suggestions = [s for s in data['suggestions'] if s['type'] == 'vineyard']
        assert len(wine_suggestions) > 0 or len(vineyard_suggestions) > 0
    
    def test_api_stats_empty(self, client):
        """Test stats API with no wines."""
        response = client.get('/api/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_wines'] == 0
        assert data['average_rating'] == 0
    
    def test_api_stats_with_wines(self, client, multiple_wines):
        """Test stats API with wines."""
        response = client.get('/api/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['total_wines'] == 5
        assert data['average_rating'] > 0
        assert '5' in data['rating_distribution']
        assert len(data['wines_by_year']) > 0
        assert len(data['top_vineyards']) > 0


class TestErrorHandling:
    """Test error handling."""
    
    def test_404_error(self, client):
        """Test 404 error page."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_invalid_wine_data(self, client):
        """Test submitting invalid wine data."""
        data = {
            'wine_name': '',  # Empty name
            'vineyard_name': 'Test',
            'vintage_year': 1700,  # Invalid year
            'rating': 10,  # Invalid rating
        }
        response = client.post('/wines/add', data=data, follow_redirects=True)
        assert response.status_code == 200
        # Should stay on add page with errors