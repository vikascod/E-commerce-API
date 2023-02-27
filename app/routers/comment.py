from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.oauth2 import get_current_user
from app import schemas, models
from app.database import get_db

router = APIRouter(
    tags=['Comments']
)


@router.post('/comments/{product_id}')
async def create(product_id:int, comment:schemas.CommentCreate, db:Session=Depends(get_db), current_user:int=Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id==product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'No product available with id {product_id}')

    if product.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")

    new_comment = models.Comment(user_id=current_user.id, product_id=product.id, **comment.dict())
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@router.get('/comment/{comment_id}')
async def show(comment_id:int, db:Session=Depends(get_db)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No comment with id {comment_id}")

    return comment


@router.put('/product/{product_id}/comment/{comment_id}')
async def update(product_id:int, comment_id:int, request:schemas.CommentCreate, db:Session=Depends(get_db), current_user:int=Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id==product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No Product available with id {product_id}")

    comment_update = db.query(models.Comment).filter(models.Comment.id==comment_id)
    comment = comment_update.first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No comment with id {comment_id}")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")

    comment_update.update(request.dict())
    db.commit()
    return comment_update.first()


@router.delete('/comment/{comment_id}')
async def destroy(comment_id:int, db:Session=Depends(get_db), current_user:int=Depends(get_current_user)):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No comment with id {comment_id}")
    
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform actions")
    
    db.delete(comment)
    db.commit()
    return {'msg':'Deleted'}