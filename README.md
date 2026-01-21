# reader 3

![reader3](reader3.png)

A lightweight, self-hosted EPUB reader that lets you read through EPUB books one chapter at a time. This makes it very easy to copy paste the contents of a chapter to an LLM, to read along. Basically - get epub books (e.g. [Project Gutenberg](https://www.gutenberg.org/) has many), open them up in this reader, copy paste text around to your favorite LLM, and read together and along.

This project was 90% vibe coded just to illustrate how one can very easily [read books together with LLMs](https://x.com/karpathy/status/1990577951671509438). I'm not going to support it in any way, it's provided here as is for other people's inspiration and I don't intend to improve it. Code is ephemeral now and libraries are over, ask your LLM to change it in whatever way you like.

## Usage

The project uses [uv](https://docs.astral.sh/uv/). So for example, download [Dracula EPUB3](https://www.gutenberg.org/ebooks/345) to this directory as `dracula.epub`, then:

```bash
uv run -m backend.cli dracula.epub
```

This creates the directory `dracula_data`, which registers the book to your local library. We can then run the server:

```bash
uv run -m backend.main
```

And visit [localhost:8123](http://localhost:8123/) to see your current Library. You can easily add more books, or delete them from your library by deleting the folder. It's not supposed to be complicated or complex.

## Project layout

- `backend/`: FastAPI app and services
- `frontend/`: reserved for the SPA (future Logto integration)
- `books/`, `epubs/`: local data directories

## Frontend (scaffold)

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_USE_MOCK=true` to use the local mock data while the API is being wired.

## Backend (API)

```bash
uv run -m backend.main
```

API endpoints:

- `GET /api/books`
- `GET /api/books/{book_id}`
- `GET /api/books/{book_id}/chapters/{chapter_index}`
- `GET /books/{book_id}/images/{image_name}`

## License

MIT
