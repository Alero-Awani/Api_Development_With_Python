from fastapi import Body, FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
from typing import Optional 
import psycopg2
from psycopg2.extras import RealDictCursor
import time 
from . import models, schemas 
from .database import engine, SessionLocal
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message":"How are you all doing?"}

# CONNECTING TO THE POSTGRES DATABASE 
while True:
    try:
        conn = psycopg2.connect(host="localhost",
                                database = "fastapi",
                                user = "postgres",
                                password = "chegbeyeri",
                                port = 5432,
                                cursor_factory = RealDictCursor)

        cursor = conn.cursor( )
        print("Database Connection was successful")
        break
    except Exception as error:
        print("Connection to the database failed")
        print("Error: ", error)
        time.sleep(2)


#Example of a very simple post request with no data beign sent 
# @app.post("/createposts")
# def create_post():
#     return {"message":"The post has successfully been created"}


#EXPLANATION:
# Here payload is the name of the varaible that will hold the data sent through the post request 
#Body: This actually comes from the FAST API library, so basically here we are extracting the fields from the body, convert it 
#dictionary and store it a variable named payload 
# when you press send on postman you will see the payload printed out 
# In the return part we are refrencing the title and content of the payload dictionary
@app.post("/createposts")
def create_post(payload: dict = Body(...)):
    print(payload)
    return {"new post": f"title: {payload['title']} content: {payload['content']}"}


#DEFINING SCHEMA:
#Here we will be using pydantic to define what our schema should look like, this helps to solve certian issues 

# EXPLANATION:
# This is the pydantic model we have created below 
# we are passing in the different properties for our post, title and content 
# str -> represents the field type 
# here we are assigning the default value of category to False in case the user doesnt provide it 
#rating is a fully optional field and if the user doesnt provide it, it will default to None 

class Post(BaseModel):
    title: str
    content: str
    published: bool
    # rating: Optional[int] = None
    # category:  bool = False

#EXPLANATION : 
# Here we are refrencing the Post pydantic model above and saving it in a variable called new_post   
# it will automatically validate the data it receives from the client based on the model, it will check if the 
# client passed in the required field with field types 
# NOTE: When we extract the data and save it into new post, it actuall stores it as a pydantic model and all pydantic models have an 
# method called .dict (), so if you ever need to convert your pydantic model to a dictionary, use this
# @app.post("/posts")
# def create_post(new_post: Post):
#     print(new_post.published) 
#     print(new_post.rating) 
#     print(new_post)
#     print(new_post.dict())
#     return {"data": new_post}

#EXPLANATION: Ideally we are supposed to store our post in a database, instead we will store it in a list of dictionaries
my_posts = [
    {"title":"Here goes another woman", "content" : "The woman was awake","id": 1},
    {"title":"The boy who cried wolf","content": "The boy was eaten by the wolf","id":2},
    {"title":"Alero against the world man","content":"This is about Alero just believing in herself man","id":3},
    
]


# Here we are passing in the list we described above, recall that it will be converted to json first so that it can be sent 
# over our API 
@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM public."Posts";""")
    posts = cursor.fetchall()
    print(posts)
    return {"data": my_posts}


# using the post to add new data to our list of dictionaries 
# we are sending new data through post that we would like to append to our dictionary 
@app.post("/posts")
def create_post(new_post: schemas.CreatePost):

    #WORKING WITH POSTGRES 
    cursor.execute("""INSERT INTO public."Posts" (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
                   (new_post.title, new_post.content, new_post.published))
    fetch_post = cursor.fetchone()
    conn.commit()
    return {"data": fetch_post}

    #WORKING WITH IN MEMORY DICTIONARY
    # #convert the pydantic model to a dictionary
    # post_dict = new_post.dict()
    # #assign an id to the post and give it a random integer 
    # post_dict["id"] = randrange(1, 1000000)
    # my_posts.append(post_dict)
    # return {"data": post_dict}

# define a function to get one post, used with the route below
def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

# define a route to get just one post based on a path parameter {id}
# we can pass the value into the function as you can see below 
# in postman put http://127.0.0.1:8000/posts/2
# id : int below automatically converts the id which will be given as a string by default to an integer, and also helps with valisdation
@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute("""SELECT * FROM public."Posts" WHERE id = %s """,
                   (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with the id {id} was not found")

    #WORKING WITH IN MEMORY DICTIONARY
    # print(id)
    # return {"post_detail": f"This is the post you are interested in {id}"}
    # post = find_post(id)
    return {"post detail": post}


# To get the latest post 
@app.get("/posts/latest")
def get_latest_post():
    latest = my_posts[len(my_posts) - 1]
    return {"details": latest}

# The delete function 
#Enumerate - This helps to keep track of loops, and the item accessed within that iteration of the loop 
# Enumerate helps with this need by assigning a counter to each item in the object, allowing us to track the accessed items.
# It essentially turns each item into a key-value pair, where each item in the collection is paired with a number 

# This function will give us the index of the dictionary with that specific id 
def find_index_post(id): 
    for i,p in enumerate(my_posts):
        if p["id"] == id:
            return i 
#DELETING A POST 

@app.delete("/posts/{id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):

    cursor.execute("""DELETE FROM public."Posts" WHERE id = %s RETURNING * """,
                   (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} does not exist')
    return Response(status_code=status.HTTP_204_NO_CONTENT)

    #IN MEMORY METHOD
    # index = find_index_post(id)
    # we are using this to raise a 404 error if the user passes an id that doesnt exist
    # if index == None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id {id} does not exist')
    # my_posts.pop(index)


#UPDATE POST with PUT
@app.put("/posts/{id}")
def update_post(id: int, post: schemas.CreatePost):

    cursor.execute("""UPDATE public."Posts" SET title=%s, content=%s, published=%s WHERE id=%s RETURNING * """,
                   (post.title, post.content, post.published, str(id)))
    
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'Post with id {id} does not exist')
    return {"data": updated_post }


    # IN MEMORY DICTIONARY 
    # index = find_index_post(id)
    # print(index)
    # # we are using this to raise a 404 error if the user passes an id that doesnt exist
    # if index == None:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail=f'Post with id {id} does not exist')
    # # now we want to update our dictionary of posts 
    # # first we convert the data we receive from our front end to a dictionary
    # post_dict = post.dict()

    # # we are setting the id key field in our new passed dictionary to the id that is passed in to the function
    # post_dict['id'] = id 

    # # recall that we got the index of the specific post that we are updating through its id
    # # now grab the post from the dictionary
    # my_posts[index] = post_dict 
    # # this above will automatically replace the content in the old dictionary 
    # return {"message":"The post has successfully been updated"}



#TESTING OUT SQLALCHEMY ORM
@app.get("/sqlalchemy")
def test_post(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}



