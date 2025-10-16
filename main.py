from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.requests import Request
from starlette import status

from contextlib import asynccontextmanager
import json
import os
from pathlib import Path
from typing import Dict, Any

books: Dict[int, Dict[str, Any]] = {}
next_id: int = 1


def _json_path() -> Path:
    return Path(os.getenv("BOOKS_JSON_PATH", "books.json"))


def save_to_json() -> None:
    path = _json_path()
    data = list(books.values())
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_from_json() -> None:
    global books, next_id
    path = _json_path()
    if path.exists():
        try:
            raw = path.read_text(encoding="utf-8") or "[]"
            data = json.loads(raw)
            if not isinstance(data, list):
                data = []
        except json.JSONDecodeError:
            data = []
        norm: Dict[int, Dict[str, Any]] = {}
        for item in data:
            if not isinstance(item, dict):
                continue
            if not {"id", "title", "author"} <= set(item.keys()):
                continue
            try:
                _id = int(item["id"])
                title = str(item["title"])
                author = str(item["author"])
            except Exception:
                continue
            norm[_id] = {"id": _id, "title": title, "author": author}
        books = norm
        next_id = (max(books.keys()) + 1) if books else 1
    else:
        books = {
            1: {"id": 1, "title": "назва книги", "author": "Потужний автор"}
        }
        next_id = 2
        save_to_json()


def _write_shutdown_marker_if_needed(app: Starlette) -> None:
    # Маркер для тестів/ручної перевірки
    app.state.shutdown_called = True
    marker = os.getenv("SHUTDOWN_MARKER")
    if marker:
        Path(marker).write_text("shutdown-ok", encoding="utf-8")


# === ОКРЕМА ФУНКЦІЯ SHUTDOWN ===
async def graceful_shutdown(app: Starlette) -> None:
    """
    Єдине місце для всієї логіки завершення:
    - логи
    - збереження стану
    - закриття ресурсів (HTTP-клієнти, БД, тощо)
    """
    print("[shutdown] saving books.json ...")
    save_to_json()
    # приклад: якщо були асинхронні ресурси
    # await app.state.http.aclose()
    print("[shutdown] done")
    _write_shutdown_marker_if_needed(app)


@asynccontextmanager
async def lifespan(app: Starlette):
    # startup
    load_from_json()
    print("[startup] books loaded")
    try:
        yield
    finally:
        # shutdown
        await graceful_shutdown(app)


async def index(request: Request):
    return JSONResponse({"message": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaa"})


async def list_books(request: Request):
    return JSONResponse({"books": list(books.values()), "total": len(books)})


def _validate_payload(payload: dict):
    if not isinstance(payload, dict):
        return False, "Invalid JSON payload."
    title = payload.get("title")
    author = payload.get("author")
    if not isinstance(title, str) or not title.strip():
        return False, "Missing or invalid 'title'."
    if not isinstance(author, str) or not author.strip():
        return False, "Missing or invalid 'author'."
    return True, None


async def create_book(request: Request):
    global next_id
    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=status.HTTP_400_BAD_REQUEST)

    ok, err = _validate_payload(payload)
    if not ok:
        return JSONResponse({"detail": err}, status_code=status.HTTP_400_BAD_REQUEST)

    new_book = {"id": next_id, "title": payload["title"].strip(), "author": payload["author"].strip()}
    books[next_id] = new_book
    next_id += 1
    save_to_json()
    return JSONResponse(new_book, status_code=status.HTTP_201_CREATED)


async def get_book(request: Request):
    book_id = int(request.path_params["book_id"])
    book = books.get(book_id)
    if not book:
        return JSONResponse({"detail": "Book not found"}, status_code=status.HTTP_404_NOT_FOUND)
    return JSONResponse(book)


async def update_book(request: Request):
    book_id = int(request.path_params["book_id"])
    if book_id not in books:
        return JSONResponse({"detail": "Book not found"}, status_code=status.HTTP_404_NOT_FOUND)

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"detail": "Invalid JSON"}, status_code=status.HTTP_400_BAD_REQUEST)

    ok, err = _validate_payload(payload)
    if not ok:
        return JSONResponse({"detail": err}, status_code=status.HTTP_400_BAD_REQUEST)

    updated = {"id": book_id, "title": payload["title"].strip(), "author": payload["author"].strip()}
    books[book_id] = updated
    save_to_json()
    return JSONResponse(updated, status_code=status.HTTP_200_OK)


async def delete_book(request: Request):
    book_id = int(request.path_params["book_id"])
    if book_id not in books:
        return JSONResponse({"detail": "Book not found"}, status_code=status.HTTP_404_NOT_FOUND)
    del books[book_id]
    save_to_json()
    return JSONResponse({"message": "Book deleted"})


routes = [
    Route("/", index, methods=["GET"]),
    Route("/books", list_books, methods=["GET"]),
    Route("/books", create_book, methods=["POST"]),
    Route("/books/{book_id:int}", get_book, methods=["GET"]),
    Route("/books/{book_id:int}", update_book, methods=["PUT"]),
    Route("/books/{book_id:int}", delete_book, methods=["DELETE"]),
]

app = Starlette(debug=True, routes=routes, lifespan=lifespan)
