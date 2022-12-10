from pydantic import BaseModel, EmailStr
from typing import Optional 
from datetime import datetime

# REQUEST SCHEMA FOR POSTS
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True 
    # rating: Optional[int] = None
    # category:  bool = False

class CreatePost(PostBase):
    #this will inherit all the attributes from postbase
    pass 

class UpdatePost(PostBase):
    published: bool

# RESPONSE SCHEMA FOR POSTS
class PostResponse(PostBase):
    id: int
    created_at: datetime
   
    class Config:
     orm_mode = True


# USER REQUEST SCHEMA
# This is used to verify that the information passed in by the user is correct 
# we wil be using the email validator library to ensure that the email is actually the right format 
class UserCreate(BaseModel):
    email: EmailStr
    password: str

#USER RESPONSE SCHEMA
class UserResponse(BaseModel):
    email: EmailStr
    id: int
    class Config:
        orm_mode = True 


#LOGIN REQUEST SCHEMA 
class UserLogin(BaseModel):
    email: EmailStr
    password: str 

#SCHEMA FOR THE TOKEN, recall that in our /login route ,we return the the access_token and the token type 
class Token(BaseModel):
    access_token: str
    token_type: str

# We will also set up a schema for the data that we encoded in the token 
class TokenData(BaseModel):
    id: Optional[str] = None 
