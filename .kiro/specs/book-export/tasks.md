# Implementation Plan: Book Export Feature

## Overview

This plan implements the book export functionality in incremental steps, building from core utilities to complete export workflows. Each task builds on previous work and includes validation through tests.

## Tasks

- [x] 1. Set up project dependencies and utilities

  - Add required dependencies to `pyproject.toml`: markdownify, weasyprint, PyYAML, Pillow
  - Install dependencies using package manager
  - _Requirements: All (foundation)_

- [ ] 2. Implement image processing module

  - [x] 2.1 Create `image_processor.py` with ImageProcessor class

    - Implement `__init__` to set up image directory path
    - Implement `get_base64_data_uri` method with caching
    - Implement `get_mime_type` method for file extension detection
    - Implement `encode_image` method for base64 encoding
    - _Requirements: 5.1, 5.2_

  - [ ]\* 2.2 Write property test for base64 round-trip

    - **Property 10: Base64 encoding validity**
    - **Validates: Requirements 5.2, 5.3**

  - [ ]\* 2.3 Write unit tests for ImageProcessor
    - Test encoding of PNG, JPEG, GIF images
    - Test MIME type detection
    - Test caching behavior
    - Test handling of missing images
    - _Requirements: 5.6_

- [ ] 3. Implement filename sanitization

  - [x] 3.1 Add `sanitize_filename` function to `export_service.py`

    - Remove invalid filesystem characters: `/ \ : * ? " < > |`
    - Replace spaces with underscores
    - Limit length to 200 characters
    - Handle empty strings with fallback name
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

  - [ ]\* 3.2 Write property test for filename sanitization
    - **Property 3: Filename sanitization safety**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

- [ ] 4. Implement Markdown exporter module

  - [x] 4.1 Create `markdown_exporter.py` with core conversion functions

    - Implement `html_to_markdown` function using markdownify
    - Implement image replacement logic to use base64 data URIs
    - Implement `generate_frontmatter` for YAML metadata
    - _Requirements: 2.2, 2.3, 5.3_

  - [x] 4.2 Implement TOC generation for Markdown

    - Implement `generate_toc_markdown` for single-file mode (anchor links)
    - Implement `generate_toc_markdown` for chapter mode (file links)
    - Handle hierarchical TOC structure recursively
    - _Requirements: 2.4, 3.4_

  - [x] 4.3 Implement single-file Markdown export

    - Implement `export_single_file` function
    - Generate frontmatter with metadata
    - Generate table of contents
    - Convert and concatenate all chapters
    - Add chapter separators
    - _Requirements: 2.1, 2.3, 2.4, 2.5, 2.6, 2.7_

  - [ ]\* 4.4 Write property test for Markdown export completeness

    - **Property 1: Export completeness**
    - **Validates: Requirements 2.1, 2.6**

  - [ ]\* 4.5 Write property test for metadata preservation in Markdown

    - **Property 4: Metadata preservation**
    - **Validates: Requirements 2.3**

  - [x] 4.6 Implement chapter-split Markdown export

    - Implement `export_chapters` function
    - Create temporary directory for chapter files
    - Generate README.md with metadata and TOC
    - Convert each chapter to separate file with sanitized names
    - Create ZIP archive of all files
    - Clean up temporary directory
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ]\* 4.7 Write property test for chapter file naming

    - **Property 6: Chapter split file naming**
    - **Validates: Requirements 3.2, 8.4**

  - [ ]\* 4.8 Write property test for ZIP archive completeness
    - **Property 9: ZIP archive completeness**
    - **Validates: Requirements 3.5**

- [ ] 5. Checkpoint - Verify Markdown export functionality

  - Test single-file export with sample book
  - Test chapter-split export with sample book
  - Verify images are embedded as base64
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. Implement PDF exporter module

  - [x] 6.1 Create `pdf_exporter.py` with HTML processing functions

    - Implement `generate_title_page` for metadata display
    - Implement `combine_chapters_html` to merge all chapters
    - Implement image replacement with base64 data URIs in HTML
    - Implement `generate_pdf_css` for print styling
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 6.2 Implement PDF bookmark generation

    - Implement `create_pdf_bookmarks` function
    - Parse TOC structure recursively
    - Create hierarchical PDF bookmarks using weasyprint API
    - _Requirements: 4.5_

  - [x] 6.3 Implement main PDF export function

    - Implement `export_pdf` function
    - Generate title page HTML
    - Combine all chapters with page breaks
    - Apply CSS styling
    - Render to PDF using weasyprint
    - Add bookmarks to PDF
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [ ]\* 6.4 Write property test for PDF export completeness

    - **Property 1: Export completeness**
    - **Validates: Requirements 4.6**

  - [ ]\* 6.5 Write property test for image embedding in PDF

    - **Property 2: Image embedding consistency**
    - **Validates: Requirements 4.3, 5.5**

  - [ ]\* 6.6 Write property test for TOC structure in PDF
    - **Property 5: TOC structure preservation**
    - **Validates: Requirements 4.5**

- [ ] 7. Implement export service orchestrator

  - [x] 7.1 Create `export_service.py` with main orchestration logic

    - Implement `ExportResult` dataclass
    - Implement `ExportError`, `BookNotFoundError`, `ConversionError` exceptions
    - Implement `load_book` function to load from pickle
    - _Requirements: 7.1_

  - [x] 7.2 Implement main export function

    - Implement `export_book` function as main entry point
    - Route to appropriate exporter based on format and mode
    - Handle errors and cleanup
    - Return ExportResult with file path and metadata
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 7.2, 7.3, 7.5_

  - [ ]\* 7.3 Write property test for error recovery

    - **Property 7: Error recovery without corruption**
    - **Validates: Requirements 5.6, 7.2, 7.3, 7.4, 7.5**

  - [ ]\* 7.4 Write unit tests for export service
    - Test book loading success and failure
    - Test format routing
    - Test error handling and cleanup
    - _Requirements: 7.1, 7.5_

- [ ] 8. Checkpoint - Verify all export modules work independently

  - Test export_service with all formats
  - Verify error handling works correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Implement FastAPI export endpoints

  - [x] 9.1 Add export routes to `server.py`

    - Implement `GET /export/{book_id}/markdown` endpoint with mode parameter
    - Implement `GET /export/{book_id}/pdf` endpoint
    - Add input validation for book_id and mode
    - _Requirements: 6.1, 6.3_

  - [x] 9.2 Implement file response handling

    - Return FileResponse with appropriate MIME types
    - Set Content-Disposition headers for download
    - Handle file cleanup after sending
    - _Requirements: 6.2, 6.4, 6.7_

  - [x] 9.3 Implement error responses

    - Return 404 for invalid book_id
    - Return 500 for export failures with error details
    - Use consistent error response format
    - _Requirements: 6.5, 6.6, 7.6_

  - [ ]\* 9.4 Write integration tests for API endpoints

    - Test successful exports for all formats
    - Test error responses
    - Test file download headers
    - Verify MIME types and filenames
    - _Requirements: 6.2, 6.4, 6.7_

  - [ ]\* 9.5 Write property test for API response correctness
    - **Property 8: API response correctness**
    - **Validates: Requirements 6.2, 6.4, 6.7**

- [ ] 10. Update web interface templates

  - [x] 10.1 Add export buttons to library page

    - Update `templates/library.html`
    - Add export dropdown menu for each book
    - Add options: "Markdown (Single)", "Markdown (Chapters)", "PDF"
    - Wire buttons to export API endpoints
    - _Requirements: 1.1, 1.3_

  - [x] 10.2 Add export menu to reader page

    - Update `templates/reader.html`
    - Add export button in navigation area
    - Add dropdown with format options
    - Wire to export API endpoints
    - _Requirements: 1.2, 1.3_

  - [ ] 10.3 Add export progress feedback
    - Add loading indicator during export
    - Show success message on completion
    - Show error message on failure
    - _Requirements: 1.4, 1.5_

- [ ] 11. Final integration and testing

  - [x] 11.1 End-to-end testing with real books

    - Test export of small book (< 10 chapters)
    - Test export of medium book (10-50 chapters)
    - Test export of large book (50+ chapters)
    - Test export of book with many images
    - _Requirements: All_

  - [ ]\* 11.2 Write property test for image embedding consistency

    - **Property 2: Image embedding consistency**
    - **Validates: Requirements 2.5, 3.3, 4.3, 5.3, 5.5**

  - [ ]\* 11.3 Performance testing
    - Test export time for large books
    - Test memory usage during export
    - Verify no memory leaks
    - _Requirements: All_

- [x] 12. Final checkpoint - Complete system verification
  - Verify all export formats work from web interface
  - Verify all error cases are handled gracefully
  - Verify all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties across randomized inputs
- Unit tests validate specific examples and edge cases
- Integration tests verify end-to-end workflows
