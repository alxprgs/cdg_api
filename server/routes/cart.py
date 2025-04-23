from fastapi import Request, HTTPException, status
from pydantic import BaseModel, Field
from server import database, app
from typing import Dict
from fastapi.encoders import jsonable_encoder
from server.core.functions.user import get_authenticated_user
from server.core.functions.cart import generate_cart_id, validate_cart_id
from yookassa import Configuration, Payment
from server.core.config import settings
import uuid

class CartItemCreate(BaseModel):
    name: str
    price: float = Field(gt=0)
    quantity: int = Field(1, gt=0)

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItemResponse(BaseModel):
    cart_id: str
    name: str
    price: float
    quantity: int

class OrderResponse(BaseModel):
    total_price: float
    status: bool
    payment_url: str


@app.post("/v1/cart/items", response_model=Dict)
async def add_to_cart(request: Request,item: CartItemCreate,):
    user = await get_authenticated_user(request, database)
    cart = user.get("cart", {})
    
    existing_cart_id = None
    for cart_id, cart_item in cart.items():
        if cart_item.get("name") == item.name:
            existing_cart_id = cart_id
            break
    
    if existing_cart_id:
        result = await database["users"].update_one(
            {
                "_id": user["_id"],
                f"cart.{existing_cart_id}": {"$exists": True}
            },
            {"$inc": {f"cart.{existing_cart_id}.quantity": 1}}
        )
        cart_id = existing_cart_id
    else:
        cart_id = generate_cart_id()
        update_data = {
            f"cart.{cart_id}": {
                "name": item.name,
                "price": item.price,
                "quantity": item.quantity
            }
        }
        result = await database["users"].update_one(
            {"_id": user["_id"]},
            {"$set": update_data}
        )
    if result.modified_count != 1:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось добавить товар в корзину"
        )
    
    return {
        "status": True,
        "cart_id": cart_id,
        "message": "Товар добавлен в корзину"
    }

@app.patch("/v1/cart/items/{cart_id}", response_model=Dict)
async def update_cart_item(
    request: Request,
    cart_id: str,
    update_data: CartItemUpdate,
    
):
    validate_cart_id(cart_id)
    user = await get_authenticated_user(request, database)
    
    result = await database["users"].update_one(
        {
            "_id": user["_id"],
            f"cart.{cart_id}": {"$exists": True}
        },
        {"$set": {f"cart.{cart_id}.quantity": update_data.quantity}}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Элемент корзины не найден"
        )

    return {
        "status": True,
        "message": "Элемент корзины обновлен"
    }

@app.delete("/v1/cart/items/{cart_id}", response_model=Dict)
async def delete_cart_item(
    request: Request,
    cart_id: str,
    
):
    validate_cart_id(cart_id)
    user = await get_authenticated_user(request, database)
    
    result = await database["users"].update_one(
        {
            "_id": user["_id"],
            f"cart.{cart_id}": {"$exists": True}
        },
        {"$unset": {f"cart.{cart_id}": ""}}
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Элемент корзины не найден"
        )

    return {
        "status": True,
        "message": "Элемент корзины удален"
    }

@app.get("/v1/cart/items", response_model=Dict)
async def get_cart_items(request: Request):
    user = await get_authenticated_user(request, database)
    
    cart = user.get("cart", {})
    
    formatted_cart = [
        {
            "cart_id": cart_id,
            "name": item["name"],
            "price": float(item["price"]),
            "quantity": int(item["quantity"])
        }
        for cart_id, item in cart.items()
    ]
    return {
        "status": True,
        "cart": jsonable_encoder(formatted_cart)
    }

@app.post("/v1/cart/order", response_model=OrderResponse)
async def create_order(
    request: Request,
    
):
    user = await get_authenticated_user(request, database)
    cart = user.get("cart", {})
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно создать заказ: корзина пуста"
        )
    
    total_price = sum(item["price"] * item["quantity"] for item in cart.values())
    total_price = round(total_price, 2)
    
    order_id = str(uuid.uuid4())

    Configuration.account_id = settings.ACCOUNT_ID
    Configuration.secret_key = settings.SECRET_KEY  

    payment = Payment.create({
        "amount": {
            "value": total_price,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://prghorse.ru/"
        },
        "capture": True,
        "description": f"Заказ из кафе Dolce Goose ({order_id})"
    }, uuid.uuid4())

    payment_url = payment.confirmation.confirmation_url
    
    await database["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"cart": {}}}
    )
    
    return {
        "total_price": total_price,
        "status": True,
        "payment_url": payment_url
    }