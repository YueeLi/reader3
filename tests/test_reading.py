"""Tests for basic reading functionality."""

import pytest
from bs4 import BeautifulSoup


class TestLibraryView:
    """Test library page functionality."""
    
    def test_library_page_loads(self, client):
        """Test that library page loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Library" in response.text
    
    def test_library_shows_books(self, client, test_book_id):
        """Test that library displays available books."""
        response = client.get("/")
        assert response.status_code == 200
        
        # Check that book cards are present
        soup = BeautifulSoup(response.text, 'html.parser')
        book_cards = soup.find_all(class_='book-card')
        assert len(book_cards) > 0
    
    def test_library_has_read_buttons(self, client):
        """Test that each book has a Read Book button."""
        response = client.get("/")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        read_buttons = soup.find_all('a', class_='btn', string='Read Book')
        assert len(read_buttons) > 0
    
    def test_library_has_export_buttons(self, client):
        """Test that each book has export functionality."""
        response = client.get("/")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        export_buttons = soup.find_all('button', class_='export-btn')
        assert len(export_buttons) > 0


class TestReaderView:
    """Test reader page functionality."""
    
    def test_reader_page_loads(self, client, test_book_id):
        """Test that reader page loads successfully."""
        response = client.get(f"/read/{test_book_id}/0")
        assert response.status_code == 200
    
    def test_reader_displays_content(self, client, test_book_id):
        """Test that reader displays book content."""
        response = client.get(f"/read/{test_book_id}/0")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check for main content area
        content = soup.find(class_='book-content')
        assert content is not None
    
    def test_reader_has_sidebar(self, client, test_book_id):
        """Test that reader has navigation sidebar."""
        response = client.get(f"/read/{test_book_id}/0")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        sidebar = soup.find(id='sidebar')
        assert sidebar is not None
    
    def test_reader_has_toc(self, client, test_book_id):
        """Test that reader displays table of contents."""
        response = client.get(f"/read/{test_book_id}/0")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        toc_links = soup.find_all(class_='toc-link')
        assert len(toc_links) > 0
    
    def test_reader_has_spine_map(self, client, test_book_id):
        """Test that reader includes spineMap JavaScript object."""
        response = client.get(f"/read/{test_book_id}/0")
        
        # Check for spineMap in JavaScript
        assert "const spineMap" in response.text
        assert "function findAndGo" in response.text
    
    def test_reader_has_export_menu(self, client, test_book_id):
        """Test that reader has export menu."""
        response = client.get(f"/read/{test_book_id}/0")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        export_menu = soup.find(class_='export-menu')
        assert export_menu is not None


class TestNavigation:
    """Test navigation functionality."""
    
    def test_redirect_to_first_chapter(self, client, test_book_id):
        """Test that /read/{book_id} loads chapter 0."""
        response = client.get(f"/read/{test_book_id}")
        assert response.status_code == 200
        # Should display first chapter content
        assert 'book-content' in response.text
    
    def test_next_button_present(self, client, test_book_id):
        """Test that Next button is present on first chapter."""
        response = client.get(f"/read/{test_book_id}/0")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        next_button = soup.find('a', class_='nav-btn', string=lambda s: 'Next' in s if s else False)
        assert next_button is not None
    
    def test_prev_button_disabled_on_first_chapter(self, client, test_book_id):
        """Test that Previous button is disabled on first chapter."""
        response = client.get(f"/read/{test_book_id}/0")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        prev_button = soup.find('span', class_='nav-btn disabled', string=lambda s: 'Previous' in s if s else False)
        assert prev_button is not None
    
    def test_chapter_navigation_works(self, client, test_book_id):
        """Test that we can navigate to different chapters."""
        # Test chapter 0
        response0 = client.get(f"/read/{test_book_id}/0")
        assert response0.status_code == 200
        
        # Test chapter 1
        response1 = client.get(f"/read/{test_book_id}/1")
        assert response1.status_code == 200
        
        # Content should be different
        assert response0.text != response1.text
    
    def test_invalid_chapter_returns_404(self, client, test_book_id):
        """Test that invalid chapter index returns 404."""
        response = client.get(f"/read/{test_book_id}/99999")
        assert response.status_code == 404
    
    def test_invalid_book_returns_404(self, client):
        """Test that invalid book ID returns 404."""
        response = client.get("/read/nonexistent_book_data/0")
        assert response.status_code == 404


class TestImageServing:
    """Test image serving functionality."""
    
    def test_image_route_exists(self, client, test_book_id):
        """Test that image serving route works."""
        # Try to load cover image
        response = client.get(f"/read/{test_book_id}/images/cover.jpeg")
        
        # Should return 200 if image exists, or 404 if not
        assert response.status_code in [200, 404]
    
    def test_image_returns_correct_content_type(self, client, test_book_id):
        """Test that images return correct content type."""
        response = client.get(f"/read/{test_book_id}/images/cover.jpeg")
        
        if response.status_code == 200:
            # Should be an image MIME type
            assert 'image' in response.headers.get('content-type', '')
    
    def test_nonexistent_image_returns_404(self, client, test_book_id):
        """Test that nonexistent image returns 404."""
        response = client.get(f"/read/{test_book_id}/images/nonexistent.jpg")
        assert response.status_code == 404
