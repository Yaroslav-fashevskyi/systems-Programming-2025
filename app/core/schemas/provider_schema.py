from pydantic import BaseModel, Field
from typing import Optional


class ProviderCreateSchema(BaseModel):
    name: str = Field(max_length=255)
    url: Optional[str] = None


class ProviderResponseSchema(BaseModel):
    id: int
    name: str
    url: Optional[str]

    class Config:
        orm_mode = True


class ProviderPartialUpdateSchema(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
