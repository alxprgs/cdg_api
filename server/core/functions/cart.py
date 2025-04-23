from fastapi import HTTPException, status
from uuid import UUID
import uuid 

def validate_cart_id(cart_id: str):
    try:
        UUID(cart_id, version=4)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Некорректный ID корзины")
    
def generate_cart_id() -> str:
    return str(uuid.uuid4())