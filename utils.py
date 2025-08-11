import os
import uuid
from PIL import Image, ImageOps
from werkzeug.utils import secure_filename
from flask import current_app
from config import Config
import pillow_heif


pillow_heif.register_heif_opener()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_and_process_image(file):
    if not file or not allowed_file(file.filename):
        return None, None
    
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ['heic', 'heif', 'png']:
        unique_filename = unique_filename.rsplit('.', 1)[0] + '.jpg'
    
    image_path = os.path.join(Config.UPLOAD_FOLDER, unique_filename)
    thumbnail_filename = f"thumb_{unique_filename}"
    thumbnail_path = os.path.join(Config.THUMBNAIL_FOLDER, thumbnail_filename)
    
    try:
        img = Image.open(file.stream)
        
        # Apply EXIF orientation if present
        img = ImageOps.exif_transpose(img)
        
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        img_copy = img.copy()
        img.thumbnail(Config.IMAGE_SIZE, Image.Resampling.LANCZOS)
        img.save(image_path, 'JPEG', quality=Config.IMAGE_QUALITY, optimize=True)
        
        img_copy.thumbnail(Config.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
        img_copy.save(thumbnail_path, 'JPEG', quality=Config.THUMBNAIL_QUALITY, optimize=True)
        
        return f"uploads/{unique_filename}", f"uploads/thumbnails/{thumbnail_filename}"
    
    except Exception as e:
        print(f"Error processing image: {e}")
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        return None, None


def delete_image_files(image_path, thumbnail_path):
    try:
        # Get folders from app config if in app context, otherwise use Config
        if current_app:
            upload_folder = current_app.config.get('UPLOAD_FOLDER', Config.UPLOAD_FOLDER)
            thumbnail_folder = current_app.config.get('THUMBNAIL_FOLDER', Config.THUMBNAIL_FOLDER)
        else:
            upload_folder = Config.UPLOAD_FOLDER
            thumbnail_folder = Config.THUMBNAIL_FOLDER
            
        if image_path:
            # Handle both relative and absolute paths
            if image_path.startswith('uploads/'):
                # Remove 'uploads/' prefix and join with UPLOAD_FOLDER
                filename = image_path.replace('uploads/', '')
                full_path = os.path.join(upload_folder, filename)
            else:
                full_path = image_path
            
            if os.path.exists(full_path):
                os.remove(full_path)
        
        if thumbnail_path:
            # Handle both relative and absolute paths
            if thumbnail_path.startswith('uploads/thumbnails/'):
                # Remove prefix and join with THUMBNAIL_FOLDER
                filename = thumbnail_path.replace('uploads/thumbnails/', '')
                full_path = os.path.join(thumbnail_folder, filename)
            else:
                full_path = thumbnail_path
                
            if os.path.exists(full_path):
                os.remove(full_path)
    except Exception as e:
        print(f"Error deleting image files: {e}")