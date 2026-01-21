import os
import pickle
from functools import lru_cache
from typing import Optional

# Set library path for WeasyPrint on macOS
if os.uname().sysname == 'Darwin':  # macOS
    os.environ.setdefault('DYLD_LIBRARY_PATH', '/opt/homebrew/lib')

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.services import reader3 as reader3_module
from backend.app.services.reader3 import Book
from backend.app.services.export_service import export_book, BookNotFoundError, ExportError

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BOOKS_DIR = os.path.join(BASE_DIR, "books")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure books directory exists before mounting static files.
os.makedirs(BOOKS_DIR, exist_ok=True)

# Mount books directory as static files for serving cover images
app.mount("/books", StaticFiles(directory=BOOKS_DIR), name="books")

class _ReaderUnpickler(pickle.Unpickler):
    """Maps legacy pickles saved under __main__ to the reader3 module."""
    def find_class(self, module, name):
        if module in {"__main__", "reader3"} and hasattr(reader3_module, name):
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

def _find_cover_url(book_id: str) -> Optional[str]:
    images_dir = os.path.join(BOOKS_DIR, book_id, "images")
    if not os.path.exists(images_dir):
        return None

    for cover_name in ["cover.jpeg", "cover.jpg", "cover.png"]:
        potential_cover = os.path.join(images_dir, cover_name)
        if os.path.exists(potential_cover):
            return f"/books/{book_id}/images/{cover_name}"

    return None


def _flatten_toc(entries, depth=0):
    flattened = []
    for entry in entries:
        flattened.append(
            {
                "title": entry.title,
                "href": entry.href,
                "depth": depth,
            }
        )
        if entry.children:
            flattened.extend(_flatten_toc(entry.children, depth + 1))
    return flattened


@app.get("/api/books")
async def list_books():
    """Lists all available processed books."""
    books = []

    os.makedirs(BOOKS_DIR, exist_ok=True)

    if os.path.exists(BOOKS_DIR):
        for item in os.listdir(BOOKS_DIR):
            item_path = os.path.join(BOOKS_DIR, item)
            if item.endswith("_data") and os.path.isdir(item_path):
                book = load_book_cached(item)
                if book:
                    books.append(
                        {
                            "id": item,
                            "title": book.metadata.title,
                            "author": ", ".join(book.metadata.authors),
                            "chapters": len(book.spine),
                            "coverUrl": _find_cover_url(item),
                        }
                    )

    return books

@app.get("/healthz", include_in_schema=False)
async def health_check():
    """Simple health endpoint."""
    return {"status": "ok"}

@app.get("/api/books/{book_id}")
async def get_book_detail(book_id: str):
    book = load_book_cached(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return {
        "id": book_id,
        "title": book.metadata.title,
        "author": ", ".join(book.metadata.authors),
        "chapters": len(book.spine),
        "coverUrl": _find_cover_url(book_id),
        "toc": _flatten_toc(book.toc),
    }


@app.get("/api/books/{book_id}/chapters/{chapter_index}")
async def get_book_chapter(book_id: str, chapter_index: int):
    book = load_book_cached(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if chapter_index < 0 or chapter_index >= len(book.spine):
        raise HTTPException(status_code=404, detail="Chapter not found")

    chapter = book.spine[chapter_index]
    return {
        "id": chapter.id,
        "title": chapter.title,
        "order": chapter.order,
        "html": chapter.content,
    }


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
