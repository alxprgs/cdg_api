from server.core.functions.user import check_auth_us
from fastapi import Request
from server import database, app

@app.get("/v1/check_auth")
async def check_auth(request: Request) -> bool:
    return await check_auth_us(request=request, database=database)
