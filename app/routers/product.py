from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, models
from typing import Optional, List

router = APIRouter(
    prefix='/product',
    tags=['Products']
)

@router.post('/')
async def create(product:schemas.ProductCreate, db:Session=Depends(get_db)):
    new_product = models.Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


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

@router.delete('/{id}')
async def destroy(id:int, db:Session=Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id==id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No product available with id {id}")
    db.delete(product)
    db.commit()
    return {'msg':'Deleted'}


@router.put('/{id}')
async def update(id:int, request:schemas.ProductCreate, db:Session=Depends(get_db)):
    product_upd = db.query(models.Product).filter(models.Product.id==id)
    product = product_upd.first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No product available with id {id}")
    update_data = request.dict(exclude_unset=True)
    db.query(models.Product).filter(models.Product.id==id).update(update_data)
    db.commit()
    return product_upd.first()
