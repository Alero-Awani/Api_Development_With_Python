# This is where we will learn about responses 
# from main.py. if you pass in something like http://8080/posts/5 where 5 doesnt exist in the dictionary
# it doesnt return an explanatory response which is why we have to make use of fast Api response 

from fastapi import Response , status, HTTPException
from fastapi import Body, FastAPI
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
from typing import Optional 

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool
    rating: Optional[int] = None
    # category:  bool = False

my_posts = [
    {"title":"Here goes another woman", "content" : "The woman was awake","id": 1},
    {"title":"The boy who cried wolf","content": "The boy was eaten by the wolf","id":2},
    {"title":"Alero against the world man","content":"This is about Alero just believing in herself man","id":3},
    
]

def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

# @app.get("/posts/{id}")
# def get_post(id: int, response: Response):
#     post = find_post(id)
#     if not post:
#         response.status_code = 404
#     else:
#         return {"post detail": post}


# instead of hardcoding the 404 we can import status from the fastapi library
# @app.get("/posts/{id}")
# def get_post(id: int, response: Response):
#     post = find_post(id)
#     if not post:
#         response.status_code = status.HTTP_404_NOT_FOUND
#         return {"message": f"post with the id {id} was not found"}
#     return {"post detail": post}

# Instead of doing the stuff above, we can use httpException which is a better option
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with the id {id} was not found")
    return {"post detail": post}


# Normally when we create a post, the status code is supposed to be 201, but it ususally shows us 200
# to change the default status code to 201, we do this 
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(new_post: Post):
    #convert the pydantic model to a dictionary
    post_dict = new_post.dict()
    #assign an id to the post and give it a random integer 
    post_dict["id"] = randrange(1, 1000000)
    my_posts.append(post_dict)
    return {"data": post_dict}

