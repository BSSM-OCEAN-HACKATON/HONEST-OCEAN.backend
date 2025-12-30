from fastapi import FastAPI
from app.api.endpoints import fish, merchant
from dotenv import load_dotenv
from app import models
from app.database import engine

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fish Analysis API")

app.include_router(fish.router, prefix="/api/v1/fish", tags=["Fish"])
app.include_router(merchant.router, prefix="/api/v1/merchant", tags=["Merchant"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
