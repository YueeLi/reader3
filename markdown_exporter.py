"""
Markdown export functionality for books.

Converts book HTML content to Markdown format with embedded images.
Supports both single-file and chapter-split export modes.
"""

import os
import re
import tempfile
import zipfile
from typing import Dict
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import yaml

from reader3 import Book, BookMetadata, TOCEntry
from image_processor import ImageProcessor
from export_service import sanitize_filename, BOOKS_DIR


def generate_frontmatter(metadata: BookMetadata) -> str:
    """
    Generate YAML frontmatter from book metadata.
    
    Args:
        metadata: BookMetadata object
    
    Returns:
        YAML frontmatter string with --- delimiters
    """
    frontmatter_data = {
        'title': metadata.title,
        'authors': metadata.authors,
        'language': metadata.language,
    }
    
    # Add optional fields if present
    if metadata.publisher:
        frontmatter_data['publisher'] = metadata.publisher
    if metadata.date:
        frontmatter_data['date'] = metadata.date
    if metadata.description:
        frontmatter_data['description'] = metadata.description
    
    # Convert to YAML
    yaml_str = yaml.dump(frontmatter_data, allow_unicode=True, sort_keys=False)
    
    return f"---\n{yaml_str}---\n\n"


def html_to_markdown(html: str, image_processor: ImageProcessor, image_map: Dict[str, str]) -> str:
    """
    Convert HTML content to Markdown with embedded images.
    
    Args:
        html: HTML content string
        image_processor: ImageProcessor instance for encoding images
        image_map: Dictionary mapping image paths to filenames
    
    Returns:
        Markdown string with base64-embedded images
    """
    # Parse HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Replace image src with base64 data URIs
    for img in soup.find_all('img'):
        src = img.get('src', '')
        if not src:
            continue
        
        # Extract filename from src (e.g., 'images/pic.jpg' -> 'pic.jpg')
        filename = os.path.basename(src)
        
        # Get base64 data URI
        data_uri = image_processor.get_base64_data_uri(filename)
        
        if data_uri:
            img['src'] = data_uri
        else:
            # If image not found, keep original src or remove
            print(f"Warning: Image not found: {filename}")
    
    # Convert to Markdown
    markdown = md(str(soup), heading_style="ATX")
    
    return markdown


def export_single_file(book: Book, book_id: str) -> str:
    """
    Export entire book as single Markdown file.
    
    Process:
    1. Generate YAML frontmatter with metadata
    2. Generate table of contents with anchor links
    3. Convert each spine chapter to Markdown
    4. Embed images as base64 data URIs
    5. Concatenate with chapter separators
    
    Args:
        book: Book object to export
        book_id: Book folder name
    
    Returns:
        Path to generated .md file
    """
    # Initialize image processor
    image_processor = ImageProcessor(BOOKS_DIR, book_id)
    
    # Build output
    output = []
    
    # 1. Add frontmatter
    output.append(generate_frontmatter(book.metadata))
    
    # 2. Add title
    output.append(f"# {book.metadata.title}\n\n")
    
    # 3. Add table of contents
    output.append("## Table of Contents\n\n")
    toc_md = generate_toc_markdown(book.toc, mode='single')
    output.append(toc_md)
    output.append("\n---\n\n")
    
    # 4. Convert each chapter
    for i, chapter in enumerate(book.spine):
        # Add chapter heading with anchor
        chapter_anchor = f"chapter-{i}"
        output.append(f'<a id="{chapter_anchor}"></a>\n\n')
        output.append(f"## Chapter {i + 1}\n\n")
        
        # Convert HTML to Markdown
        markdown_content = html_to_markdown(chapter.content, image_processor, book.images)
        output.append(markdown_content)
        
        # Add separator between chapters
        if i < len(book.spine) - 1:
            output.append("\n\n---\n\n")
    
    # 5. Write to file
    output_dir = os.path.join(BOOKS_DIR, book_id, 'exports')
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{sanitize_filename(book.metadata.title)}_single.md")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(''.join(output))
    
    return output_file


def generate_toc_markdown(toc: list[TOCEntry], mode: str, level: int = 0) -> str:
    """
    Generate Markdown table of contents.
    
    Args:
        toc: List of TOCEntry objects
        mode: 'single' for anchor links, 'chapters' for file links
        level: Current indentation level
    
    Returns:
        Markdown TOC string
    """
    lines = []
    indent = "  " * level
    
    for i, entry in enumerate(toc):
        if mode == 'single':
            # Link to anchor in same file
            link = f"[{entry.title}](#chapter-{i})"
        else:
            # Link to separate file
            filename = f"{i:02d}_{sanitize_filename(entry.title)}.md"
            link = f"[{entry.title}]({filename})"
        
        lines.append(f"{indent}- {link}\n")
        
        # Recursively add children
        if entry.children:
            child_toc = generate_toc_markdown(entry.children, mode, level + 1)
            lines.append(child_toc)
    
    return ''.join(lines)


def export_chapters(book: Book, book_id: str) -> str:
    """
    Export book as multiple Markdown files in ZIP archive.
    
    Process:
    1. Create temporary directory
    2. Generate README.md with metadata and TOC
    3. Convert each chapter to separate .md file
    4. Embed images in each file
    5. Create ZIP archive
    6. Clean up temporary directory
    
    Args:
        book: Book object to export
        book_id: Book folder name
    
    Returns:
        Path to generated .zip file
    """
    # Initialize image processor
    image_processor = ImageProcessor(BOOKS_DIR, book_id)
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Generate README.md
        readme_content = []
        readme_content.append(generate_frontmatter(book.metadata))
        readme_content.append(f"# {book.metadata.title}\n\n")
        readme_content.append("## Table of Contents\n\n")
        readme_content.append(generate_toc_markdown(book.toc, mode='chapters'))
        
        readme_path = os.path.join(temp_dir, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(''.join(readme_content))
        
        # 2. Generate chapter files
        for i, chapter in enumerate(book.spine):
            # Create filename
            chapter_title = chapter.title if chapter.title else f"Chapter_{i+1}"
            filename = f"{i:02d}_{sanitize_filename(chapter_title)}.md"
            filepath = os.path.join(temp_dir, filename)
            
            # Convert chapter to Markdown
            chapter_content = []
            chapter_content.append(f"# {chapter_title}\n\n")
            markdown_content = html_to_markdown(chapter.content, image_processor, book.images)
            chapter_content.append(markdown_content)
            
            # Write chapter file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(''.join(chapter_content))
        
        # 3. Create ZIP archive
        output_dir = os.path.join(BOOKS_DIR, book_id, 'exports')
        os.makedirs(output_dir, exist_ok=True)
        
        zip_filename = f"{sanitize_filename(book.metadata.title)}_chapters.zip"
        zip_path = os.path.join(output_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from temp directory
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        return zip_path
