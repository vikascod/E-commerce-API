from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import schemas, models
from app.database import get_db
from app.oauth2 import get_current_user, create_access_token
from app.utils import verify_pass


router = APIRouter(
    tags=['Authentication']
)

@router.post('/login')
async def login(user_credentials:OAuth2PasswordRequestForm=Depends(), db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not verify_pass(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Password")
    
    access_token = create_access_token(data={'user_id':user.id})
    return {'access_token':access_token, 'token_type':'bearer'}