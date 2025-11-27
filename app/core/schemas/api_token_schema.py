from pydantic import BaseModel, Field
from typing import Optional


class ApiTokenCreateSchema(BaseModel):
    token: str = Field(max_length=255)
    user_id: int


class ApiTokenResponseSchema(BaseModel):
    id: int
    token: str
    user_id: int

    class Config:
        orm_mode = True


class ApiTokenPartialUpdateSchema(BaseModel):
    token: Optional[str] = None
