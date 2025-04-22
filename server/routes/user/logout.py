from server import app
from fastapi.responses import JSONResponse

@app.get("/logout")
async def logout() -> JSONResponse:
    response = JSONResponse({"status": True}, status_code=200)
    response.delete_cookie(key="token")
    return response
