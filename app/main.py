from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.routers import user, auth, product, cart, order, comment

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce API",
    description="Trusted Website in India"
)

app.include_router(user.router)
app.include_router(auth.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(order.router)
app.include_router(comment.router)