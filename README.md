# Wine Tracker 🍷

A personal wine tracking application that allows users to catalog wines they've tasted, rate them, and maintain a searchable digital wine journal with photo documentation.

## Features

- 📷 **Photo Capture**: Upload and store wine label photos with automatic orientation correction
- ⭐ **Rating System**: Rate wines from 1 to 5 stars
- 🔍 **Smart Search**: Search by wine name, vineyard, rating, or vintage year
- 📱 **Mobile-First Design**: Optimized for mobile devices with swipe gallery
- 📝 **Tasting Notes**: Add personal notes for each wine
- 🖼️ **Gallery View**: Browse your collection with a TikTok-style swipe interface

## Tech Stack

- **Backend**: Python 3.15+ with Flask
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript
- **Image Processing**: Pillow with HEIC/HEIF support

## Installation

### Prerequisites

- Python 3.15 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/wine-tracker.git
   cd wine-tracker
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python app.py
   # The database will be created automatically on first run
   ```

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and adjust the settings:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///wine_tracker.db

# Server
HOST=0.0.0.0
PORT=3000

# File Uploads
MAX_CONTENT_LENGTH=10485760  # 10MB
UPLOAD_FOLDER=uploads
THUMBNAIL_FOLDER=uploads/thumbnails

# Image Processing
IMAGE_MAX_WIDTH=1200
IMAGE_MAX_HEIGHT=1200
THUMBNAIL_WIDTH=300
THUMBNAIL_HEIGHT=300
IMAGE_QUALITY=85
THUMBNAIL_QUALITY=75
```

## Running the Application

### Development Mode

```bash
python app.py
```

The application will be available at `http://localhost:3000`

### Production Mode

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:3000 "app:create_app()"
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_models.py
```

## API Endpoints

### Main Routes
- `GET /` - Home dashboard
- `GET /wines` - List all wines
- `GET /wines/add` - Add wine form
- `POST /wines/add` - Create new wine
- `GET /wines/<id>` - View wine details
- `GET /wines/<id>/edit` - Edit wine form
- `POST /wines/<id>/edit` - Update wine
- `POST /wines/<id>/delete` - Delete wine
- `GET /gallery` - Swipe gallery view
- `GET /search` - Search page

### API Routes
- `GET /api/search` - Search wines (query params: q, rating, year_from, year_to)
- `GET /api/wines` - Get all wines with pagination
- `GET /api/wines/<id>` - Get single wine
- `GET /api/wines/suggestions` - Get search suggestions
- `GET /api/stats` - Get collection statistics

## Project Structure

```
wine-tracker/
├── app.py                 # Flask application factory
├── config.py              # Configuration settings
├── extensions.py          # Flask extensions initialization
├── models.py              # Database models
├── utils.py               # Utility functions
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── .env.example           # Example environment file
├── routes/
│   ├── main.py           # Main application routes
│   ├── wine.py           # Wine CRUD routes
│   └── api.py            # RESTful API endpoints
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── gallery.html
│   ├── search.html
│   └── wines/
│       ├── add.html
│       ├── edit.html
│       ├── list.html
│       └── view.html
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── main.js
│       └── sw.js
├── uploads/              # Wine images (not in git)
│   └── thumbnails/
└── tests/                # Test suite
    ├── conftest.py
    ├── test_models.py
    ├── test_routes.py
    └── test_utils.py
```

## Features in Detail

### Image Processing
- Automatic EXIF orientation correction
- Image resizing for optimal storage
- Thumbnail generation for list views
- Support for HEIC/HEIF formats from iPhone

### Search & Filter
- Real-time search suggestions
- Filter by rating and vintage year
- Case-insensitive partial matching

### Mobile Experience
- Touch-optimized interface
- Swipe gestures in gallery
- Responsive design (320px - 1200px)
- Camera integration for photo capture

## Security

- CSRF protection on all forms
- Input validation and sanitization
- Secure file upload handling
- SQL injection prevention via ORM

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues and questions, please use the GitHub issue tracker.