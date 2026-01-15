# Requirements Document

## Introduction

This document specifies the requirements for adding export functionality to the EPUB reader application. The feature enables users to export processed books into Markdown and PDF formats through a web interface, with support for different export modes and embedded images.

## Glossary

- **Book**: A processed EPUB file stored as a structured Book object containing metadata, spine (chapters), TOC, and images
- **Export_System**: The system component responsible for converting Book objects into Markdown or PDF formats
- **Spine**: The linear reading order of chapter content files in a Book
- **TOC**: Table of Contents - the hierarchical navigation structure of a Book
- **Web_Interface**: The FastAPI-based web application that serves the reader UI
- **Single_File_Mode**: Export mode where the entire book is combined into one output file
- **Chapter_Split_Mode**: Export mode where each chapter becomes a separate file
- **Base64_Embedding**: Technique for encoding binary image data as text within the output file

## Requirements

### Requirement 1: Web-Based Export Triggering

**User Story:** As a reader, I want to export books from the web interface, so that I can access my books in different formats without using command-line tools.

#### Acceptance Criteria

1. WHEN a user views the library page, THE Web_Interface SHALL display an export button for each book
2. WHEN a user views a book in the reader, THE Web_Interface SHALL display export options in the navigation area
3. WHEN a user clicks an export button, THE Web_Interface SHALL present format options (Markdown single-file, Markdown chapters, PDF)
4. WHEN a user selects an export format, THE Export_System SHALL initiate the export process and provide download capability
5. WHEN an export is in progress, THE Web_Interface SHALL display progress feedback to the user

### Requirement 2: Markdown Single-File Export

**User Story:** As a reader, I want to export a book as a single Markdown file, so that I can read or edit the entire book in any Markdown editor.

#### Acceptance Criteria

1. WHEN a user requests single-file Markdown export, THE Export_System SHALL convert all spine chapters to Markdown format
2. WHEN converting HTML to Markdown, THE Export_System SHALL preserve text formatting including headings, lists, emphasis, and links
3. WHEN processing the book, THE Export_System SHALL include metadata as YAML frontmatter at the beginning of the file
4. WHEN processing the TOC, THE Export_System SHALL generate a Markdown table of contents with links to chapter sections
5. WHEN encountering images, THE Export_System SHALL convert them to base64-encoded data URIs embedded in the Markdown
6. WHEN all chapters are processed, THE Export_System SHALL concatenate them in spine order with clear chapter separators
7. WHEN the export completes, THE Export_System SHALL provide the file for download with filename format: `{book_title}_single.md`

### Requirement 3: Markdown Chapter-Split Export

**User Story:** As a reader, I want to export a book as separate Markdown files per chapter, so that I can work with individual chapters independently.

#### Acceptance Criteria

1. WHEN a user requests chapter-split Markdown export, THE Export_System SHALL create one Markdown file per spine chapter
2. WHEN creating chapter files, THE Export*System SHALL name them using the pattern: `{order}*{chapter_title}.md`
3. WHEN processing each chapter, THE Export_System SHALL convert HTML to Markdown with base64-embedded images
4. WHEN processing the book, THE Export_System SHALL create a main `README.md` file containing metadata and TOC with links to chapter files
5. WHEN all files are created, THE Export_System SHALL package them into a ZIP archive
6. WHEN the export completes, THE Export_System SHALL provide the ZIP file for download with filename format: `{book_title}_chapters.zip`

### Requirement 4: PDF Export with Original Layout

**User Story:** As a reader, I want to export a book as a PDF file, so that I can read it on any device with preserved formatting.

#### Acceptance Criteria

1. WHEN a user requests PDF export, THE Export_System SHALL convert the book using HTML-to-PDF rendering
2. WHEN rendering HTML, THE Export_System SHALL preserve the original layout, styles, and formatting from the spine chapters
3. WHEN processing images, THE Export_System SHALL embed image data directly into the PDF document
4. WHEN generating the PDF, THE Export_System SHALL include a title page with book metadata (title, authors, publisher, date)
5. WHEN processing the TOC, THE Export_System SHALL generate PDF bookmarks matching the hierarchical TOC structure
6. WHEN rendering chapters, THE Export_System SHALL maintain spine order and insert page breaks between chapters
7. WHEN the export completes, THE Export_System SHALL provide the PDF file for download with filename format: `{book_title}.pdf`

### Requirement 5: Image Processing and Embedding

**User Story:** As a reader, I want exported files to be self-contained with embedded images, so that I don't need to manage separate image folders.

#### Acceptance Criteria

1. WHEN processing images for Markdown export, THE Export_System SHALL read image files from the book's images directory
2. WHEN encoding images, THE Export_System SHALL convert image binary data to base64 format
3. WHEN embedding in Markdown, THE Export_System SHALL use the data URI scheme: `![alt](data:image/{type};base64,{data})`
4. WHEN processing images for PDF export, THE Export_System SHALL resolve image paths from the HTML content
5. WHEN rendering PDF, THE Export_System SHALL embed images directly into the PDF document structure
6. IF an image file is missing, THEN THE Export_System SHALL log a warning and continue processing without failing

### Requirement 6: Export API Endpoints

**User Story:** As a developer, I want RESTful API endpoints for export functionality, so that the web interface can trigger exports programmatically.

#### Acceptance Criteria

1. THE Web_Interface SHALL provide endpoint `GET /export/{book_id}/markdown` accepting query parameter `mode` with values `single` or `chapters`
2. WHEN the markdown endpoint receives a valid request, THE Export_System SHALL return the appropriate file or ZIP archive
3. THE Web_Interface SHALL provide endpoint `GET /export/{book_id}/pdf` for PDF export
4. WHEN the PDF endpoint receives a valid request, THE Export_System SHALL return a PDF file with appropriate content-type headers
5. IF a book_id does not exist, THEN THE Web_Interface SHALL return HTTP 404 with error message
6. IF an export process fails, THEN THE Web_Interface SHALL return HTTP 500 with error details
7. WHEN returning files, THE Web_Interface SHALL set appropriate Content-Disposition headers for browser download

### Requirement 7: Error Handling and Validation

**User Story:** As a user, I want clear error messages when exports fail, so that I understand what went wrong and can take corrective action.

#### Acceptance Criteria

1. IF a book cannot be loaded from pickle, THEN THE Export_System SHALL return an error message indicating the book is unavailable
2. IF HTML-to-Markdown conversion fails for a chapter, THEN THE Export_System SHALL log the error and skip that chapter with a placeholder
3. IF PDF rendering fails, THEN THE Export_System SHALL return an error message with details about the rendering failure
4. IF image encoding fails, THEN THE Export_System SHALL log a warning and continue without that image
5. WHEN any error occurs, THE Export_System SHALL ensure partial files are cleaned up and not left on disk
6. WHEN validation fails, THE Web_Interface SHALL display user-friendly error messages in the UI

### Requirement 8: File Naming and Sanitization

**User Story:** As a user, I want exported files to have clean, valid filenames, so that they work across different operating systems.

#### Acceptance Criteria

1. WHEN generating filenames, THE Export_System SHALL sanitize book titles by removing invalid filesystem characters
2. WHEN sanitizing, THE Export_System SHALL replace spaces with underscores and remove characters: `/ \ : * ? " < > |`
3. WHEN a sanitized filename is empty, THE Export_System SHALL use a fallback name: `book_export`
4. WHEN generating chapter filenames, THE Export_System SHALL limit filename length to 200 characters
5. THE Export_System SHALL ensure all generated filenames are valid UTF-8 strings
