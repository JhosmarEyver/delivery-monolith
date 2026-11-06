from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.database import get_db


router = APIRouter()


# ============================================================
# Schema para procesar un pago
# ============================================================

class PaymentRequest(BaseModel):
    order_id: str
    amount: float = Field(gt=0)
    payment_method: str


# ============================================================
# Procesar pago
# ============================================================

@router.post("/process")
def process_payment(
    payment_data: PaymentRequest,
    db: Session = Depends(get_db)
):
    return {
        "transaction_id": "TXN-998877",
        "order_id": payment_data.order_id,
        "status": "APPROVED",
        "amount": payment_data.amount,
        "payment_method": payment_data.payment_method
    }


# ============================================================
# Health check del módulo Payment
# ============================================================

@router.get("/health")
def payment_health():
    return {
        "module": "payment",
        "status": "ok"
    }

