from fastapi import APIRouter, Depends, status, HTTPException, Response 
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session 
from .. import database, schemas, models, utils, oauth2


router = APIRouter(
    tags=['Authentication']
)


@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):

    # we want to make a request to our user table in the database to retrieve the user based off his email
    # models.User => we are accessing the User table and filtering it 
    # we are comparing the email in the table to the email that we passed in which was stored in the variable(user_credentials)
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    # if there is no user with that specific email then we are going to raise an exception
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid Credentials, The user with email {user_credentials.email} does not exist")
    
    # NOTE: The plain password is stored in User credentials and the hashed password which is from the database is stored in user 
    # Now if the passwords are actually not equal then we will raise an http exception
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail="Invalid Credentials")
    
    # Create a Token, here we are passing just the user_id in the payl oad
    access_token = oauth2.create_access_token(data={"user_id": user.id})
    # Return Token 
    return {"access_token": access_token, "token_type": "bearer"}
