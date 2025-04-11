from typing import List

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ContactResponse, ContactUpdate
from src.services.contacts import ContactService
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, current_user.id)
    return contacts

@router.get("/search", response_model=List[ContactResponse])
async def search_contacts(
    query: str = Query(..., description="Search term (name, surname or email)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(query, current_user.id)
    return contacts

@router.get("/birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(
    days: int = Query(7, ge=1, le=30, description="Number of days for birthday lookup"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts_by_birthday(days, current_user.id)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, current_user.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, current_user.id)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate, 
    contact_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, current_user.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact_service = ContactService(db)
    contact = await contact_service.delete_contact(contact_id, current_user.id)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact 