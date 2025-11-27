from pydantic import BaseModel, Field
from typing import Optional


class ProjectCreateSchema(BaseModel):
    name: str = Field(max_length=255)
    description: str = Field(max_length=500)


class ProjectResponseSchema(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


class ProjectPartialUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
