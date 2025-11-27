from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.settings.db import get_db
from app.core.models.lookup_result import LookupResult
from app.core.schemas.lookup_result_schema import (
    LookupResultCreateSchema, LookupResultResponseSchema, LookupResultPartialUpdateSchema
)

router = APIRouter(prefix="/lookup-results", tags=["Lookup Results"])


@router.post("/", response_model=LookupResultResponseSchema)
def create_lookup_result(data: LookupResultCreateSchema, session: Session = Depends(get_db)):
    obj = LookupResult(**data.dict())
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.get("/", response_model=list[LookupResultResponseSchema])
def list_lookup_results(session: Session = Depends(get_db)):
    return session.query(LookupResult).all()


@router.get("/{obj_id}", response_model=LookupResultResponseSchema)
def get_lookup_result(obj_id: int, session: Session = Depends(get_db)):
    obj = session.query(LookupResult).filter(LookupResult.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    return obj


@router.put("/{obj_id}", response_model=LookupResultResponseSchema)
def update_lookup_result(obj_id: int, data: LookupResultCreateSchema, session: Session = Depends(get_db)):
    obj = session.query(LookupResult).filter(LookupResult.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    for k, v in data.dict().items():
        setattr(obj, k, v)
    session.commit()
    return obj


@router.patch("/{obj_id}", response_model=LookupResultResponseSchema)
def patch_lookup_result(obj_id: int, data: LookupResultPartialUpdateSchema, session: Session = Depends(get_db)):
    obj = session.query(LookupResult).filter(LookupResult.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    session.commit()
    return obj


@router.delete("/{obj_id}")
def delete_lookup_result(obj_id: int, session: Session = Depends(get_db)):
    obj = session.query(LookupResult).filter(LookupResult.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    session.delete(obj)
    session.commit()
    return {"status": "deleted"}
