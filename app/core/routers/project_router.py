from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.settings.db import get_db
from app.core.models.project import Project
from app.core.models.user import User


# ---------- Pydantic-схеми ----------

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    # ОБОВʼЯЗКОВО: до якого юзера належить проєкт
    user_id: str


class ProjectRead(ProjectBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        # замість orm_mode=True в Pydantic v2
        from_attributes = True


# ---------- Router ----------

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("/", response_model=List[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    """
    Очікує JSON:
    {
        "name": "string",
        "description": "string",
        "user_id": "uuid існуючого користувача"
    }
    """

    # 1. Перевіряємо, що такий user існує
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User with this id does not exist")

    project = Project(
        name=payload.name,
        description=payload.description,
        user_id=payload.user_id,
        created_at=datetime.utcnow(),
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@router.delete("/{project_id}")
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    return {"status": "deleted"}
