"""
Export service for converting books to various formats.

Orchestrates the export process and handles book loading, format routing,
and error handling.
"""

import os
import pickle
import re
from dataclasses import dataclass
from typing import Optional

from reader3 import Book


# --- Data Structures ---

@dataclass
class ExportResult:
    """Result of an export operation."""
    file_path: str      # Path to generated file
    filename: str       # Suggested download filename
    mime_type: str      # MIME type for HTTP response
    cleanup: bool = True  # Whether to delete file after sending


# --- Exceptions ---

class ExportError(Exception):
    """Base exception for export errors."""
    pass


class BookNotFoundError(ExportError):
    """Raised when book_id doesn't exist."""
    pass


class ConversionError(ExportError):
    """Raised when format conversion fails."""
    pass


# --- Constants ---

BOOKS_DIR = "books"


# --- Utility Functions ---

def sanitize_filename(title: str, max_length: int = 200) -> str:
    """
    Sanitize book title for use as filename.
    
    Removes invalid filesystem characters and limits length to ensure
    compatibility across Windows, macOS, and Linux.
    
    Args:
        title: Book title or text to sanitize
        max_length: Maximum filename length (default: 200)
    
    Returns:
        Sanitized filename string
    
    Examples:
        >>> sanitize_filename("My Book: A Story")
        'My_Book_A_Story'
        >>> sanitize_filename("Book/Title?")
        'BookTitle'
        >>> sanitize_filename("")
        'book_export'
    """
    if not title or not title.strip():
        return "book_export"
    
    # Remove or replace invalid characters: / \ : * ? " < > |
    # Replace with empty string
    sanitized = re.sub(r'[/\\:*?"<>|]', '', title)
    
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Remove any remaining non-alphanumeric characters except underscore, hyphen, and dot
    sanitized = re.sub(r'[^\w\-.]', '', sanitized)
    
    # Collapse multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length].rstrip('_')
    
    # Final check - if empty after sanitization, use fallback
    if not sanitized:
        return "book_export"
    
    return sanitized


def load_book(book_id: str) -> Book:
    """
    Load Book object from pickle file.
    
    Args:
        book_id: Book folder name (e.g., 'book_name_data')
    
    Returns:
        Book object
    
    Raises:
        BookNotFoundError: If book_id doesn't exist or pickle cannot be loaded
    """
    file_path = os.path.join(BOOKS_DIR, book_id, "book.pkl")
    
    if not os.path.exists(file_path):
        raise BookNotFoundError(f"Book not found: {book_id}")
    
    try:
        # Import reader3 to make classes available
        import sys
        import reader3
        
        # Add reader3 classes to __main__ namespace for pickle compatibility
        # This handles the case where pickle was saved with __main__.Book
        if '__main__' in sys.modules:
            main_module = sys.modules['__main__']
            if not hasattr(main_module, 'Book'):
                main_module.Book = reader3.Book
                main_module.BookMetadata = reader3.BookMetadata
                main_module.ChapterContent = reader3.ChapterContent
                main_module.TOCEntry = reader3.TOCEntry
        
        with open(file_path, "rb") as f:
            book = pickle.load(f)
        return book
    except Exception as e:
        raise BookNotFoundError(f"Failed to load book {book_id}: {e}")


def export_book(book_id: str, format: str, mode: Optional[str] = None) -> ExportResult:
    """
    Main entry point for export operations.
    
    Args:
        book_id: The book folder name (e.g., 'book_name_data')
        format: 'markdown' or 'pdf'
        mode: For markdown: 'single' or 'chapters'; ignored for PDF
    
    Returns:
        ExportResult containing file_path, filename, and mime_type
    
    Raises:
        BookNotFoundError: If book_id doesn't exist
        ExportError: If export process fails
    """
    # Load book
    book = load_book(book_id)
    
    # Route to appropriate exporter
    if format == 'markdown':
        # Import here to avoid circular dependencies
        from markdown_exporter import export_single_file, export_chapters
        
        if mode == 'chapters':
            file_path = export_chapters(book, book_id)
            filename = f"{sanitize_filename(book.metadata.title)}_chapters.zip"
            mime_type = "application/zip"
        else:  # default to single
            file_path = export_single_file(book, book_id)
            filename = f"{sanitize_filename(book.metadata.title)}_single.md"
            mime_type = "text/markdown"
    
    elif format == 'pdf':
        # Import here to avoid circular dependencies
        from pdf_exporter import export_pdf
        
        file_path = export_pdf(book, book_id)
        filename = f"{sanitize_filename(book.metadata.title)}.pdf"
        mime_type = "application/pdf"
    
    else:
        raise ExportError(f"Unsupported format: {format}")
    
    return ExportResult(
        file_path=file_path,
        filename=filename,
        mime_type=mime_type,
        cleanup=True
    )
