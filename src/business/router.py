import uuid

from fastapi import APIRouter


router = APIRouter(
    prefix="/api/business-profile",
    tags=["business"],
)


@router.get("/{business_id}")
async def get_business(business_id: uuid.UUID):
    pass


@router.post("/")
async def create_business():
    pass


@router.put("/{business_id}")
async def update_business(business_id: uuid.UUID):
    pass


@router.delete("/{business_id}")
async def delete_business(business_id: uuid.UUID):
    pass
