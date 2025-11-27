from pydantic import BaseModel, Field
from typing import Optional


class IPQueryCreateSchema(BaseModel):
    ip: str = Field(max_length=45)
    user_id: int


class IPQueryResponseSchema(BaseModel):
    id: int
    ip: str
    user_id: int

    class Config:
        orm_mode = True


class IPQueryPartialUpdateSchema(BaseModel):
    ip: Optional[str] = None
