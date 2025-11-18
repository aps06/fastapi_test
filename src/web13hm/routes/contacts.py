from fastapi import (
    APIRouter,
    Path,
    Depends,
    HTTPException,
    Query,
    status,
    Security,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from fastapi.requests import Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from src.web13hm.shemas import (
    ResponseContactModel,
    ContactModel,
)
from src.web13hm.database.db import get_db
from src.web13hm.repository import contacts as contacts_repository
from src.web13hm.services.auth import auth_service
from src.web13hm.core.config import limiter


router = APIRouter(prefix='/contacts', tags=["contacts"])

security = HTTPBearer()


@router.get("/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@router.get("/contacts")
@limiter.limit("3/minute")
async def read_all_contacts(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
    skip: int = 0,
    limit: int = Query(default=10, le=100, ge=10),
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    contacts = await contacts_repository.get_Contacts(skip=skip, limit=limit, db=db, user=current_user)
    return contacts


@router.get("/contacts/{data}", response_model=None)
@limiter.limit("5/minute")
async def read_contacts(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
    data: str = Path(description="The ID, NAME, LAST NAME, or EMAIL of the contact"),
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    contacts = await contacts_repository.get_Contacts_by(Contacts_data=data, user=current_user, db=db)

    return contacts


@router.get("/birthday")
@limiter.limit("2/minute")
async def birthday_by_7_day(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
    skip: int = 0,
    limit: int = Query(default=10, le=100, ge=10),
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
) -> List[ResponseContactModel]:
    contacts = await contacts_repository.birthday_by_7_day(skip=skip, limit=limit, db=db, current_user=current_user)

    return contacts


@router.post("/Create", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_contact(
    request: Request,
    contact: ContactModel,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security),
    current_user=Depends(auth_service.get_current_user),
):
    new_contact = await contacts_repository.create_contact(contact=contact, db=db, current_user=current_user)

    return new_contact


@router.put("/Update/{contact_id}", response_model=ResponseContactModel)
@limiter.limit("3/minute")
async def update_contact(
    request: Request,
    contact_id: int,
    contact: ContactModel,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security),
    current_user=Depends(auth_service.get_current_user),
):
    contacts_db = await contacts_repository.update_contact(contact_id=contact_id, contact=contact, db=db, current_user=current_user)
    return contacts_db


@router.delete(
    "/delete/{contact_id}",
)
@limiter.limit("2/minute")
async def delete_contact(
    request: Request,
    contact_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_service.get_current_user),
):
    return await contacts_repository.delete_contact(contact_id=contact_id, db=db, current_user=current_user)
