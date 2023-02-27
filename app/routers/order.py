from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import schemas, models
from app.oauth2 import get_current_user



router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.get("/", response_model=List[schemas.Order])
async def read_orders(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user:int=Depends(get_current_user)):
    orders = db.query(models.Order).offset(skip).limit(limit).all()
    # if orders.user_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")
    return orders


@router.get("/{order_id}", response_model=schemas.Order)
async def read_order(order_id: int, db: Session = Depends(get_db), current_user:int=Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")

    return order


@router.post("/", response_model=schemas.Order)
async def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), current_user:int=Depends(get_current_user)):

    product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product ID")

    total_price = product.price * order.quantity

    new_order = models.Order(
        user_id= current_user.id,
        product_id=order.product_id, 
        quantity=order.quantity, 
        total_price=total_price,
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order



@router.put("/{order_id}", response_model=schemas.Order)
async def update_order(order_id: int, order: schemas.OrderCreate, db: Session = Depends(get_db), current_user:int=Depends(get_current_user)):
    existing_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not existing_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")


    product = db.query(models.Product).filter(models.Product.id == order.product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid product ID")

    if existing_order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")

    existing_order.total_price = product.price * order.quantity
    existing_order.user_id = order.user_id
    existing_order.product_id = order.product_id
    existing_order.quantity = order.quantity
    # existing_order.update({'user_id': order.user_id, 'product_id': order.product_id, 'quantity': order.quantity, 'total_price': total_price})
    db.commit()
    return db.query(models.Order).filter(models.Order.id == order_id).first()


@router.delete("/{order_id}")
async def delete_order(order_id: int, db: Session = Depends(get_db), current_user:int=Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")

    db.delete(order)
    db.commit()
    return "Order deleted"



@router.put("/{order_id}/status", response_model=schemas.Order)
def update_order_status(order_id: int, status: str, db: Session = Depends(get_db), current_user:int=Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")

    order.status = status
    db.add(order)
    db.commit()
    db.refresh(order)
    return order