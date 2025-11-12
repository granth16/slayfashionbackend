from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..models import Customer
from ..schemas import CustomerData

router = APIRouter(prefix="/api/customer", tags=["Customer"])


@router.get("/profile", response_model=CustomerData)
async def get_customer_profile(
    phone: str,
    db: Session = Depends(get_db)
):
    """
    Get customer profile by phone number
    """
    customer = db.query(Customer).filter(Customer.phone == phone).first()
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )
    
    return CustomerData(
        id=str(customer.id),
        phone=customer.phone,
        email=customer.shopify_email,
        first_name=customer.first_name,
        last_name=customer.last_name,
        shopify_customer_id=customer.shopify_customer_id
    )


@router.get("/check")
async def check_customer_exists(
    phone: str,
    db: Session = Depends(get_db)
):
    """
    Check if customer exists in database
    """
    customer = db.query(Customer).filter(Customer.phone == phone).first()
    
    return {
        "exists": customer is not None,
        "phone": phone
    }

