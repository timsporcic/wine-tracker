# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Wine Tracker Application - a mobile-first web app for personal wine collection management. The app allows users to catalog wines they've tasted, rate them, and maintain a searchable digital wine journal with photo documentation.

## Technology Stack

- **Backend**: Python 3.15 with Flask
- **Frontend**: HTML5, CSS3, JavaScript (responsive mobile-first design)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Image Processing**: PIL/Pillow
- **File Storage**: Local filesystem or cloud storage (AWS S3)

## Project Structure

```
wine_tracker/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── routes/
│   ├── __init__.py
│   ├── main.py          # Main routes
│   ├── wine.py          # Wine CRUD operations
│   └── api.py           # API endpoints
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
├── uploads/              # Wine label images
└── requirements.txt
```

## Core Features & Architecture

### Wine Entry System
- Photo capture/upload with automatic compression and thumbnail generation
- Star rating system (1-5 stars)
- Required fields: wine name, vineyard, vintage year, rating
- Automatic date tracking for entries

### Search & Discovery
- Text search across wine and vineyard names (case-insensitive, partial matches)
- Vertical swipe gallery interface (TikTok/Instagram Stories style)
- Full-screen photo browsing with overlay information

### Database Schema
```sql
wines_table:
- id (Primary Key)
- wine_name (VARCHAR, NOT NULL)
- vineyard_name (VARCHAR, NOT NULL)
- vintage_year (INTEGER, NOT NULL)
- rating (INTEGER, 1-5, NOT NULL)
- notes (TEXT, OPTIONAL)
- image_path (VARCHAR, NOT NULL)
- thumbnail_path (VARCHAR, NOT NULL)
- date_added (DATETIME, NOT NULL)
- date_modified (DATETIME, NOT NULL)
```

## Development Commands

### Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Development server with debug mode
flask run --debug

# Or if using app.py directly
python app.py
```

### Database Operations
```bash
# Initialize database
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migrations
flask db upgrade
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wine_tracker

# Run specific test file
pytest tests/test_models.py
```

## Key Implementation Notes

### Mobile-First Design Requirements
- Touch targets minimum 44px
- Responsive breakpoints: 320px to 1200px
- Portrait orientation optimized
- Swipe gestures for gallery navigation

### Image Handling
- Support JPEG, PNG, HEIC formats
- Max file size: 10MB
- Auto-generate thumbnails for list views
- Maintain original quality for detail view

### Performance Targets
- Page loads < 2 seconds on mobile
- Image uploads < 10 seconds
- Search results < 1 second
- Handle 100+ wine entries without degradation

### Security Considerations
- Input validation and sanitization on all forms
- Parameterized queries for SQL injection prevention
- File type validation for uploads
- CSRF protection on all forms
- Secure session management

## API Endpoints

- `GET /` - Home dashboard
- `GET /wines` - List all wines
- `POST /wines/add` - Add new wine entry
- `GET /wines/<id>` - Wine detail view
- `PUT /wines/<id>` - Update wine entry
- `DELETE /wines/<id>` - Delete wine entry
- `GET /api/search` - Search wines (query params: q, rating, year)
- `GET /gallery` - Swipe gallery view