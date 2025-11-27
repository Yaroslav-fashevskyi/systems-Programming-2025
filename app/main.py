from fastapi import FastAPI

from app.core.settings.db import Base, engine

# Імпортуємо моделі, щоб SQLAlchemy бачив таблиці
from app.core.models import user, project, provider, api_token, ip_query, lookup_result

# Роутери
from app.core.routers.user_router import router as user_router
from app.core.routers.project_router import router as project_router
from app.core.routers.provider_router import router as provider_router
from app.core.routers.api_token_router import router as api_token_router
from app.core.routers.ip_query_router import router as ip_query_router
from app.core.routers.lookup_result_router import router as lookup_result_router

# Створення таблиць
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Підключення роутерів
app.include_router(user_router)
app.include_router(project_router)
app.include_router(provider_router)
app.include_router(api_token_router)
app.include_router(ip_query_router)
app.include_router(lookup_result_router)


@app.get("/health")
def health():
    return {"status": "ok"}
