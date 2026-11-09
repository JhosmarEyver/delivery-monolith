from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.core.database import get_db


router = APIRouter()


# ============================================================
# Schema para crear un pedido
# ============================================================

class OrderCreate(BaseModel):
    customer_id: int
    restaurant_id: int
    items: list[str]


# ============================================================
# Crear pedido
# ============================================================

@router.post("/")
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db)
):
    return {
        "message": "Pedido creado exitosamente",
        "order_id": "ORD-12345",
        "status": "PENDING",
        "customer_id": order_data.customer_id,
        "restaurant_id": order_data.restaurant_id,
        "items": order_data.items
    }


# ============================================================
# Health check del módulo (va antes de /{order_id} para que no lo capture)
# ============================================================

@router.get("/health")
def order_health():
    return {
        "module": "order",
        "status": "ok"
    }


# ============================================================
# Obtener pedido
# ============================================================

@router.get("/{order_id}")
def get_order(
    order_id: str,
    db: Session = Depends(get_db)
):
    return {
        "order_id": order_id,
        "status": "IN_PREPARATION",
        "items": [
            "Hamburguesa",
            "Papas"
        ]
    }

