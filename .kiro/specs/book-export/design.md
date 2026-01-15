# Design Document: Book Export Feature

## Overview

This document describes the design for adding export functionality to the EPUB reader application. The system will enable users to export processed books into Markdown (single-file or chapter-split) and PDF formats through a web interface. All exports will have embedded images for self-contained output files.

The design follows a modular architecture with separate concerns for:

- Export orchestration and format selection
- HTML-to-Markdown conversion with image embedding
- HTML-to-PDF rendering with image embedding
- File packaging and delivery through web APIs

## Architecture

### High-Level Architecture

```
┌─────────────────┐
│  Web Interface  │
│   (FastAPI)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Export Router   │
│  (API Layer)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Export Service  │
│  (Orchestrator) │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌─────────┐
│Markdown │ │   PDF   │
│Exporter │ │Exporter │
└─────────┘ └─────────┘
```

### Component Responsibilities

1. **Export Router** (`server.py` additions)

   - Handles HTTP requests for export endpoints
   - Validates book_id and export parameters
   - Returns appropriate file responses with headers

2. **Export Service** (`export_service.py`)

   - Loads Book objects from pickle files
   - Orchestrates export process based on format and mode
   - Handles file cleanup and error recovery

3. **Markdown Exporter** (`markdown_exporter.py`)

   - Converts HTML chapters to Markdown
   - Embeds images as base64 data URIs
   - Generates frontmatter and TOC
   - Supports single-file and chapter-split modes

4. **PDF Exporter** (`pdf_exporter.py`)

   - Renders HTML to PDF using weasyprint
   - Embeds images directly in PDF
   - Generates title page and bookmarks
   - Maintains original layout and styling

5. **Image Processor** (`image_processor.py`)
   - Reads image files from disk
   - Encodes images to base64
   - Determines MIME types
   - Handles missing images gracefully

## Components and Interfaces

### 1. Export Service

**Module**: `export_service.py`

**Key Functions**:

```python
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

def load_book(book_id: str) -> Book:
    """Load Book object from pickle file."""

def sanitize_filename(title: str) -> str:
    """
    Sanitize book title for use as filename.
    Removes invalid characters and limits length.
    """
```

**Data Structures**:

```python
@dataclass
class ExportResult:
    file_path: str      # Path to generated file
    filename: str       # Suggested download filename
    mime_type: str      # MIME type for HTTP response
    cleanup: bool       # Whether to delete file after sending
```

### 2. Markdown Exporter

**Module**: `markdown_exporter.py`

**Key Functions**:

```python
def export_single_file(book: Book, output_path: str, image_processor: ImageProcessor) -> str:
    """
    Export entire book as single Markdown file.

    Process:
    1. Generate YAML frontmatter with metadata
    2. Generate table of contents with anchor links
    3. Convert each spine chapter to Markdown
    4. Embed images as base64 data URIs
    5. Concatenate with chapter separators

    Returns: Path to generated .md file
    """

def export_chapters(book: Book, output_dir: str, image_processor: ImageProcessor) -> str:
    """
    Export book as multiple Markdown files in ZIP archive.

    Process:
    1. Create temporary directory
    2. Generate README.md with metadata and TOC
    3. Convert each chapter to separate .md file
    4. Embed images in each file
    5. Create ZIP archive
    6. Clean up temporary directory

    Returns: Path to generated .zip file
    """

def html_to_markdown(html: str, image_processor: ImageProcessor, image_map: Dict[str, str]) -> str:
    """
    Convert HTML content to Markdown with embedded images.

    Uses markdownify library for conversion.
    Replaces image src attributes with base64 data URIs.
    """

def generate_frontmatter(metadata: BookMetadata) -> str:
    """Generate YAML frontmatter from book metadata."""

def generate_toc_markdown(toc: List[TOCEntry], mode: str) -> str:
    """
    Generate Markdown table of contents.

    For single-file: Links to anchors (#chapter-1)
    For chapters: Links to files (01_chapter.md)
    """
```

**Dependencies**:

- `markdownify`: HTML to Markdown conversion
- `PyYAML`: YAML frontmatter generation

### 3. PDF Exporter

**Module**: `pdf_exporter.py`

**Key Functions**:

```python
def export_pdf(book: Book, output_path: str, image_processor: ImageProcessor) -> str:
    """
    Export book as PDF with embedded images.

    Process:
    1. Generate title page HTML with metadata
    2. Combine all spine chapters into single HTML document
    3. Resolve and embed images as data URIs in HTML
    4. Apply CSS styling for print layout
    5. Render HTML to PDF using weasyprint
    6. Add PDF bookmarks from TOC structure

    Returns: Path to generated .pdf file
    """

def generate_title_page(metadata: BookMetadata) -> str:
    """Generate HTML for PDF title page."""

def combine_chapters_html(spine: List[ChapterContent], image_processor: ImageProcessor, image_map: Dict[str, str]) -> str:
    """
    Combine all chapters into single HTML document.
    Replace image src with base64 data URIs.
    Insert page breaks between chapters.
    """

def generate_pdf_css() -> str:
    """
    Generate CSS for PDF rendering.
    Includes page size, margins, fonts, and print-specific styles.
    """

def create_pdf_bookmarks(pdf_writer, toc: List[TOCEntry]) -> None:
    """
    Add hierarchical bookmarks to PDF from TOC structure.
    Uses PyPDF2 or weasyprint bookmark API.
    """
```

**Dependencies**:

- `weasyprint`: HTML to PDF rendering
- `Pillow`: Image processing support for weasyprint

### 4. Image Processor

**Module**: `image_processor.py`

**Key Functions**:

```python
class ImageProcessor:
    """Handles image loading and base64 encoding."""

    def __init__(self, books_dir: str, book_id: str):
        """Initialize with path to book's image directory."""
        self.images_dir = os.path.join(books_dir, book_id, 'images')
        self._cache: Dict[str, str] = {}  # Cache encoded images

    def get_base64_data_uri(self, image_filename: str) -> Optional[str]:
        """
        Load image and return as base64 data URI.

        Format: data:image/png;base64,iVBORw0KGgoAAAANS...

        Returns None if image not found.
        Caches results to avoid re-encoding same image.
        """

    def get_mime_type(self, filename: str) -> str:
        """Determine MIME type from file extension."""

    def encode_image(self, image_path: str) -> str:
        """Read image file and encode to base64 string."""
```

### 5. Export Router (FastAPI)

**Module**: `server.py` (additions)

**Endpoints**:

```python
@app.get("/export/{book_id}/markdown")
async def export_markdown(
    book_id: str,
    mode: str = Query("single", regex="^(single|chapters)$")
) -> FileResponse:
    """
    Export book as Markdown.

    Query Parameters:
        mode: 'single' for single file, 'chapters' for ZIP archive

    Returns:
        FileResponse with .md or .zip file
    """

@app.get("/export/{book_id}/pdf")
async def export_pdf(book_id: str) -> FileResponse:
    """
    Export book as PDF.

    Returns:
        FileResponse with .pdf file
    """
```

## Data Models

### Existing Models (from reader3.py)

We will reuse existing data structures:

- `Book`: Main book object with metadata, spine, toc, images
- `BookMetadata`: Title, authors, publisher, etc.
- `ChapterContent`: Individual chapter with HTML content
- `TOCEntry`: Table of contents entry with hierarchy

### New Models

```python
@dataclass
class ExportResult:
    """Result of an export operation."""
    file_path: str
    filename: str
    mime_type: str
    cleanup: bool = True  # Delete file after sending

class ExportError(Exception):
    """Base exception for export errors."""
    pass

class BookNotFoundError(ExportError):
    """Raised when book_id doesn't exist."""
    pass

class ConversionError(ExportError):
    """Raised when format conversion fails."""
    pass
```

## Correctness Properties

_A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees._

### Property 1: Export completeness

_For any_ valid Book object, exporting to any format should include all spine chapters in the correct order.

**Validates: Requirements 2.1, 2.6, 3.1, 4.6**

### Property 2: Image embedding consistency

_For any_ Book with images, all image references in the exported output should be either valid base64 data URIs (Markdown) or embedded in the PDF, with no external file dependencies.

**Validates: Requirements 2.5, 3.3, 4.3, 5.3, 5.5**

### Property 3: Filename sanitization safety

_For any_ book title string (including those with special characters), the sanitized filename should contain only valid filesystem characters and be usable across Windows, macOS, and Linux.

**Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

### Property 4: Metadata preservation

_For any_ Book with metadata, the exported output should contain all available metadata fields (title, authors, publisher, date) in an accessible format.

**Validates: Requirements 2.3, 4.4**

### Property 5: TOC structure preservation

_For any_ Book with a hierarchical TOC, the exported output should maintain the same hierarchical structure with working navigation links or bookmarks.

**Validates: Requirements 2.4, 3.4, 4.5**

### Property 6: Chapter split file naming

_For any_ Book exported in chapter-split mode, each chapter file should have a unique, ordered filename that corresponds to its position in the spine.

**Validates: Requirements 3.2, 8.4**

### Property 7: Error recovery without corruption

_For any_ export operation that encounters an error (missing image, conversion failure), the system should either complete with warnings or fail cleanly without leaving corrupted partial files.

**Validates: Requirements 5.6, 7.2, 7.3, 7.4, 7.5**

### Property 8: API response correctness

_For any_ valid export request, the API should return a file with the correct MIME type, Content-Disposition header, and filename matching the export format.

**Validates: Requirements 6.2, 6.4, 6.7**

### Property 9: ZIP archive completeness

_For any_ chapter-split Markdown export, the ZIP archive should contain exactly N+1 files (N chapter files plus 1 README.md) where N is the number of spine chapters.

**Validates: Requirements 3.5**

### Property 10: Base64 encoding validity

_For any_ image file processed for embedding, the resulting base64 data URI should be valid and decodable back to the original image data.

**Validates: Requirements 5.2, 5.3**

## Error Handling

### Error Categories

1. **Book Loading Errors**

   - Book pickle file not found
   - Pickle deserialization failure
   - Corrupted book data

2. **Conversion Errors**

   - HTML to Markdown conversion failure
   - HTML to PDF rendering failure
   - Invalid HTML structure

3. **Image Processing Errors**

   - Image file not found
   - Image encoding failure
   - Unsupported image format

4. **File System Errors**

   - Insufficient disk space
   - Permission denied
   - Path too long

5. **API Errors**
   - Invalid book_id
   - Invalid export parameters
   - Request timeout

### Error Handling Strategy

**Graceful Degradation**:

- Missing images: Log warning, continue without image
- Single chapter conversion failure: Include error placeholder, continue
- Non-critical metadata missing: Use defaults

**Fail Fast**:

- Book not found: Return 404 immediately
- PDF rendering engine failure: Return 500 with details
- Disk space exhausted: Return 500 with details

**Cleanup**:

- Always clean up temporary files on error
- Use context managers for file operations
- Implement try-finally blocks for resource cleanup

### Error Response Format

```python
{
    "error": "ExportError",
    "message": "Failed to export book",
    "details": "PDF rendering failed: missing font",
    "book_id": "example_book_data"
}
```

## Testing Strategy

### Unit Tests

Test individual components in isolation:

1. **Image Processor Tests**

   - Test base64 encoding of various image formats (PNG, JPEG, GIF)
   - Test MIME type detection
   - Test caching behavior
   - Test handling of missing images

2. **Filename Sanitization Tests**

   - Test removal of invalid characters
   - Test length limiting
   - Test empty string handling
   - Test Unicode character handling

3. **Markdown Conversion Tests**

   - Test HTML to Markdown conversion for various HTML structures
   - Test frontmatter generation
   - Test TOC generation for single-file and chapter modes
   - Test image replacement with data URIs

4. **PDF Generation Tests**
   - Test title page generation
   - Test chapter combination
   - Test CSS application
   - Test bookmark creation

### Property-Based Tests

Test universal properties across randomized inputs (minimum 100 iterations per test):

1. **Property Test: Export Completeness**

   - Generate random Book objects with varying chapter counts
   - Export to all formats
   - Verify all chapters present in output
   - **Feature: book-export, Property 1: Export completeness**

2. **Property Test: Image Embedding**

   - Generate Books with random image counts and types
   - Export to all formats
   - Verify no external image references remain
   - **Feature: book-export, Property 2: Image embedding consistency**

3. **Property Test: Filename Sanitization**

   - Generate random strings with special characters
   - Sanitize filenames
   - Verify all output filenames are valid on all platforms
   - **Feature: book-export, Property 3: Filename sanitization safety**

4. **Property Test: Metadata Preservation**

   - Generate Books with random metadata combinations
   - Export to all formats
   - Verify all metadata fields present in output
   - **Feature: book-export, Property 4: Metadata preservation**

5. **Property Test: TOC Structure**

   - Generate Books with random hierarchical TOC structures
   - Export to all formats
   - Verify TOC hierarchy preserved
   - **Feature: book-export, Property 5: TOC structure preservation**

6. **Property Test: Chapter File Naming**

   - Generate Books with random chapter counts
   - Export in chapter-split mode
   - Verify unique, ordered filenames
   - **Feature: book-export, Property 6: Chapter split file naming**

7. **Property Test: Error Recovery**

   - Generate Books with intentionally missing images
   - Export to all formats
   - Verify clean completion or failure without corruption
   - **Feature: book-export, Property 7: Error recovery without corruption**

8. **Property Test: Base64 Round-Trip**
   - Generate random image files
   - Encode to base64 data URI
   - Decode and verify data integrity
   - **Feature: book-export, Property 10: Base64 encoding validity**

### Integration Tests

Test end-to-end workflows:

1. **Full Export Workflow Tests**

   - Load real EPUB file
   - Process with reader3.py
   - Export to all formats
   - Verify output files are valid and complete

2. **API Endpoint Tests**

   - Test all export endpoints with valid requests
   - Test error responses for invalid requests
   - Test file download headers and MIME types

3. **Large Book Tests**
   - Test export of books with 100+ chapters
   - Test export of books with 100+ images
   - Verify performance and memory usage

### Testing Tools

- **Unit Testing**: `pytest`
- **Property-Based Testing**: `hypothesis` (Python PBT library)
- **HTTP Testing**: `httpx` or `TestClient` from FastAPI
- **File Validation**:
  - Markdown: Parse with `markdown` library
  - PDF: Validate with `PyPDF2` or `pdfplumber`
  - ZIP: Validate with `zipfile`

### Test Configuration

- Minimum 100 iterations for each property-based test
- Use fixtures for sample Book objects
- Use temporary directories for test outputs
- Clean up all test files after execution

## Implementation Notes

### Dependencies to Add

```toml
[tool.poetry.dependencies]
markdownify = "^0.11.6"      # HTML to Markdown
weasyprint = "^60.0"          # HTML to PDF
PyYAML = "^6.0"               # YAML frontmatter
Pillow = "^10.0"              # Image processing
```

### File Organization

```
project/
├── reader3.py              # Existing EPUB processor
├── server.py               # Existing FastAPI server (add export routes)
├── export_service.py       # New: Export orchestration
├── markdown_exporter.py    # New: Markdown export logic
├── pdf_exporter.py         # New: PDF export logic
├── image_processor.py      # New: Image encoding utilities
├── tests/
│   ├── test_export_service.py
│   ├── test_markdown_exporter.py
│   ├── test_pdf_exporter.py
│   ├── test_image_processor.py
│   └── test_export_properties.py  # Property-based tests
└── templates/
    ├── library.html        # Update: Add export buttons
    └── reader.html         # Update: Add export menu
```

### Performance Considerations

1. **Image Caching**: Cache base64-encoded images to avoid re-encoding
2. **Streaming**: For large PDFs, consider streaming response
3. **Async Processing**: For very large books, consider background task queue
4. **Memory Management**: Process chapters incrementally to avoid loading entire book in memory

### Security Considerations

1. **Path Traversal**: Validate book_id to prevent directory traversal attacks
2. **File Size Limits**: Set maximum export file size to prevent DoS
3. **Temporary File Cleanup**: Always clean up temporary files to prevent disk exhaustion
4. **Input Validation**: Validate all user inputs (book_id, mode parameters)

## Future Enhancements

Potential features for future iterations:

1. **Export Configuration**

   - Custom CSS for PDF styling
   - Font selection for PDF
   - Page size options (A4, Letter, etc.)
   - Include/exclude images option

2. **Progress Tracking**

   - WebSocket-based progress updates for large exports
   - Estimated time remaining
   - Cancel operation support

3. **Batch Export**

   - Export multiple books at once
   - Export entire library

4. **Additional Formats**

   - EPUB re-export with modifications
   - Plain text export
   - HTML export

5. **Cloud Storage Integration**
   - Direct export to Google Drive, Dropbox, etc.
   - Share exported files via link
