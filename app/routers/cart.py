from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db

router = APIRouter(
    tags=['Carts']
)


@router.get("/carts/{cart_id}/items", response_model=schemas.Cart)
def get_cart_items(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@router.post("/carts", response_model=schemas.Cart)
def add_item_to_cart(item: schemas.CartCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = models.Cart(**item.dict(exclude={"product_id"}), product=product)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item



@router.put("/carts/{cart_id}/items/{item_id}", response_model=schemas.Cart)
def update_cart_item(cart_id: int, item_id: int, item: schemas.CartCreate, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    cart_item = db.query(models.Cart).filter(models.Cart.id == item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    # if item.quantity > cart_item.product.quantity:
    #     raise HTTPException(status_code=400, detail="Not enough product in stock")
    cart_item.quantity = item.quantity
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart


@router.delete("/carts/{cart_id}/items/{item_id}")
def delete_cart_item(cart_id: int, item_id: int, db: Session = Depends(get_db)):
    
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_item = db.query(models.Cart).filter(models.Cart.id == item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Cart item deleted successfully"}
