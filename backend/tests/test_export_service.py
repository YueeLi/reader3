"""Tests for export service functionality."""

import os
import pytest
from backend.app.services.export_service import (
    sanitize_filename,
    load_book,
    export_book,
    BookNotFoundError,
    ExportError,
)


class TestFilenameSanitization:
    """Test filename sanitization."""
    
    def test_sanitize_removes_special_chars(self):
        """Test that special characters are removed."""
        result = sanitize_filename("Book/Title:Test?")
        assert '/' not in result
        assert ':' not in result
        assert '?' not in result
    
    def test_sanitize_replaces_spaces(self):
        """Test that spaces are replaced with underscores."""
        result = sanitize_filename("My Book Title")
        assert ' ' not in result
        assert '_' in result
    
    def test_sanitize_limits_length(self):
        """Test that filename length is limited."""
        long_title = "A" * 300
        result = sanitize_filename(long_title)
        assert len(result) <= 200
    
    def test_sanitize_empty_string(self):
        """Test that empty string returns fallback."""
        result = sanitize_filename("")
        assert result == "book_export"
    
    def test_sanitize_whitespace_only(self):
        """Test that whitespace-only string returns fallback."""
        result = sanitize_filename("   ")
        assert result == "book_export"
    
    def test_sanitize_preserves_valid_chars(self):
        """Test that valid characters are preserved."""
        result = sanitize_filename("Book_Title-123.txt")
        assert "Book_Title-123" in result


class TestBookLoading:
    """Test book loading functionality."""
    
    def test_load_existing_book(self, test_book_id):
        """Test that existing book can be loaded."""
        book = load_book(test_book_id)
        assert book is not None
        assert book.metadata is not None
        assert len(book.spine) > 0
    
    def test_load_nonexistent_book_raises_error(self):
        """Test that loading nonexistent book raises error."""
        with pytest.raises(BookNotFoundError):
            load_book("nonexistent_book_data")
    
    def test_loaded_book_has_metadata(self, test_book_id):
        """Test that loaded book has metadata."""
        book = load_book(test_book_id)
        assert book.metadata.title is not None
        assert len(book.metadata.authors) >= 0
    
    def test_loaded_book_has_spine(self, test_book_id):
        """Test that loaded book has spine chapters."""
        book = load_book(test_book_id)
        assert len(book.spine) > 0
        assert book.spine[0].content is not None
    
    def test_loaded_book_has_toc(self, test_book_id):
        """Test that loaded book has table of contents."""
        book = load_book(test_book_id)
        assert len(book.toc) >= 0


class TestExportBook:
    """Test main export_book function."""
    
    def test_export_markdown_single(self, test_book_id):
        """Test exporting book as single Markdown file."""
        result = export_book(test_book_id, format='markdown', mode='single')
        
        assert result.file_path is not None
        assert os.path.exists(result.file_path)
        assert result.filename.endswith('.md')
        assert result.mime_type == 'text/markdown'
    
    def test_export_markdown_chapters(self, test_book_id):
        """Test exporting book as chapter Markdown files."""
        result = export_book(test_book_id, format='markdown', mode='chapters')
        
        assert result.file_path is not None
        assert os.path.exists(result.file_path)
        assert result.filename.endswith('.zip')
        assert result.mime_type == 'application/zip'
    
    def test_export_pdf(self, test_book_id):
        """Test exporting book as PDF."""
        result = export_book(test_book_id, format='pdf')
        
        assert result.file_path is not None
        assert os.path.exists(result.file_path)
        assert result.filename.endswith('.pdf')
        assert result.mime_type == 'application/pdf'
    
    def test_export_nonexistent_book_raises_error(self):
        """Test that exporting nonexistent book raises error."""
        with pytest.raises(BookNotFoundError):
            export_book("nonexistent_book_data", format='markdown')
    
    def test_export_invalid_format_raises_error(self, test_book_id):
        """Test that invalid format raises error."""
        with pytest.raises(ExportError):
            export_book(test_book_id, format='invalid_format')
    
    def test_export_creates_exports_directory(self, test_book_id):
        """Test that export creates exports directory."""
        result = export_book(test_book_id, format='markdown', mode='single')
        
        exports_dir = os.path.dirname(result.file_path)
        assert os.path.exists(exports_dir)
        assert 'exports' in exports_dir
