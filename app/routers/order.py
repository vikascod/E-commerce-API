from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas, models


router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)


@router.get("/", response_model=List[schemas.Order])
async def read_orders(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=schemas.Order)
async def read_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.post("/", response_model=schemas.Order)
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == order.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    
    product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product ID")
    
    total_price = product.price * order.quantity

    new_order = models.Order(user_id=order.user_id, product_id=order.product_id, quantity=order.quantity, total_price=total_price)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.put("/{order_id}", response_model=schemas.Order)
async def update_order(order_id: int, order: schemas.OrderCreate, db: Session = Depends(get_db)):
    existing_order = db.query(models.Order).filter(models.Order.id == order_id)
    if not existing_order.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    user = db.query(models.User).filter(models.User.id == order.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product ID")
    total_price = product.price * order.quantity
    existing_order.update({'user_id': order.user_id, 'product_id': order.product_id, 'quantity': order.quantity, 'total_price': total_price})
    db.commit()
    return db.query(models.Order).filter(models.Order.id == order_id).first()


@router.delete("/{order_id}")
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    db.delete(order)
    db.commit()
    return "Order deleted"
