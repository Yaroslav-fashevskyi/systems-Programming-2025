from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.settings.db import get_db
from app.core.models.provider import Provider
from app.core.schemas.provider_schema import (
    ProviderCreateSchema, ProviderResponseSchema, ProviderPartialUpdateSchema
)

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.post("/", response_model=ProviderResponseSchema)
def create_provider(data: ProviderCreateSchema, session: Session = Depends(get_db)):
    obj = Provider(**data.dict())
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.get("/", response_model=list[ProviderResponseSchema])
def list_providers(session: Session = Depends(get_db)):
    return session.query(Provider).all()


@router.get("/{obj_id}", response_model=ProviderResponseSchema)
def get_provider(obj_id: int, session: Session = Depends(get_db)):
    obj = session.query(Provider).filter(Provider.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Provider not found")
    return obj


@router.put("/{obj_id}", response_model=ProviderResponseSchema)
def update_provider(obj_id: int, data: ProviderCreateSchema, session: Session = Depends(get_db)):
    obj = session.query(Provider).filter(Provider.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    for k, v in data.dict().items():
        setattr(obj, k, v)
    session.commit()
    return obj


@router.patch("/{obj_id}", response_model=ProviderResponseSchema)
def patch_provider(obj_id: int, data: ProviderPartialUpdateSchema, session: Session = Depends(get_db)):
    obj = session.query(Provider).filter(Provider.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    session.commit()
    return obj


@router.delete("/{obj_id}")
def delete_provider(obj_id: int, session: Session = Depends(get_db)):
    obj = session.query(Provider).filter(Provider.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    session.delete(obj)
    session.commit()
    return {"status": "deleted"}
