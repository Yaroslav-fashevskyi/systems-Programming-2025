from pydantic import BaseModel, Field
from typing import Optional


class LookupResultCreateSchema(BaseModel):
    ip: str = Field(max_length=45)
    country: Optional[str]
    isp: Optional[str]


class LookupResultResponseSchema(BaseModel):
    id: int
    ip: str
    country: Optional[str]
    isp: Optional[str]

    class Config:
        orm_mode = True


class LookupResultPartialUpdateSchema(BaseModel):
    country: Optional[str] = None
    isp: Optional[str] = None
