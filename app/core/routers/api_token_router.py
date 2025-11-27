from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.settings.db import get_db
from app.core.models.api_token import ApiToken
from app.core.schemas.api_token_schema import (
    ApiTokenCreateSchema, ApiTokenResponseSchema, ApiTokenPartialUpdateSchema
)

router = APIRouter(prefix="/api-tokens", tags=["API Tokens"])


@router.post("/", response_model=ApiTokenResponseSchema)
def create_api_token(data: ApiTokenCreateSchema, session: Session = Depends(get_db)):
    obj = ApiToken(**data.dict())
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.get("/", response_model=list[ApiTokenResponseSchema])
def list_tokens(session: Session = Depends(get_db)):
    return session.query(ApiToken).all()


@router.get("/{obj_id}", response_model=ApiTokenResponseSchema)
def get_token(obj_id: int, session: Session = Depends(get_db)):
    obj = session.query(ApiToken).filter(ApiToken.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Token not found")
    return obj


@router.put("/{obj_id}", response_model=ApiTokenResponseSchema)
def update_token(obj_id: int, data: ApiTokenCreateSchema, session: Session = Depends(get_db)):
    obj = session.query(ApiToken).filter(ApiToken.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    for k, v in data.dict().items():
        setattr(obj, k, v)
    session.commit()
    return obj


@router.patch("/{obj_id}", response_model=ApiTokenResponseSchema)
def patch_token(obj_id: int, data: ApiTokenPartialUpdateSchema, session: Session = Depends(get_db)):
    obj = session.query(ApiToken).filter(ApiToken.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(obj, k, v)
    session.commit()
    return obj


@router.delete("/{obj_id}")
def delete_token(obj_id: int, session: Session = Depends(get_db)):
    obj = session.query(ApiToken).filter(ApiToken.id == obj_id).first()
    if not obj:
        raise HTTPException(404, "Not found")
    session.delete(obj)
    session.commit()
    return {"status": "deleted"}
