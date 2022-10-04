from fastapi import Body, FastAPI
from fastapi.params import Body
from pydantic import BaseModel

# here we are assigning the default value of category to False in case the user doesnt provide it 
class Post(BaseModel):
    title: str
    content: str
    category:  bool = False

app = FastAPI()

@app.get("/")
async def root():
    return {"message":"Hello World"}

@app.get("/posts/v1")
async def root():
    return {"Hello":"Hey there, how are you"}


# @app.post("/createposts")
# def create_post(payload: dict = Body(...)):
#     print(payload)
#     return {"new post": f"title: payload[title] content: payload[content]"}

# Using the Pydantic BaseModel
@app.post("/createposts")
def create_post(new_post: Post):
    print(new_post.category)
    print(new_post.dict())
    return {"data":"create new post data"}