from fastapi.responses import JSONResponse
from fastapi import Request
from server import database, app
from server.core.functions.user import get_authenticated_user

@app.get("/v1/get_name")
async def get_name(request: Request):
    try:
        user = await get_authenticated_user(request=request,database=database)
        if user:
            name = user["name"]
            return JSONResponse({"status": True, "name": name})
        else:
            return JSONResponse({"status": False, "message": "server error"}, status_code=500)
    except Exception:
               return JSONResponse({"status": False, "message": "server error"}, status_code=500)