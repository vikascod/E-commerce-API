from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app import schemas, models
from app.database import get_db

router = APIRouter(
    tags=['Carts']
)


@router.get("/carts/{cart_id}/items", response_model=schemas.Cart)
async def get_cart_items(cart_id: int, db: Session = Depends(get_db)):
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart

@router.post("/carts", response_model=schemas.Cart)
async def add_item_to_cart(item: schemas.CartCreate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = models.Cart(**item.dict(exclude={"product_id"}), product=product)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item



@router.put("/carts/{cart_id}/items/{item_id}", response_model=schemas.Cart)
async def update_cart_item(cart_id: int, item_id: int, item: schemas.CartCreate, db: Session = Depends(get_db)):
    
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_item = db.query(models.Cart).filter(models.Cart.id == item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")

    cart_item.quantity = item.quantity
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart


@router.delete("/carts/{cart_id}/items/{item_id}")
async def delete_cart_item(cart_id: int, item_id: int, db: Session = Depends(get_db)):
    
    cart = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_item = db.query(models.Cart).filter(models.Cart.id == item_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(cart_item)
    db.commit()
    return {"message": "Cart item deleted successfully"}



@router.put('/cart/increase/quantity/{cart_id}')
async def increase_item_quantity(cart_id: int, db: Session=Depends(get_db)):
    # retrieve the cart item from the database
    cart_item = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    
    # check if the item exists
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    
    # increment the quantity of the item
    cart_item.quantity += 1
    
    # update the database
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    
    # return the updated cart item
    return cart_item


@router.put('/cart/decrease/quantity/{cart_id}')
async def decrease_item_quantity(cart_id: int, db: Session=Depends(get_db)):
    # retrieve the cart item from the database
    cart_item = db.query(models.Cart).filter(models.Cart.id == cart_id).first()
    
    # check if the item exists
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    
    # check if the quantity is already 1
    if cart_item.quantity == 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quantity cannot be less than 1")
    
    # decrement the quantity of the item
    cart_item.quantity -= 1
    
    # update the database
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    
    return cart_item