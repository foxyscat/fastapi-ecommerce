from fastapi import FastAPI
from db.database import engine
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from models.user_models import Base
from routers import _admin, _auth, _basket, _payment, _products,_user_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan)


app.include_router(_auth.router)
app.include_router(_basket.router)
app.include_router(_payment.router)
app.include_router(_products.router)
app.include_router(_admin.router)
app.include_router(_user_admin.router)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
