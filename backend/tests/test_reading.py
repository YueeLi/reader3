"""Tests for basic reading functionality."""

import pytest


class TestBooksApi:
    """Test books API functionality."""

    def test_books_list(self, client):
        response = client.get("/api/books")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_books_list_contains_expected_fields(self, client, test_book_id):
        response = client.get("/api/books")
        data = response.json()
        assert any(book["id"] == test_book_id for book in data)
        sample = data[0]
        assert "title" in sample
        assert "author" in sample
        assert "chapters" in sample
        assert "coverUrl" in sample


class TestBookDetailApi:
    """Test book detail API."""

    def test_book_detail(self, client, test_book_id):
        response = client.get(f"/api/books/{test_book_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_book_id
        assert data["chapters"] >= 1
        assert isinstance(data["toc"], list)

    def test_book_detail_not_found(self, client):
        response = client.get("/api/books/nonexistent_book_data")
        assert response.status_code == 404


class TestChapterApi:
    """Test chapter API."""

    def test_chapter_fetch(self, client, test_book_id):
        response = client.get(f"/api/books/{test_book_id}/chapters/0")
        assert response.status_code == 200
        data = response.json()
        assert "html" in data
        assert data["order"] == 0

    def test_invalid_chapter_returns_404(self, client, test_book_id):
        response = client.get(f"/api/books/{test_book_id}/chapters/99999")
        assert response.status_code == 404

    def test_invalid_book_returns_404(self, client):
        response = client.get("/api/books/nonexistent_book_data/chapters/0")
        assert response.status_code == 404


class TestImageServing:
    """Test image serving functionality."""

    def test_image_route_exists(self, client, test_book_id):
        response = client.get(f"/books/{test_book_id}/images/cover.jpeg")
        assert response.status_code in [200, 404]

    def test_image_returns_correct_content_type(self, client, test_book_id):
        response = client.get(f"/books/{test_book_id}/images/cover.jpeg")

        if response.status_code == 200:
            assert "image" in response.headers.get("content-type", "")

    def test_nonexistent_image_returns_404(self, client, test_book_id):
        response = client.get(f"/books/{test_book_id}/images/nonexistent.jpg")
        assert response.status_code == 404
