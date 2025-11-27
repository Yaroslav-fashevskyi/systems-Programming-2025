from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.settings.db import get_db
from app.core.models.ip_query import IpQuery
from app.core.schemas.ip_query_schema import (
    IPQueryCreateSchema, IPQueryResponseSchema, IPQueryPartialUpdateSchema
)

router = APIRouter(prefix="/ip-queries", tags=["IP Queries"])


@router.post("/", response_model=IPQueryResponseSchema)
def create_ip_query(data: IPQueryCreateSchema, session: Session = Depends(get_db)):
    obj = IPQuery(**data.dict())
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.get("/", response_model=list[IPQueryResponseSchema])
def list_ip_queries(session: Session = Depends(get_db)):
    return session.query(IPQuery).all()


@router.get("/{obj_id}", response_model=IPQueryResponseSchema)
def get_ip_query(obj_id: int, session: Session = Depends(get_db)):
    obj = session.query(IPQuery).filter(IPQuery.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Query not found")
    return obj


@router.put("/{obj_id}", response_model=IPQueryResponseSchema)
def update_ip_query(obj_id: int, data: IPQueryCreateSchema, session: Session = Depends(get_db)):
    obj = session.query(IPQuery).filter(IPQuery.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    for k, v in data.dict().items():
        setattr(obj, k, v)
    session.commit()
    return obj


@router.patch("/{obj_id}", response_model=IPQueryResponseSchema)
def patch_ip_query(obj_id: int, data: IPQueryPartialUpdateSchema, session: Session = Depends(get_db)):
    obj = session.query(IPQuery).filter(IPQuery.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    session.commit()
    return obj


@router.delete("/{obj_id}")
def delete_ip_query(obj_id: int, session: Session = Depends(get_db)):
    obj = session.query(IPQuery).filter(IPQuery.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    session.delete(obj)
    session.commit()
    return {"status": "deleted"}
