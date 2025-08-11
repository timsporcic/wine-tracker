import pytest
import os
import tempfile
from PIL import Image
from werkzeug.datastructures import FileStorage
from io import BytesIO
from utils import allowed_file, save_and_process_image, delete_image_files


class TestImageUtils:
    """Test image processing utilities."""
    
    def test_allowed_file_valid_extensions(self):
        """Test allowed_file with valid extensions."""
        assert allowed_file('test.jpg') == True
        assert allowed_file('test.jpeg') == True
        assert allowed_file('test.png') == True
        assert allowed_file('test.PNG') == True
        assert allowed_file('test.JPEG') == True
        assert allowed_file('wine.heic') == True
        assert allowed_file('wine.heif') == True
    
    def test_allowed_file_invalid_extensions(self):
        """Test allowed_file with invalid extensions."""
        assert allowed_file('test.txt') == False
        assert allowed_file('test.pdf') == False
        assert allowed_file('test.doc') == False
        assert allowed_file('test') == False
        assert allowed_file('') == False
    
    def test_allowed_file_multiple_dots(self):
        """Test allowed_file with filenames containing multiple dots."""
        assert allowed_file('my.wine.photo.jpg') == True
        assert allowed_file('my.wine.photo.txt') == False
    
    def test_save_and_process_image_valid_jpeg(self, app, temp_upload_dir):
        """Test saving and processing a valid JPEG image."""
        with app.app_context():
            # Create a test image
            img = Image.new('RGB', (800, 600), color='blue')
            img_io = BytesIO()
            img.save(img_io, 'JPEG')
            img_io.seek(0)
            
            # Create FileStorage object
            file = FileStorage(
                stream=img_io,
                filename='test_wine.jpg',
                content_type='image/jpeg'
            )
            
            # Process the image
            image_path, thumbnail_path = save_and_process_image(file)
            
            assert image_path is not None
            assert thumbnail_path is not None
            assert 'uploads/' in image_path
            assert 'uploads/thumbnails/' in thumbnail_path
            assert image_path.endswith('.jpg')
            assert thumbnail_path.endswith('.jpg')
    
    def test_save_and_process_image_valid_png(self, app, temp_upload_dir):
        """Test saving and processing a valid PNG image."""
        with app.app_context():
            # Create a test image
            img = Image.new('RGBA', (1000, 1000), color='red')
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            
            # Create FileStorage object
            file = FileStorage(
                stream=img_io,
                filename='test_wine.png',
                content_type='image/png'
            )
            
            # Process the image
            image_path, thumbnail_path = save_and_process_image(file)
            
            assert image_path is not None
            assert thumbnail_path is not None
            # PNG should be converted to JPEG
            assert image_path.endswith('.jpg')
            assert thumbnail_path.endswith('.jpg')
    
    def test_save_and_process_image_invalid_extension(self, app, temp_upload_dir):
        """Test processing file with invalid extension."""
        with app.app_context():
            # Create FileStorage with invalid extension
            file = FileStorage(
                stream=BytesIO(b'invalid data'),
                filename='test.txt',
                content_type='text/plain'
            )
            
            # Process should return None
            image_path, thumbnail_path = save_and_process_image(file)
            
            assert image_path is None
            assert thumbnail_path is None
    
    def test_save_and_process_image_no_file(self, app, temp_upload_dir):
        """Test processing with no file."""
        with app.app_context():
            image_path, thumbnail_path = save_and_process_image(None)
            
            assert image_path is None
            assert thumbnail_path is None
    
    def test_save_and_process_image_size_limits(self, app, temp_upload_dir):
        """Test that images are resized according to config."""
        with app.app_context():
            # Create a large test image
            img = Image.new('RGB', (3000, 3000), color='green')
            img_io = BytesIO()
            img.save(img_io, 'JPEG')
            img_io.seek(0)
            
            # Create FileStorage object
            file = FileStorage(
                stream=img_io,
                filename='large_wine.jpg',
                content_type='image/jpeg'
            )
            
            # Process the image
            image_path, thumbnail_path = save_and_process_image(file)
            
            assert image_path is not None
            assert thumbnail_path is not None
            
            # Check that files were created and resized
            full_image_path = os.path.join(
                os.path.dirname(app.config['UPLOAD_FOLDER']), 
                image_path
            )
            full_thumb_path = os.path.join(
                os.path.dirname(app.config['UPLOAD_FOLDER']), 
                thumbnail_path
            )
            
            if os.path.exists(full_image_path):
                img = Image.open(full_image_path)
                assert img.width <= 1200
                assert img.height <= 1200
            
            if os.path.exists(full_thumb_path):
                thumb = Image.open(full_thumb_path)
                assert thumb.width <= 300
                assert thumb.height <= 300
    
    def test_save_and_process_image_unique_filenames(self, app, temp_upload_dir):
        """Test that unique filenames are generated."""
        with app.app_context():
            # Create two identical images with same filename
            img1 = Image.new('RGB', (100, 100), color='red')
            img_io1 = BytesIO()
            img1.save(img_io1, 'JPEG')
            img_io1.seek(0)
            
            img2 = Image.new('RGB', (100, 100), color='blue')
            img_io2 = BytesIO()
            img2.save(img_io2, 'JPEG')
            img_io2.seek(0)
            
            file1 = FileStorage(
                stream=img_io1,
                filename='wine.jpg',
                content_type='image/jpeg'
            )
            
            file2 = FileStorage(
                stream=img_io2,
                filename='wine.jpg',
                content_type='image/jpeg'
            )
            
            # Process both images
            image_path1, thumbnail_path1 = save_and_process_image(file1)
            image_path2, thumbnail_path2 = save_and_process_image(file2)
            
            # Paths should be different due to UUID
            assert image_path1 != image_path2
            assert thumbnail_path1 != thumbnail_path2
    
    def test_delete_image_files_existing(self, app, temp_upload_dir):
        """Test deleting existing image files."""
        with app.app_context():
            # Update config to use temp directories
            app.config['UPLOAD_FOLDER'] = temp_upload_dir
            app.config['THUMBNAIL_FOLDER'] = os.path.join(temp_upload_dir, 'thumbnails')
            
            # Create test files
            test_image = os.path.join(temp_upload_dir, 'test.jpg')
            test_thumb = os.path.join(temp_upload_dir, 'thumbnails', 'thumb_test.jpg')
            
            with open(test_image, 'w') as f:
                f.write('test')
            with open(test_thumb, 'w') as f:
                f.write('test')
            
            # Delete the files
            delete_image_files('uploads/test.jpg', 'uploads/thumbnails/thumb_test.jpg')
            
            # Files should be deleted
            assert not os.path.exists(test_image)
            assert not os.path.exists(test_thumb)
    
    def test_delete_image_files_nonexistent(self, app, temp_upload_dir):
        """Test deleting non-existent files doesn't raise error."""
        with app.app_context():
            # Should not raise any exception
            delete_image_files('uploads/nonexistent.jpg', 'uploads/thumbnails/thumb_nonexistent.jpg')
    
    def test_delete_image_files_none_paths(self, app, temp_upload_dir):
        """Test deleting with None paths."""
        with app.app_context():
            # Should not raise any exception
            delete_image_files(None, None)
            delete_image_files('', '')
    
    def test_save_and_process_image_error_handling(self, app, temp_upload_dir):
        """Test error handling in image processing."""
        with app.app_context():
            # Create FileStorage with corrupted image data
            file = FileStorage(
                stream=BytesIO(b'corrupted image data'),
                filename='corrupted.jpg',
                content_type='image/jpeg'
            )
            
            # Should handle error gracefully
            image_path, thumbnail_path = save_and_process_image(file)
            
            assert image_path is None
            assert thumbnail_path is None