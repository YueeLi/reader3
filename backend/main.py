import hashlib
import os
import pickle
import shutil
import tempfile
from functools import lru_cache
from typing import Optional

# Set library path for WeasyPrint on macOS
if os.uname().sysname == 'Darwin':  # macOS
    os.environ.setdefault('DYLD_LIBRARY_PATH', '/opt/homebrew/lib')

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
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


def _hash_upload_to_temp(upload_file: UploadFile, tmp_handle) -> str:
    hasher = hashlib.sha256()
    for chunk in iter(lambda: upload_file.file.read(1024 * 1024), b""):
        tmp_handle.write(chunk)
        hasher.update(chunk)
    return hasher.hexdigest()


def _find_duplicate_by_hash(file_hash: str) -> Optional[str]:
    if not os.path.exists(BOOKS_DIR):
        return None

    for item in os.listdir(BOOKS_DIR):
        item_path = os.path.join(BOOKS_DIR, item)
        if not (item.endswith("_data") and os.path.isdir(item_path)):
            continue
        hash_path = os.path.join(item_path, "source.sha256")
        if not os.path.exists(hash_path):
            continue
        try:
            with open(hash_path, "r", encoding="utf-8") as f:
                stored_hash = f.read().strip()
            if stored_hash == file_hash:
                return item
        except OSError:
            continue
    return None


def _sanitize_book_name(filename: str) -> str:
    base_name = os.path.splitext(os.path.basename(filename))[0].strip()
    if not base_name:
        return "book"
    safe_name = "".join(
        char for char in base_name if char.isalnum() or char in "._- "
    )
    safe_name = safe_name.strip().replace(" ", "_")
    return safe_name or "book"


def _resolve_unique_folder(base_name: str) -> str:
    candidate = f"{base_name}_data"
    if not os.path.exists(os.path.join(BOOKS_DIR, candidate)):
        return candidate

    suffix = 2
    while True:
        candidate = f"{base_name}_{suffix}_data"
        if not os.path.exists(os.path.join(BOOKS_DIR, candidate)):
            return candidate
        suffix += 1


def _build_spine_index(book: Book) -> dict:
    return {chapter.href: idx for idx, chapter in enumerate(book.spine)}


def _flatten_toc(entries, spine_index, depth=0):
    flattened = []
    for entry in entries:
        chapter_index = spine_index.get(entry.file_href)
        flattened.append(
            {
                "title": entry.title,
                "chapterIndex": chapter_index,
                "anchor": entry.anchor or None,
                "depth": depth,
            }
        )
        if entry.children:
            flattened.extend(_flatten_toc(entry.children, spine_index, depth + 1))
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


@app.post("/api/books/import")
async def import_book(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing EPUB filename")

    if not file.filename.lower().endswith(".epub"):
        raise HTTPException(status_code=400, detail="Only .epub files are supported")

    temp_path = None
    output_dir = None
    file_hash = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".epub") as tmp:
            temp_path = tmp.name
            file_hash = _hash_upload_to_temp(file, tmp)

        if file_hash:
            duplicate_id = _find_duplicate_by_hash(file_hash)
            if duplicate_id:
                existing_book = load_book_cached(duplicate_id)
                existing_title = (
                    existing_book.metadata.title if existing_book else duplicate_id
                )
                raise HTTPException(
                    status_code=409,
                    detail=f"Book already imported: {existing_title}",
                )

        base_name = _sanitize_book_name(file.filename)
        folder_name = _resolve_unique_folder(base_name)
        output_dir = os.path.join(BOOKS_DIR, folder_name)

        book_obj = reader3_module.process_epub(temp_path, output_dir)
        reader3_module.save_to_pickle(book_obj, output_dir)
        if file_hash:
            with open(
                os.path.join(output_dir, "source.sha256"), "w", encoding="utf-8"
            ) as f:
                f.write(file_hash)

        load_book_cached.cache_clear()

        return {
            "id": folder_name,
            "title": book_obj.metadata.title,
            "author": ", ".join(book_obj.metadata.authors),
            "chapters": len(book_obj.spine),
            "coverUrl": _find_cover_url(folder_name),
        }
    except HTTPException:
        raise
    except Exception as exc:
        if output_dir and os.path.exists(output_dir):
            shutil.rmtree(output_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Import failed: {exc}")
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
        try:
            await file.close()
        except Exception:
            pass

@app.get("/healthz", include_in_schema=False)
async def health_check():
    """Simple health endpoint."""
    return {"status": "ok"}

@app.get("/api/books/{book_id}")
async def get_book_detail(book_id: str):
    book = load_book_cached(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    spine_index = _build_spine_index(book)
    return {
        "id": book_id,
        "title": book.metadata.title,
        "author": ", ".join(book.metadata.authors),
        "chapters": len(book.spine),
        "coverUrl": _find_cover_url(book_id),
        "toc": _flatten_toc(book.toc, spine_index),
    }


@app.get("/api/books/{book_id}/chapters/{chapter_index}")
async def get_book_chapter(book_id: str, chapter_index: int):
    book = load_book_cached(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if chapter_index < 0 or chapter_index >= len(book.spine):
        raise HTTPException(status_code=404, detail="Chapter not found")

    chapter = book.spine[chapter_index]
    html = chapter.content.replace(
        'src="images/', f'src="/books/{book_id}/images/'
    ).replace(
        "src='images/", f"src='/books/{book_id}/images/"
    )
    return {
        "id": chapter.id,
        "title": chapter.title,
        "order": chapter.order,
        "html": html,
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
