from server import database, app
from server.core.functions.hash import verify_hash
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from secrets import token_urlsafe
from pydantic_extra_types.phone_numbers import PhoneNumber

class User_login(BaseModel):
    login: PhoneNumber = Field(...)
    password: str = Field(...)

@app.post("/v1/login")
async def login(user_data: User_login) -> JSONResponse:
    db = database["users"]
    try:
        user = await db.find_one({"login": user_data.login})
    except Exception:
        return JSONResponse({"status": False, "message": "server error"}, status_code=500)
    if user:
        if verify_hash(plain_hash=user_data.password, hashed_hash=user["password"]):
            token = token_urlsafe(128)
            csrf_token = token_urlsafe(64)
            await database["users"].update_one({"_id": user["_id"]}, {"$set": {"session": token, "csrf_token": csrf_token}})
            response = JSONResponse({"status": True}, status_code=200)
            response.set_cookie(key="token", value=token, httponly=True, secure=True, samesite="None", domain=".prghorse.ru")
            response.set_cookie(key="csrf_token", value=csrf_token, secure=True, samesite="None", domain=".prghorse.ru")
            return response
        return JSONResponse({"status": False, "message": "Неверный пароль."}, status_code=401)
    return JSONResponse({"status": False, "message": "Пользователь не найден."}, status_code=401)
