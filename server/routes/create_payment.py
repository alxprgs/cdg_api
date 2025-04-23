import uuid
from server import app, database
from yookassa import Configuration, Payment
from server.core.config import settings
from fastapi.responses import JSONResponse

@app.post("/payment/create_paymentv1")
async def create_paymentv1(amount: float):
    Configuration.account_id = settings.ACCOUNT_ID
    Configuration.secret_key = settings.SECRET_KEY  

    payment = Payment.create({
        "amount": {
            "value": amount,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://prghorse/return_url"
        },
        "capture": True,
        "description": "Заказ из кафе Dolce Goose"
    }, uuid.uuid4())

    confirmation_url = payment.confirmation.confirmation_url

    return JSONResponse(content={"status": True,"confirmation_url": confirmation_url}, status_code=200)