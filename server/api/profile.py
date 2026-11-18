from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from server.database import get_db
from server.schemas.profile import ProfileDocument
from server.services.profile import ensure_demo_profile

router = APIRouter()


@router.get("/profile", response_model=ProfileDocument)
def get_profile(db: Session = Depends(get_db)) -> ProfileDocument:
    profile = ensure_demo_profile(db)
    db.commit()
    return ProfileDocument.model_validate(profile.document)


@router.put("/profile", response_model=ProfileDocument)
def put_profile(body: ProfileDocument, db: Session = Depends(get_db)) -> ProfileDocument:
    profile = ensure_demo_profile(db)
    profile.document = body.model_dump(mode="json")
    db.commit()
    return body
