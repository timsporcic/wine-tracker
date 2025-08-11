from datetime import datetime, UTC
from extensions import db


class Wine(db.Model):
    __tablename__ = 'wines'
    
    id = db.Column(db.Integer, primary_key=True)
    wine_name = db.Column(db.String(100), nullable=False, index=True)
    vineyard_name = db.Column(db.String(100), nullable=False, index=True)
    vintage_year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text(500))
    image_path = db.Column(db.String(255), nullable=False)
    thumbnail_path = db.Column(db.String(255), nullable=False)
    date_added = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    date_modified = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    def __init__(self, wine_name, vineyard_name, vintage_year, rating, 
                 image_path, thumbnail_path, notes=None):
        self.wine_name = wine_name
        self.vineyard_name = vineyard_name
        self.vintage_year = vintage_year
        self.rating = rating
        self.notes = notes
        self.image_path = image_path
        self.thumbnail_path = thumbnail_path
        self.date_added = datetime.now(UTC)
        self.date_modified = datetime.now(UTC)
    
    def to_dict(self):
        return {
            'id': self.id,
            'wine_name': self.wine_name,
            'vineyard_name': self.vineyard_name,
            'vintage_year': self.vintage_year,
            'rating': self.rating,
            'notes': self.notes,
            'image_path': self.image_path,
            'thumbnail_path': self.thumbnail_path,
            'date_added': self.date_added.isoformat() if self.date_added else None,
            'date_modified': self.date_modified.isoformat() if self.date_modified else None
        }
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['id', 'date_added']:
                setattr(self, key, value)
        self.date_modified = datetime.now(UTC)
    
    def validate(self):
        errors = []
        
        if not self.wine_name or len(self.wine_name) > 100:
            errors.append("Wine name is required and must be 100 characters or less")
        
        if not self.vineyard_name or len(self.vineyard_name) > 100:
            errors.append("Vineyard name is required and must be 100 characters or less")
        
        current_year = datetime.now().year
        if not self.vintage_year or self.vintage_year < 1800 or self.vintage_year > current_year:
            errors.append(f"Vintage year must be between 1800 and {current_year}")
        
        if not self.rating or self.rating < 1 or self.rating > 5:
            errors.append("Rating must be between 1 and 5 stars")
        
        if self.notes and len(self.notes) > 500:
            errors.append("Notes must be 500 characters or less")
        
        if not self.image_path:
            errors.append("Image path is required")
        
        if not self.thumbnail_path:
            errors.append("Thumbnail path is required")
        
        return errors
    
    def __repr__(self):
        return f'<Wine {self.wine_name} - {self.vineyard_name} ({self.vintage_year})>'