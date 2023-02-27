from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, models
from app.utils import hash
from typing import List
from app.oauth2 import get_current_user


router = APIRouter(
    prefix='/user',
    tags=['Users']
)

@router.post('/')
async def create(user:schemas.UserCreate, db:Session=Depends(get_db)):
    hashed_password = hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get('/{id}', response_model=schemas.User)
async def show(id:int, db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.id==id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No user available with id {id}')
    return user


@router.delete('/{id}')
async def destroy(id:int, db:Session=Depends(get_db), current_user:int=Depends(get_current_user)):
    user_del = db.query(models.User).filter(models.User.id==id).first()
    if not user_del:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user available with id {id}")

    if user_del.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")
    
    db.delete(user_del)
    db.commit()
    return {'msg':'Deleted'}


@router.put('/{id}')
async def update(id:int, request:schemas.UserCreate, db:Session=Depends(get_db), current_user:int=Depends(get_current_user)):
    user_upd = db.query(models.User).filter(models.User.id==id)
    user = user_upd.first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user available with id {id}")

    if user.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")

    hashed_password = hash(request.password)
    request.password = hashed_password
    update_data = request.dict(exclude_unset=True)
    db.query(models.User).filter(models.User.id==id).update(update_data)
    db.commit()
    return user_upd.first()