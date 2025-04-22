from server import app
from fastapi.responses import JSONResponse

@app.get("/stauts")
async def status() -> JSONResponse:
    return JSONResponse({"status": True}, status_code=200)
