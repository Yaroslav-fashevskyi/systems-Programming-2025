from contextlib import asynccontextmanager
from fastapi import FastAPI

# 1) Підключаємо Database і BaseModel
from .core.settings.db import Database
from .core.models.base import BaseModel
from .core.models import BaseModel, User, Project, ApiToken, Provider, LookupResult, IpQuery

# 2) URL до SQLite (файл test.db у корені проєкту)
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
db = Database(url=DATABASE_URL)

# 3) Lifespan: підключення до БД та створення таблиць
@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI):
    await db.connect()
    async with db.engine.begin() as connection:  # type: ignore[union-attr]
        await connection.run_sync(BaseModel.metadata.create_all)
    yield
    await db.disconnect()

# 4) FastAPI app із lifespan
app = FastAPI(lifespan=lifespan)

# 5) Health endpoint
@app.get(path="/health", tags=["System"])
async def health():
    ok = await db.ping()
    return {"status": "ok" if ok else "error"}
