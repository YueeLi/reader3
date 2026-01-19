import os
import pickle
from functools import lru_cache
from typing import Optional

# Set library path for WeasyPrint on macOS
if os.uname().sysname == 'Darwin':  # macOS
    os.environ.setdefault('DYLD_LIBRARY_PATH', '/opt/homebrew/lib')

from fastapi import FastAPI, Request, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import reader3 as reader3_module
from reader3 import Book, BookMetadata, ChapterContent, TOCEntry
from export_service import export_book, BookNotFoundError, ExportError

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Mount books directory as static files for serving cover images
app.mount("/books", StaticFiles(directory="books"), name="books")

# Where are the book folders located?
BOOKS_DIR = "books"

class _ReaderUnpickler(pickle.Unpickler):
    """Maps legacy pickles saved under __main__ to the reader3 module."""
    def find_class(self, module, name):
        if module == "__main__" and hasattr(reader3_module, name):
            return getattr(reader3_module, name)
        return super().find_class(module, name)


@lru_cache(maxsize=10)
def load_book_cached(folder_name: str) -> Optional[Book]:
    """
    Loads the book from the pickle file.
    Cached so we don't re-read the disk on every click.
    """
    file_path = os.path.join(BOOKS_DIR, folder_name, "book.pkl")
    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, "rb") as f:
            book = _ReaderUnpickler(f).load()
        return book
    except Exception as e:
        print(f"Error loading book {folder_name}: {e}")
        return None

@app.get("/", response_class=HTMLResponse)
async def library_view(request: Request):
    """Lists all available processed books."""
    books = []

    # 确保 books 目录存在
    os.makedirs(BOOKS_DIR, exist_ok=True)
    
    # Scan directory for folders ending in '_data' that have a book.pkl
    if os.path.exists(BOOKS_DIR):
        for item in os.listdir(BOOKS_DIR):
            item_path = os.path.join(BOOKS_DIR, item)
            if item.endswith("_data") and os.path.isdir(item_path):
                # Try to load it to get the title
                book = load_book_cached(item)
                if book:
                    # Check for cover image
                    cover_path = None
                    images_dir = os.path.join(item_path, "images")
                    if os.path.exists(images_dir):
                        # Look for cover.jpeg or cover.jpg
                        for cover_name in ["cover.jpeg", "cover.jpg", "cover.png"]:
                            potential_cover = os.path.join(images_dir, cover_name)
                            if os.path.exists(potential_cover):
                                cover_path = f"/books/{item}/images/{cover_name}"
                                break
                    
                    books.append({
                        "id": item,
                        "title": book.metadata.title,
                        "author": ", ".join(book.metadata.authors),
                        "chapters": len(book.spine),
                        "cover_path": cover_path
                    })

    return templates.TemplateResponse("library.html", {"request": request, "books": books})

@app.head("/", include_in_schema=False)
async def library_view_head():
    """Health/HEAD check for load balancers."""
    return Response(status_code=200)

@app.get("/healthz", include_in_schema=False)
async def health_check():
    """Simple health endpoint."""
    return {"status": "ok"}

@app.get("/read/{book_id}", response_class=HTMLResponse)
async def redirect_to_first_chapter(request: Request, book_id: str):
    """Helper to just go to chapter 0."""
    return await read_chapter(request=request, book_id=book_id, chapter_index=0)

@app.get("/read/{book_id}/images/{image_name}")
async def serve_image(book_id: str, image_name: str):
    """
    Serves images specifically for a book.
    The HTML contains <img src="images/pic.jpg">.
    The browser resolves this to /read/{book_id}/images/pic.jpg.
    """
    # Security check: ensure book_id is clean
    safe_book_id = os.path.basename(book_id)
    safe_image_name = os.path.basename(image_name)

    img_path = os.path.join(BOOKS_DIR, safe_book_id, "images", safe_image_name)

    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(img_path)

@app.get("/read/{book_id}/{chapter_index}", response_class=HTMLResponse)
async def read_chapter(request: Request, book_id: str, chapter_index: int):
    """The main reader interface."""
    book = load_book_cached(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if chapter_index < 0 or chapter_index >= len(book.spine):
        raise HTTPException(status_code=404, detail="Chapter not found")

    current_chapter = book.spine[chapter_index]

    # Calculate Prev/Next links
    prev_idx = chapter_index - 1 if chapter_index > 0 else None
    next_idx = chapter_index + 1 if chapter_index < len(book.spine) - 1 else None

    return templates.TemplateResponse("reader.html", {
        "request": request,
        "book": book,
        "current_chapter": current_chapter,
        "chapter_index": chapter_index,
        "book_id": book_id,
        "prev_idx": prev_idx,
        "next_idx": next_idx
    })


@app.get("/export/{book_id}/markdown")
async def export_markdown(
    book_id: str,
    mode: str = Query("single", pattern="^(single|chapters)$")
):
    """
    Export book as Markdown.
    
    Query Parameters:
        mode: 'single' for single file, 'chapters' for ZIP archive
    
    Returns:
        FileResponse with .md or .zip file
    """
    try:
        result = export_book(book_id, format='markdown', mode=mode)
        
        # Encode filename for Content-Disposition header
        from urllib.parse import quote
        encoded_filename = quote(result.filename)
        
        return FileResponse(
            path=result.file_path,
            media_type=result.mime_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    
    except BookNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except ExportError as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.get("/export/{book_id}/pdf")
async def export_pdf_endpoint(book_id: str):
    """
    Export book as PDF.
    
    Returns:
        FileResponse with .pdf file
    """
    try:
        result = export_book(book_id, format='pdf')
        
        # Encode filename for Content-Disposition header
        from urllib.parse import quote
        encoded_filename = quote(result.filename)
        
        return FileResponse(
            path=result.file_path,
            media_type=result.mime_type,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )
    
    except BookNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except ExportError as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting server at http://127.0.0.1:8123")
    uvicorn.run(app, host="127.0.0.1", port=8123)
