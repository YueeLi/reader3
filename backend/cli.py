"""CLI entrypoint for processing EPUB files."""

import os
import sys

from backend.app.services.reader3 import process_epub, save_to_pickle

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python -m backend.cli <file.epub>")
        sys.exit(1)

    epub_file = sys.argv[1]
    if not os.path.exists(epub_file):
        raise FileNotFoundError("File not found.")

    books_base_dir = os.path.join(BASE_DIR, "books")
    os.makedirs(books_base_dir, exist_ok=True)

    book_name = os.path.splitext(os.path.basename(epub_file))[0]
    out_dir = os.path.join(books_base_dir, book_name + "_data")

    book_obj = process_epub(epub_file, out_dir)
    save_to_pickle(book_obj, out_dir)
    print("\n--- Summary ---")
    print(f"Title: {book_obj.metadata.title}")
    print(f"Authors: {', '.join(book_obj.metadata.authors)}")
    print(f"Physical Files (Spine): {len(book_obj.spine)}")
    print(f"TOC Root Items: {len(book_obj.toc)}")
    print(f"Images extracted: {len(book_obj.images)}")


if __name__ == "__main__":
    main()
