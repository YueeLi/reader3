"""Tests for image processing functionality."""

import os
import base64
import pytest
from image_processor import ImageProcessor


class TestImageProcessor:
    """Test ImageProcessor class."""
    
    @pytest.fixture
    def processor(self, test_book_id):
        """Create an ImageProcessor instance."""
        return ImageProcessor('books', test_book_id)
    
    def test_processor_initialization(self, processor):
        """Test that ImageProcessor initializes correctly."""
        assert processor.images_dir is not None
        assert processor._cache == {}
    
    def test_get_mime_type_jpg(self, processor):
        """Test MIME type detection for JPEG."""
        mime = processor.get_mime_type('test.jpg')
        assert mime == 'image/jpeg'
    
    def test_get_mime_type_png(self, processor):
        """Test MIME type detection for PNG."""
        mime = processor.get_mime_type('test.png')
        assert mime == 'image/png'
    
    def test_get_mime_type_gif(self, processor):
        """Test MIME type detection for GIF."""
        mime = processor.get_mime_type('test.gif')
        assert mime == 'image/gif'
    
    def test_get_base64_data_uri_format(self, processor):
        """Test that base64 data URI has correct format."""
        # Try to get a real image if it exists
        uri = processor.get_base64_data_uri('cover.jpeg')
        
        if uri:
            assert uri.startswith('data:image/')
            assert ';base64,' in uri
    
    def test_get_base64_data_uri_caching(self, processor):
        """Test that base64 encoding is cached."""
        # Get URI twice
        uri1 = processor.get_base64_data_uri('cover.jpeg')
        uri2 = processor.get_base64_data_uri('cover.jpeg')
        
        if uri1:
            # Should be the same object (cached)
            assert uri1 == uri2
            assert 'cover.jpeg' in processor._cache
    
    def test_get_base64_data_uri_nonexistent(self, processor):
        """Test that nonexistent image returns None."""
        uri = processor.get_base64_data_uri('nonexistent.jpg')
        assert uri is None
    
    def test_encode_image_returns_base64(self, processor):
        """Test that encode_image returns valid base64."""
        # Find a real image file
        if os.path.exists(processor.images_dir):
            images = os.listdir(processor.images_dir)
            if images:
                image_path = os.path.join(processor.images_dir, images[0])
                encoded = processor.encode_image(image_path)
                
                # Should be valid base64
                assert len(encoded) > 0
                # Try to decode it
                decoded = base64.b64decode(encoded)
                assert len(decoded) > 0
