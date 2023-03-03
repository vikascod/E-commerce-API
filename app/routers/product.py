from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, models
from typing import Optional, List
from app.oauth2 import get_current_user


import redis
import requests
import json


host = "localhost"
# host = "192.168.1.100" 
port = 6379
rd = redis.Redis(host=host, port=port)
print(f"Connecting to Redis at {host}:{port}...")



router = APIRouter(
    prefix='/product',
    tags=['Products']
)


class ProductEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, models.Product):
            return {
                "id": obj.id,
                "name": obj.name,
                "description": obj.description,
                "price": obj.price,
                "is_offer": obj.is_sale,
            }
        return super().default(obj)


@router.post('/')
async def create(product:schemas.ProductCreate, db:Session=Depends(get_db), current_user:int=Depends(get_current_user)):
    new_product = models.Product(user_id=current_user.id, **product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


# @router.get('/', response_model=List[schemas.Product])
# async def all_read(skip: int = 0, limit: int = 20, search: Optional[str] = "", db: Session = Depends(get_db)):
#     products = db.query(models.Product).filter(models.Product.name.contains(search)).offset(skip).limit(limit).all()
#     cache_key = json.dumps(products, cls=ProductEncoder)
#     cache = rd.get(cache_key)
#     if cache:
#         print("Products from cache")
#         return json.loads(cache)
#     else:
#         r = requests.get("http://localhost:8000")
#         print("Product cache set")
#         rd.set(cache_key, json.dumps(products, cls=ProductEncoder))
#         return r.json()




@router.get('/', response_model=List[schemas.Product])
async def all_read(skip: int = 0, limit: int = 20, search:Optional[str]="", db:Session=Depends(get_db)):

    products = db.query(models.Product).filter(models.Product.name.contains(search)).offset(skip).limit(limit).all()

    return products



@router.get('/{id}', response_model=schemas.Product)
async def show(id:int, db:Session=Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id==id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No product available with id {id}")
    return product



@router.get('/', response_model=schemas.Product)
async def read_items(search:Optional[str]='', limit: int = 20, db:Session=Depends(get_db)):
    products = db.query(models.Product).filter(models.Product.name.contains(search)).limit(limit).all()
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No product available {search}")
    return products



@router.delete('/{id}')
async def destroy(id:int, db:Session=Depends(get_db), current_user:int=Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id==id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No product available with id {id}")

    if product.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")

    db.delete(product)
    db.commit()
    return {'msg':'Deleted'}


@router.put('/{id}')
async def update(id:int, request:schemas.ProductCreate, db:Session=Depends(get_db), current_user:int=Depends(get_current_user)):
    product_upd = db.query(models.Product).filter(models.Product.id==id)
    product = product_upd.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No product available with id {id}")

    if product.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")

    user_id = current_user.id
    update_data = request.dict(exclude_unset=True)
    db.query(models.Product).filter(models.Product.id==id).update(update_data)
    db.commit()
    return product_upd.first()
