import os
import json
from pathlib import Path
from typing import Dict, Any, List

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette import status

# ===== Глобальне "сховище" =====
BOOKS: Dict[int, Dict[str, Any]] = {}
NEXT_ID: int = 1

# Шлях до JSON (можна переозначити через env)
BOOKS_FILE = os.getenv("BOOKS_FILE", "data/books.json")
FILE_PATH = Path(BOOKS_FILE)

# ===== Хелпери =====
def _serialize_books() -> List[Dict[str, Any]]:
    return sorted(BOOKS.values(), key=lambda b: b["id"])

def _save_to_json() -> None:
    FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {"next_id": NEXT_ID, "books": _serialize_books()}
    FILE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def _load_from_json() -> bool:
    global BOOKS, NEXT_ID
    if FILE_PATH.exists():
        data = json.loads(FILE_PATH.read_text(encoding="utf-8"))
        NEXT_ID = int(data.get("next_id", 1))
        books_list = data.get("books", [])
        BOOKS = {int(b["id"]): {"id": int(b["id"]), "title": b["title"], "author": b["author"]} for b in books_list}
        if books_list:
            NEXT_ID = max(int(b["id"]) for b in books_list) + 1
        return True
    return False

# ===== Життєвий цикл =====
async def startup() -> None:
    loaded = _load_from_json()
    if not loaded:
        global BOOKS, NEXT_ID
        BOOKS = {1: {"id": 1, "title": "1984", "author": "George Orwell"}}
        NEXT_ID = 2
        _save_to_json()

async def shutdown() -> None:
    _save_to_json()

# ===== Валідація =====
def _validate_book_payload(data: Dict[str, Any]) -> str | None:
    if not isinstance(data, dict):
        return "Invalid JSON."
    if "title" not in data or "author" not in data:
        return "Fields 'title' and 'author' are required."
    if not isinstance(data["title"], str) or not isinstance(data["author"], str):
        return "'title' and 'author' must be strings."
    if not data["title"].strip() or not data["author"].strip():
        return "'title' and 'author' cannot be empty."
    return None

# ===== Ендпойнти =====
async def list_books(request: Request) -> JSONResponse:
    return JSONResponse({"books": _serialize_books(), "total": len(BOOKS)}, status_code=status.HTTP_200_OK)

async def detail_book(request: Request) -> JSONResponse:
    book_id = int(request.path_params["book_id"])
    book = BOOKS.get(book_id)
    if not book:
        return JSONResponse({"detail": "Book not found"}, status_code=status.HTTP_404_NOT_FOUND)
    return JSONResponse(book, status_code=status.HTTP_200_OK)

async def create_book(request: Request) -> JSONResponse:
    data = await request.json()
    err = _validate_book_payload(data)
    if err:
        return JSONResponse({"detail": err}, status_code=status.HTTP_400_BAD_REQUEST)
    global NEXT_ID
    new_id = NEXT_ID
    book = {"id": new_id, "title": data["title"].strip(), "author": data["author"].strip()}
    BOOKS[new_id] = book
    NEXT_ID += 1
    _save_to_json()
    return JSONResponse(book, status_code=status.HTTP_201_CREATED)

async def update_book(request: Request) -> JSONResponse:
    book_id = int(request.path_params["book_id"])
    if book_id not in BOOKS:
        return JSONResponse({"detail": "Book not found"}, status_code=status.HTTP_404_NOT_FOUND)
    data = await request.json()
    err = _validate_book_payload(data)
    if err:
        return JSONResponse({"detail": err}, status_code=status.HTTP_400_BAD_REQUEST)
    BOOKS[book_id]["title"] = data["title"].strip()
    BOOKS[book_id]["author"] = data["author"].strip()
    _save_to_json()
    return JSONResponse(BOOKS[book_id], status_code=status.HTTP_200_OK)

async def delete_book(request: Request) -> JSONResponse:
    book_id = int(request.path_params["book_id"])
    if book_id not in BOOKS:
        return JSONResponse({"detail": "Book not found"}, status_code=status.HTTP_404_NOT_FOUND)
    del BOOKS[book_id]
    _save_to_json()
    return JSONResponse({"message": "Book deleted"}, status_code=status.HTTP_200_OK)

routes = [
    Route("/books", list_books, methods=["GET"]),
    Route("/books", create_book, methods=["POST"]),
    Route("/books/{book_id:int}", detail_book, methods=["GET"]),
    Route("/books/{book_id:int}", update_book, methods=["PUT"]),
    Route("/books/{book_id:int}", delete_book, methods=["DELETE"]),
]

app = Starlette(
    debug=True,
    routes=routes,
    on_startup=[startup],
    on_shutdown=[shutdown],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
