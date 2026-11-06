from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List


router = APIRouter()


# =========================
# Schemas
# =========================

class TrackingCreate(BaseModel):
    order_id: int
    status: str
    location: str | None = None


class Tracking(TrackingCreate):
    id: int


# =========================
# Base de datos temporal
# =========================

tracking_records: List[Tracking] = []

_next_id = 1


# =========================
# Crear registro tracking
# =========================

@router.post("/", response_model=Tracking, status_code=201)
def create_tracking(data: TrackingCreate):
    global _next_id

    tracking = Tracking(
        id=_next_id,
        order_id=data.order_id,
        status=data.status,
        location=data.location,
    )

    tracking_records.append(tracking)

    _next_id += 1

    return tracking


# =========================
# Obtener todos los tracking
# =========================

@router.get("/", response_model=List[Tracking])
def get_tracking():
    return tracking_records


# =========================
# Obtener tracking por ID
# =========================

@router.get("/{tracking_id}", response_model=Tracking)
def get_tracking_by_id(tracking_id: int):

    for tracking in tracking_records:

        if tracking.id == tracking_id:
            return tracking

    raise HTTPException(
        status_code=404,
        detail="Tracking record not found"
    )


# =========================
# Obtener tracking de una orden
# =========================

@router.get("/order/{order_id}", response_model=List[Tracking])
def get_order_tracking(order_id: int):

    records = [
        tracking
        for tracking in tracking_records
        if tracking.order_id == order_id
    ]

    return records


# =========================
# Actualizar estado
# =========================

@router.put("/{tracking_id}", response_model=Tracking)
def update_tracking(
    tracking_id: int,
    data: TrackingCreate
):

    for index, tracking in enumerate(tracking_records):

        if tracking.id == tracking_id:

            updated_tracking = Tracking(
                id=tracking_id,
                order_id=data.order_id,
                status=data.status,
                location=data.location,
            )

            tracking_records[index] = updated_tracking

            return updated_tracking

    raise HTTPException(
        status_code=404,
        detail="Tracking record not found"
    )


# =========================
# Eliminar tracking
# =========================

@router.delete("/{tracking_id}")
def delete_tracking(tracking_id: int):

    for index, tracking in enumerate(tracking_records):

        if tracking.id == tracking_id:

            tracking_records.pop(index)

            return {
                "message": "Tracking record deleted successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Tracking record not found"
    )
