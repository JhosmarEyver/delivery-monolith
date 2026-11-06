from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List


router = APIRouter()


# =========================
# Schemas
# =========================

class RestaurantCreate(BaseModel):
    name: str
    address: str
    phone: str | None = None
    is_open: bool = True


class Restaurant(RestaurantCreate):
    id: int


# =========================
# Base de datos temporal
# =========================

restaurants: List[Restaurant] = []

_next_id = 1


# =========================
# Crear restaurante
# =========================

@router.post("/", response_model=Restaurant, status_code=201)
def create_restaurant(data: RestaurantCreate):
    global _next_id

    restaurant = Restaurant(
        id=_next_id,
        name=data.name,
        address=data.address,
        phone=data.phone,
        is_open=data.is_open,
    )

    restaurants.append(restaurant)
    _next_id += 1

    return restaurant


# =========================
# Obtener restaurantes
# =========================

@router.get("/", response_model=List[Restaurant])
def get_restaurants():
    return restaurants


# =========================
# Obtener restaurante por ID
# =========================

@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: int):

    for restaurant in restaurants:
        if restaurant.id == restaurant_id:
            return restaurant

    raise HTTPException(
        status_code=404,
        detail="Restaurant not found"
    )


# =========================
# Actualizar restaurante
# =========================

@router.put("/{restaurant_id}", response_model=Restaurant)
def update_restaurant(
    restaurant_id: int,
    data: RestaurantCreate
):
    for index, restaurant in enumerate(restaurants):

        if restaurant.id == restaurant_id:

            updated_restaurant = Restaurant(
                id=restaurant_id,
                name=data.name,
                address=data.address,
                phone=data.phone,
                is_open=data.is_open,
            )

            restaurants[index] = updated_restaurant

            return updated_restaurant

    raise HTTPException(
        status_code=404,
        detail="Restaurant not found"
    )


# =========================
# Eliminar restaurante
# =========================

@router.delete("/{restaurant_id}")
def delete_restaurant(restaurant_id: int):

    for index, restaurant in enumerate(restaurants):

        if restaurant.id == restaurant_id:

            restaurants.pop(index)

            return {
                "message": "Restaurant deleted successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Restaurant not found"
    )
