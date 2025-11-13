from contextlib import asynccontextmanager
from fastapi import FastAPI

from .core.settings.db import Database
from .core.models.base import BaseModel
from .core.models import BaseModel, User, Project, ApiToken, Provider, LookupResult, IpQuery

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
db = Database(url=DATABASE_URL)

@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI):
    await db.connect()
    async with db.engine.begin() as connection:  # type: ignore[union-attr]
        await connection.run_sync(BaseModel.metadata.create_all)
    yield
    await db.disconnect()


app = FastAPI(lifespan=lifespan)

@app.get(path="/health", tags=["System"])
async def health():
    ok = await db.ping()
    return {"status": "ok" if ok else "error"}
