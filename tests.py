import json
from pathlib import Path

import main  # для monkeypatch глобалок
from main import app
from starlette.testclient import TestClient
from starlette import status


def _use_temp_file(monkeypatch, tmp_path: Path) -> Path:
    """
    Перекидаємо шлях збереження JSON у тимчасову папку та скидаємо памʼять.
    """
    temp_file = tmp_path / "books.json"
    monkeypatch.setattr(main, "FILE_PATH", temp_file, raising=False)
    main.BOOKS.clear()
    main.NEXT_ID = 1
    return temp_file


class TestBookEndpoints:
    def test_list_books(self, monkeypatch, tmp_path):
        _use_temp_file(monkeypatch, tmp_path)
        with TestClient(app) as client:
            r = client.get("/books")
            assert r.status_code == status.HTTP_200_OK
            data = r.json()
            assert data["books"] == [{"id": 1, "title": "1984", "author": "George Orwell"}]
            assert data["total"] == 1

    def test_detail_not_found(self, monkeypatch, tmp_path):
        _use_temp_file(monkeypatch, tmp_path)
        with TestClient(app) as client:
            r = client.get("/books/999")
            assert r.status_code == status.HTTP_404_NOT_FOUND

    def test_create_book_and_persist(self, monkeypatch, tmp_path):
        path = _use_temp_file(monkeypatch, tmp_path)
        with TestClient(app) as client:
            r = client.post("/books", json={"title": "Sapiens", "author": "Yuval Noah Harari"})
            assert r.status_code == status.HTTP_201_CREATED
            created = r.json()
            assert created["id"] == 2
            assert created["title"] == "Sapiens"
            assert created["author"] == "Yuval Noah Harari"

            # Перевіряємо, що JSON реально зберігся
            assert path.exists()
            file_data = json.loads(path.read_text(encoding="utf-8"))
            assert any(b["title"] == "Sapiens" for b in file_data["books"])

    def test_create_validation_errors(self, monkeypatch, tmp_path):
        _use_temp_file(monkeypatch, tmp_path)
        with TestClient(app) as client:
            r = client.post("/books", json={"title": "No author"})
            assert r.status_code == status.HTTP_400_BAD_REQUEST

            r = client.post("/books", json={"title": " ", "author": "X"})
            assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_flow(self, monkeypatch, tmp_path):
        _use_temp_file(monkeypatch, tmp_path)
        with TestClient(app) as client:
            # Створюємо нову
            r = client.post("/books", json={"title": "Old", "author": "Anon"})
            assert r.status_code == status.HTTP_201_CREATED
            bid = r.json()["id"]

            # Оновлюємо
            r = client.put(f"/books/{bid}", json={"title": "New Title", "author": "New Author"})
            assert r.status_code == status.HTTP_200_OK
            updated = r.json()
            assert updated["title"] == "New Title"
            assert updated["author"] == "New Author"

            # 404 для неіснуючого id
            r = client.put("/books/999", json={"title": "X", "author": "Y"})
            assert r.status_code == status.HTTP_404_NOT_FOUND

            # Перевірка валідатора
            r = client.put(f"/books/{bid}", json={"title": "Only title"})
            assert r.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_flow(self, monkeypatch, tmp_path):
        _use_temp_file(monkeypatch, tmp_path)
        with TestClient(app) as client:
            # Додаємо ще одну
            r = client.post("/books", json={"title": "To be deleted", "author": "Anon"})
            assert r.status_code == status.HTTP_201_CREATED
            bid = r.json()["id"]

            # Видаляємо
            r = client.delete(f"/books/{bid}")
            assert r.status_code == status.HTTP_200_OK
            assert r.json()["message"] == "Book deleted"

            # Після видалення — 404
            r = client.get(f"/books/{bid}")
            assert r.status_code == status.HTTP_404_NOT_FOUND

            # Delete 404 для неіснуючого
            r = client.delete("/books/999")
            assert r.status_code == status.HTTP_404_NOT_FOUND
