from fastapi import Request, HTTPException, status

async def get_authenticated_user(request: Request, database):
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация"
        )
    user = await database["users"].find_one({"session": token})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )
    return user

async def check_auth_us(request, database) -> bool:
    token = request.cookies.get('token')
    try:
        if token:
            user = await database["users"].find_one({"session": token})
            return True if user else False
        return False 
    except Exception:
        return False