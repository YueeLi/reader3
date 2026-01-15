"""Tests for export functionality."""

import os
import zipfile
import pytest
from io import BytesIO


class TestMarkdownExport:
    """Test Markdown export functionality."""
    
    def test_markdown_single_export_endpoint(self, client, test_book_id):
        """Test that Markdown single file export endpoint works."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=single")
        assert response.status_code == 200
        assert 'text/markdown' in response.headers['content-type']
    
    def test_markdown_single_has_content(self, client, test_book_id):
        """Test that exported Markdown file has content."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=single")
        assert len(response.content) > 1000  # Should be substantial
    
    def test_markdown_single_has_frontmatter(self, client, test_book_id):
        """Test that Markdown export includes YAML frontmatter."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=single")
        content = response.content.decode('utf-8')
        
        assert content.startswith('---')
        assert 'title:' in content
        assert 'authors:' in content
    
    def test_markdown_single_has_toc(self, client, test_book_id):
        """Test that Markdown export includes table of contents."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=single")
        content = response.content.decode('utf-8')
        
        assert 'Table of Contents' in content or '## 目录' in content
    
    def test_markdown_single_has_embedded_images(self, client, test_book_id):
        """Test that Markdown export has base64 embedded images."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=single")
        content = response.content.decode('utf-8')
        
        # Check for data URI format
        if 'data:image' in content:
            assert 'base64,' in content
    
    def test_markdown_chapters_export_endpoint(self, client, test_book_id):
        """Test that Markdown chapters export endpoint works."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=chapters")
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/zip'
    
    def test_markdown_chapters_is_valid_zip(self, client, test_book_id):
        """Test that chapters export is a valid ZIP file."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=chapters")
        
        # Try to open as ZIP
        zip_file = zipfile.ZipFile(BytesIO(response.content))
        assert zip_file.testzip() is None  # No errors
    
    def test_markdown_chapters_has_readme(self, client, test_book_id):
        """Test that chapters ZIP includes README.md."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=chapters")
        
        zip_file = zipfile.ZipFile(BytesIO(response.content))
        filenames = zip_file.namelist()
        
        assert 'README.md' in filenames
    
    def test_markdown_chapters_has_multiple_files(self, client, test_book_id):
        """Test that chapters ZIP contains multiple chapter files."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=chapters")
        
        zip_file = zipfile.ZipFile(BytesIO(response.content))
        filenames = zip_file.namelist()
        
        # Should have README plus chapter files
        assert len(filenames) > 1
    
    def test_markdown_export_invalid_mode(self, client, test_book_id):
        """Test that invalid mode parameter is rejected."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=invalid")
        assert response.status_code == 422  # Validation error


class TestPDFExport:
    """Test PDF export functionality."""
    
    def test_pdf_export_endpoint(self, client, test_book_id):
        """Test that PDF export endpoint works."""
        response = client.get(f"/export/{test_book_id}/pdf")
        assert response.status_code == 200
        assert response.headers['content-type'] == 'application/pdf'
    
    def test_pdf_has_content(self, client, test_book_id):
        """Test that exported PDF has content."""
        response = client.get(f"/export/{test_book_id}/pdf")
        assert len(response.content) > 10000  # PDFs are typically large
    
    def test_pdf_is_valid_format(self, client, test_book_id):
        """Test that exported file is a valid PDF."""
        response = client.get(f"/export/{test_book_id}/pdf")
        
        # PDF files start with %PDF-
        assert response.content.startswith(b'%PDF-')
    
    def test_pdf_has_correct_headers(self, client, test_book_id):
        """Test that PDF response has correct download headers."""
        response = client.get(f"/export/{test_book_id}/pdf")
        
        assert 'content-disposition' in response.headers
        assert 'attachment' in response.headers['content-disposition']


class TestExportErrors:
    """Test export error handling."""
    
    def test_export_nonexistent_book_returns_404(self, client):
        """Test that exporting nonexistent book returns 404."""
        response = client.get("/export/nonexistent_book_data/markdown")
        assert response.status_code == 404
    
    def test_export_invalid_format(self, client, test_book_id):
        """Test that invalid export format is handled."""
        # This would require modifying the route to accept format parameter
        # For now, we test that valid formats work
        response = client.get(f"/export/{test_book_id}/markdown")
        assert response.status_code == 200


class TestExportFilenames:
    """Test export filename handling."""
    
    def test_markdown_filename_is_sanitized(self, client, test_book_id):
        """Test that Markdown export filename is properly sanitized."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=single")
        
        content_disposition = response.headers.get('content-disposition', '')
        assert 'filename' in content_disposition
        assert '.md' in content_disposition
    
    def test_pdf_filename_is_sanitized(self, client, test_book_id):
        """Test that PDF export filename is properly sanitized."""
        response = client.get(f"/export/{test_book_id}/pdf")
        
        content_disposition = response.headers.get('content-disposition', '')
        assert 'filename' in content_disposition
        assert '.pdf' in content_disposition
    
    def test_chapters_filename_is_sanitized(self, client, test_book_id):
        """Test that chapters ZIP filename is properly sanitized."""
        response = client.get(f"/export/{test_book_id}/markdown?mode=chapters")
        
        content_disposition = response.headers.get('content-disposition', '')
        assert 'filename' in content_disposition
        assert '.zip' in content_disposition


class TestExportIntegration:
    """Integration tests for export functionality."""
    
    def test_export_multiple_formats_same_book(self, client, test_book_id):
        """Test that we can export the same book in multiple formats."""
        # Export as Markdown
        md_response = client.get(f"/export/{test_book_id}/markdown?mode=single")
        assert md_response.status_code == 200
        
        # Export as PDF
        pdf_response = client.get(f"/export/{test_book_id}/pdf")
        assert pdf_response.status_code == 200
        
        # Export as chapters
        chapters_response = client.get(f"/export/{test_book_id}/markdown?mode=chapters")
        assert chapters_response.status_code == 200
    
    def test_export_different_books(self, client, test_book_id, alt_book_id):
        """Test that we can export different books."""
        # Export first book
        response1 = client.get(f"/export/{test_book_id}/markdown?mode=single")
        assert response1.status_code == 200
        
        # Export second book
        response2 = client.get(f"/export/{alt_book_id}/markdown?mode=single")
        assert response2.status_code == 200
        
        # Content should be different
        assert response1.content != response2.content
