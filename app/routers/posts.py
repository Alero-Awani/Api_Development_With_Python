from .. import models, schemas, oauth2
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. database import get_db
from typing import List 

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

#GETTING ALL POSTS 
@router.get("/", response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
   posts = db.query(models.Post).all()
   return posts 
#    return {"data": posts}


#CREATE POST(LONGER METHOD)
# @app.post("/posts", status_code=status.HTTP_201_CREATED)
# def create_post(post: Post, db: Session = Depends(get_db)):

#    new_post = models.Post(
#     title=post.title, content=post.content, published=post.published)
#    db.add(new_post)
#    db.commit()
#    db.refresh(new_post)
#    return {"data": new_post}

#CREATE POST(SHORTER METHOD) => imagine if we had many columns in our database, there is a more effective way of doing this
# converting the post pydnatic model to a dictionary and unpacking it 

# the get_current_user function is a dependency that forces the users to be logged in before they can actually create a post 
# STEPS
#1. When the user hits the endpoint, the get_current_user function gets called 
#2. All the get_current_user funtion does is call the verify_access_token, where token which comes from the user is passed 
# in to be verified
# 3. the verify function decodes the token and extracts the id from the payload, validates the schema too and returns the token data
# which in this case is just the id 
#4. Then in our create-post, we will get the id stored in the variable user_id which we have now changed to current_user since it doent 
# only return the id anymore but the full user 
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.CreatePost, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

   # now we can see that from our get_current_user function, we fetched all the user details from the database using db.query
   # and we can access its 
   # email for example using current_user.email
   print(current_user.email)
   new_post = models.Post(**post.dict())
   db.add(new_post)
   db.commit()
   db.refresh(new_post)
   return new_post
#    return {"data": new_post}


#RETREIVING A SINGLE POST WITH THE ID 
@router.get("/{id}", response_model=schemas.PostResponse)
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with the id {id} was not found")

    return {"post detail": post}

#DELETING A SINGLE POST 
@router.delete("/{id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} does not exist')
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# UPDATING A SINGLE POST 
@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int, new_post: schemas.CreatePost, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #saving the query in a variable
    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    #executing the query and storing it in a variable
    post = post_query.first()

    #checking if the executed query returned none so we can send a 404 error meaning the post with the id doesnt exist
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} does not exist')
    
    # if it exists we want to update it using the updated method 
    post_query.update(new_post.dict(), synchronize_session=False)

    # commit the changes 
    db.commit()

    # return the updated post to the user (the first instance of the post)
    return {"data": post_query.first()}

