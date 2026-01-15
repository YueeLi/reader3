"""
PDF export functionality for books.

Converts book HTML content to PDF format with embedded images and bookmarks.
Preserves original layout and styling.
"""

import os
from typing import Dict
from bs4 import BeautifulSoup
from weasyprint import HTML, CSS

from reader3 import Book, BookMetadata, TOCEntry
from image_processor import ImageProcessor
from export_service import sanitize_filename, BOOKS_DIR


def generate_title_page(metadata: BookMetadata) -> str:
    """
    Generate HTML for PDF title page.
    
    Args:
        metadata: BookMetadata object
    
    Returns:
        HTML string for title page
    """
    authors = ', '.join(metadata.authors) if metadata.authors else 'Unknown Author'
    
    html = f"""
    <div class="title-page">
        <h1 class="book-title">{metadata.title}</h1>
        <p class="book-authors">{authors}</p>
    """
    
    if metadata.publisher:
        html += f'<p class="book-publisher">{metadata.publisher}</p>\n'
    
    if metadata.date:
        html += f'<p class="book-date">{metadata.date}</p>\n'
    
    if metadata.description:
        html += f'<p class="book-description">{metadata.description}</p>\n'
    
    html += "</div>\n<div class='page-break'></div>\n"
    
    return html


def combine_chapters_html(spine: list, image_processor: ImageProcessor, image_map: Dict[str, str]) -> str:
    """
    Combine all chapters into single HTML document.
    Replace image src with base64 data URIs.
    Insert page breaks between chapters.
    
    Args:
        spine: List of ChapterContent objects
        image_processor: ImageProcessor instance
        image_map: Dictionary mapping image paths to filenames
    
    Returns:
        Combined HTML string
    """
    html_parts = []
    
    for i, chapter in enumerate(spine):
        # Add chapter heading
        html_parts.append(f'<div class="chapter">\n')
        html_parts.append(f'<h2 class="chapter-title">Chapter {i + 1}</h2>\n')
        
        # Parse chapter HTML
        soup = BeautifulSoup(chapter.content, 'html.parser')
        
        # Replace image src with base64 data URIs
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if not src:
                continue
            
            # Extract filename
            filename = os.path.basename(src)
            
            # Get base64 data URI
            data_uri = image_processor.get_base64_data_uri(filename)
            
            if data_uri:
                img['src'] = data_uri
            else:
                print(f"Warning: Image not found for PDF: {filename}")
        
        # Add chapter content
        html_parts.append(str(soup))
        html_parts.append('</div>\n')
        
        # Add page break between chapters (except last)
        if i < len(spine) - 1:
            html_parts.append('<div class="page-break"></div>\n')
    
    return ''.join(html_parts)


def generate_pdf_css() -> str:
    """
    Generate CSS for PDF rendering.
    Includes page size, margins, fonts, and print-specific styles.
    
    Returns:
        CSS string
    """
    css = """
    @page {
        size: A4;
        margin: 2cm;
        
        @top-center {
            content: string(book-title);
            font-size: 10pt;
            color: #666;
        }
        
        @bottom-center {
            content: counter(page);
            font-size: 10pt;
        }
    }
    
    @page :first {
        @top-center { content: none; }
        @bottom-center { content: none; }
    }
    
    body {
        font-family: "Helvetica", "Arial", sans-serif;
        font-size: 11pt;
        line-height: 1.6;
        color: #333;
    }
    
    .title-page {
        text-align: center;
        padding-top: 30%;
    }
    
    .book-title {
        font-size: 32pt;
        font-weight: bold;
        margin-bottom: 1em;
        string-set: book-title content();
    }
    
    .book-authors {
        font-size: 18pt;
        margin-bottom: 0.5em;
    }
    
    .book-publisher,
    .book-date {
        font-size: 12pt;
        color: #666;
        margin: 0.3em 0;
    }
    
    .book-description {
        font-size: 11pt;
        margin-top: 2em;
        text-align: left;
        padding: 0 10%;
    }
    
    .page-break {
        page-break-after: always;
    }
    
    .chapter {
        margin-bottom: 2em;
    }
    
    .chapter-title {
        font-size: 20pt;
        font-weight: bold;
        margin-top: 0;
        margin-bottom: 1em;
        page-break-after: avoid;
    }
    
    h1, h2, h3, h4, h5, h6 {
        page-break-after: avoid;
        margin-top: 1.5em;
        margin-bottom: 0.5em;
    }
    
    h1 { font-size: 24pt; }
    h2 { font-size: 20pt; }
    h3 { font-size: 16pt; }
    h4 { font-size: 14pt; }
    h5 { font-size: 12pt; }
    h6 { font-size: 11pt; }
    
    p {
        margin: 0.5em 0;
        text-align: justify;
        orphans: 3;
        widows: 3;
    }
    
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 1em auto;
        page-break-inside: avoid;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 1em 0;
        page-break-inside: avoid;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 0.5em;
        text-align: left;
    }
    
    th {
        background-color: #f5f5f5;
        font-weight: bold;
    }
    
    blockquote {
        margin: 1em 2em;
        padding: 0.5em 1em;
        border-left: 3px solid #ccc;
        background-color: #f9f9f9;
    }
    
    code {
        font-family: "Courier New", monospace;
        background-color: #f5f5f5;
        padding: 0.2em 0.4em;
        border-radius: 3px;
    }
    
    pre {
        background-color: #f5f5f5;
        padding: 1em;
        overflow-x: auto;
        page-break-inside: avoid;
    }
    
    pre code {
        background-color: transparent;
        padding: 0;
    }
    
    ul, ol {
        margin: 0.5em 0;
        padding-left: 2em;
    }
    
    li {
        margin: 0.3em 0;
    }
    
    a {
        color: #0066cc;
        text-decoration: none;
    }
    """
    
    return css


def create_pdf_bookmarks(html_doc, toc: list[TOCEntry], level: int = 0):
    """
    Add hierarchical bookmarks to PDF from TOC structure.
    
    Note: WeasyPrint automatically generates bookmarks from HTML headings.
    This function is a placeholder for future custom bookmark implementation.
    
    Args:
        html_doc: WeasyPrint HTML document
        toc: List of TOCEntry objects
        level: Current bookmark level
    """
    # WeasyPrint automatically creates bookmarks from <h1>, <h2>, etc.
    # For now, we rely on the chapter headings we add in combine_chapters_html
    pass


def export_pdf(book: Book, book_id: str) -> str:
    """
    Export book as PDF with embedded images.
    
    Process:
    1. Generate title page HTML with metadata
    2. Combine all spine chapters into single HTML document
    3. Resolve and embed images as data URIs in HTML
    4. Apply CSS styling for print layout
    5. Render HTML to PDF using weasyprint
    6. Add PDF bookmarks from TOC structure
    
    Args:
        book: Book object to export
        book_id: Book folder name
    
    Returns:
        Path to generated .pdf file
    """
    # Initialize image processor
    image_processor = ImageProcessor(BOOKS_DIR, book_id)
    
    # 1. Build complete HTML document
    html_parts = []
    
    # HTML header
    html_parts.append('<!DOCTYPE html>\n<html>\n<head>\n')
    html_parts.append('<meta charset="UTF-8">\n')
    html_parts.append(f'<title>{book.metadata.title}</title>\n')
    html_parts.append('</head>\n<body>\n')
    
    # 2. Add title page
    html_parts.append(generate_title_page(book.metadata))
    
    # 3. Add all chapters
    chapters_html = combine_chapters_html(book.spine, image_processor, book.images)
    html_parts.append(chapters_html)
    
    # HTML footer
    html_parts.append('</body>\n</html>')
    
    complete_html = ''.join(html_parts)
    
    # 4. Generate CSS
    css = generate_pdf_css()
    
    # 5. Create output directory
    output_dir = os.path.join(BOOKS_DIR, book_id, 'exports')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{sanitize_filename(book.metadata.title)}.pdf")
    
    # 6. Render PDF
    html_doc = HTML(string=complete_html)
    css_doc = CSS(string=css)
    
    html_doc.write_pdf(output_file, stylesheets=[css_doc])
    
    return output_file
