import os
import json
from pathlib import Path

from starlette.testclient import TestClient
from starlette import status


TEST_JSON_PATH = Path(__file__).parent / "books_test.json"
os.environ["BOOKS_JSON_PATH"] = str(TEST_JSON_PATH)

from main import app


class TestBookEndpoints:
    def setup_method(self):
        if TEST_JSON_PATH.exists():
            TEST_JSON_PATH.unlink()

    def test_list_books_initial(self):
        with TestClient(app) as client:
            r = client.get("/books")
            assert r.status_code == status.HTTP_200_OK
            data = r.json()
            assert data["books"] == [{
                "id": 1,
                "title": "назва книги",
                "author": "Потужний автор"
            }]
            assert data["total"] == 1

    def test_detail_found_and_not_found(self):
        with TestClient(app) as client:
            r_ok = client.get("/books/1")
            assert r_ok.status_code == status.HTTP_200_OK
            assert r_ok.json()["title"] == "назва книги"

            r_nf = client.get("/books/999")
            assert r_nf.status_code == status.HTTP_404_NOT_FOUND

    def test_create_book(self):
        with TestClient(app) as client:
            r = client.post("/books", json={"title": "Brave New World", "author": "Aldous Huxley"})
            assert r.status_code == status.HTTP_201_CREATED
            created = r.json()
            assert created["id"] == 2
            assert created["title"] == "Brave New World"

            r_list = client.get("/books")
            assert r_list.status_code == status.HTTP_200_OK
            data = r_list.json()
            assert data["total"] == 2

    def test_update_book(self):
        with TestClient(app) as client:
            r = client.put("/books/1", json={"title": "Nineteen Eighty-Four", "author": "George Orwell"})
            assert r.status_code == status.HTTP_200_OK
            updated = r.json()
            assert updated["title"] == "Nineteen Eighty-Four"

    def test_delete_book(self):
        with TestClient(app) as client:
            r = client.delete("/books/1")
            assert r.status_code == status.HTTP_200_OK
            assert r.json()["message"] == "Book deleted"

            r_nf = client.get("/books/1")
            assert r_nf.status_code == status.HTTP_404_NOT_FOUND


class TestJsonStorage:
    def setup_method(self):
        if TEST_JSON_PATH.exists():
            TEST_JSON_PATH.unlink()

    def test_json_file_created_and_matches_list(self):
        with TestClient(app) as client:
            assert TEST_JSON_PATH.exists()
            file_data = json.loads(TEST_JSON_PATH.read_text(encoding="utf-8"))
            assert isinstance(file_data, list)

            r = client.get("/books")
            data = r.json()
            assert len(file_data) == data["total"]



def test_shutdown_called():
    with TestClient(app) as client:
        client.get("/")
    assert getattr(app.state, "shutdown_called", False) is True