from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
from typing import Optional, List 
import psycopg2
from psycopg2.extras import RealDictCursor
import time 
from . import models, schemas, utils
from .database import engine, SessionLocal
from sqlalchemy.orm import Session
from .routers import posts, users, auth



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# class Post(BaseModel):
#     title: str
#     content: str
#     published: bool

# #GETTING ALL POSTS 
# @app.get("/posts", response_model=List[schemas.PostResponse])
# def get_posts(db: Session = Depends(get_db)):
#    posts = db.query(models.Post).all()
#    return posts 
# #    return {"data": posts}


# #CREATE POST(LONGER METHOD)
# # @app.post("/posts", status_code=status.HTTP_201_CREATED)
# # def create_post(post: Post, db: Session = Depends(get_db)):

# #    new_post = models.Post(
# #     title=post.title, content=post.content, published=post.published)
# #    db.add(new_post)
# #    db.commit()
# #    db.refresh(new_post)
# #    return {"data": new_post}

# #CREATE POST(SHORTER METHOD) => imagine if we had many columns in our database, there is a more effective way of doing this
# # converting the post pydnatic model to a dictionary and unpacking it 

# @app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
# def create_post(post: schemas.CreatePost, db: Session = Depends(get_db)):

#    new_post = models.Post(**post.dict())
#    db.add(new_post)
#    db.commit()
#    db.refresh(new_post)
#    return new_post
# #    return {"data": new_post}


# #RETREIVING A SINGLE POST WITH THE ID 
# @app.get("/posts/{id}", response_model=schemas.PostResponse)
# def get_post(id: int, response: Response, db: Session = Depends(get_db)):
#     post = db.query(models.Post).filter(models.Post.id == id).first()
#     if not post:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f"post with the id {id} was not found")

#     return {"post detail": post}

# #DELETING A SINGLE POST 
# @app.delete("/posts/{id}" , status_code=status.HTTP_204_NO_CONTENT)
# def delete_post(id: int, db: Session = Depends(get_db)):
#     post = db.query(models.Post).filter(models.Post.id == id)

#     if post.first() == None:
#         raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} does not exist')
#     post.delete(synchronize_session=False)
#     db.commit()
#     return Response(status_code=status.HTTP_204_NO_CONTENT)

# # UPDATING A SINGLE POST 
# @app.put("/posts/{id}", response_model=schemas.PostResponse)
# def update_post(id: int, new_post: schemas.CreatePost, db: Session = Depends(get_db)):
#     #saving the query in a variable
#     post_query = db.query(models.Post).filter(models.Post.id == id)
    
#     #executing the query and storing it in a variable
#     post = post_query.first()

#     #checking if the executed query returned none so we can send a 404 error meaning the post with the id doesnt exist
#     if post == None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'Post with id {id} does not exist')
    
#     # if it exists we want to update it using the updated method 
#     post_query.update(new_post.dict(), synchronize_session=False)

#     # commit the changes 
#     db.commit()

#     # return the updated post to the user (the first instance of the post)
#     return {"data": post_query.first()}

# # USER CREATION REQUESTS 
# @app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     #hash the password obtained from the user pydantic model above
#     hashed_password = utils.hash(user.password)
#     user.password = hashed_password

#     new_user = models.User(**user.dict())
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user


# #GET A PARTICULAR USER FROM THE ID 
# @app.get("/users/{id}", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
# def get_user(id: int, db: Session = Depends(get_db)):
#     new_user = db.query(models.User).filter(models.User.id == id).first()

#     if not new_user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                             detail=f'The user with the id {id} was not found')       

#     return new_user


app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
