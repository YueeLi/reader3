"""
Image processing utilities for book export.

Handles loading images from disk and encoding them as base64 data URIs
for embedding in Markdown and PDF exports.
"""

import os
import base64
import mimetypes
from typing import Optional, Dict


class ImageProcessor:
    """Handles image loading and base64 encoding for export."""
    
    def __init__(self, books_dir: str, book_id: str):
        """
        Initialize ImageProcessor with path to book's image directory.
        
        Args:
            books_dir: Base directory containing all books (e.g., 'books')
            book_id: Book folder name (e.g., 'book_name_data')
        """
        self.images_dir = os.path.join(books_dir, book_id, 'images')
        self._cache: Dict[str, str] = {}  # Cache encoded images
    
    def get_base64_data_uri(self, image_filename: str) -> Optional[str]:
        """
        Load image and return as base64 data URI.
        
        Format: data:image/png;base64,iVBORw0KGgoAAAANS...
        
        Args:
            image_filename: Name of the image file (e.g., 'pic.jpg')
        
        Returns:
            Base64 data URI string, or None if image not found
        
        Example:
            >>> processor = ImageProcessor('books', 'mybook_data')
            >>> uri = processor.get_base64_data_uri('cover.jpg')
            >>> uri.startswith('data:image/jpeg;base64,')
            True
        """
        # Check cache first
        if image_filename in self._cache:
            return self._cache[image_filename]
        
        # Build full path
        image_path = os.path.join(self.images_dir, image_filename)
        
        # Check if file exists
        if not os.path.exists(image_path):
            return None
        
        try:
            # Encode image
            encoded = self.encode_image(image_path)
            mime_type = self.get_mime_type(image_filename)
            
            # Build data URI
            data_uri = f"data:{mime_type};base64,{encoded}"
            
            # Cache result
            self._cache[image_filename] = data_uri
            
            return data_uri
        
        except Exception as e:
            # Log error but don't crash
            print(f"Warning: Failed to encode image {image_filename}: {e}")
            return None
    
    def get_mime_type(self, filename: str) -> str:
        """
        Determine MIME type from file extension.
        
        Args:
            filename: Image filename
        
        Returns:
            MIME type string (e.g., 'image/jpeg', 'image/png')
        """
        # Get extension
        _, ext = os.path.splitext(filename.lower())
        
        # Use mimetypes library
        mime_type = mimetypes.guess_type(filename)[0]
        
        # Fallback to common types if guess fails
        if not mime_type:
            mime_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml',
            }
            mime_type = mime_map.get(ext, 'image/jpeg')  # Default to jpeg
        
        return mime_type
    
    def encode_image(self, image_path: str) -> str:
        """
        Read image file and encode to base64 string.
        
        Args:
            image_path: Full path to image file
        
        Returns:
            Base64 encoded string
        
        Raises:
            IOError: If file cannot be read
        """
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Encode to base64
        encoded = base64.b64encode(image_data).decode('utf-8')
        
        return encoded
