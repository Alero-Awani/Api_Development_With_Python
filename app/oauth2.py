from jose import JWTError, jwt
from datetime import datetime,timedelta 
from . import schemas, database, models 
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
# There are three things we need to take care of including the 
#SECRET KEY
#ALGORITHM
#EXPIRATION TIME s

# Run openssl rand -hex 32

SECRET_KEY = '802953df45c64b73efa15d92c3b95856822710a8323542d8acbd3eb42a634a1a'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# we have to provide whatever data we want to encode in the token as a dictionary hence (data: dict)
#next we make a copy of the data because we will be manipulating the copy and we dont want to change the original data hence the .copy()
# for the expiration time, we want to grab the current time and then add 30 minutes to it 
# .update helps to insert an item into the dictionary and recall encoded_data is a dictionay
# jwt.encode() is the method that actually creates the jwt token
# not that encoded_data/data is what will have the payload

def create_access_token(data: dict):
    encoded_data = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    encoded_data.update({"exp": expire})
    encoded_jwt = jwt.encode(encoded_data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Now we want to create a function that will verify the token 
#credentials_exception => what our exception should be if the tokens dont match 
# jwt.decode decodes the token
# next we are using payload.get to retreive the data that was passed into the token, in auth.py we can see it in data={"user_id":user.id}
# and storing it in the variable id 
# If theres no id 
#note that when you're writing code that has a chance of failing its always better to put it in a try and except block 
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception 
         #here we are just validating that the user_id that was embedded actually matches the token schema, and ensure that we actually 
        # have access to the data that was passed in the token, here its just the id 
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data


#We can pass this function as a dependency into our path operations and when we do that, it will take the token from the request
#automatically, extract the id for us, verify the token is correct by calling the verify_access_token function, we can also have it
# automatically fetch the user from the database and add it as a paramter into our path operation function.


#1. heres what actually happens 
# Anytime we have a specific endpoint that has to be protected, i.e the user needs to be logged in to use it 
# E.g users that want to create a post need to be logged in 
# so we will add a dependency in the create_posts function, get_current_user: int = Depends(oauth2.get_current_user)


# 2.when we add that dependency, anytime someone wants to access a resource that requires them to be logged in, we expect that 
# thet provide an access token, and it calls the function get_current_user

# 3.but where does the token actually come from, if i would guess, it is retrieved from the oauth2_scheme, where we passed in our token-url
# as login, and remember login function actually returns the access token.

# 4. In get_curent_user, we pass in the token that comes from the request, then run verify_access_token which will provide the logic for verifying
# the token is okay and also return the token-data


# NOTE: get_current_user is what actually calls the verify_access_token function, and when it does it expects us to return the token data
# and then it gives the data to 
def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Could not validate credentials',
                                          headers={"WWW-Authenticate":"Bearer"})

    # here we want to implement getting the user from the database from the token-data(id) that was passed in 
    token = verify_access_token(token, credentials_exception)    
    user =  db.query(models.User).filter(models.User.id == token.id).first()       
    print(user)

    # here we have successfully retreived the user based off of the id 
    return user                        



#QUESTION -> why do we have the get_current_user function when it mainly just calls the verify_access function.
# So the idea behind the get_current_user function is that once the verify function returns the token data which is the id 
# The get_current function should actually fetch the user from the database, that way we can attach the user to any path operation and
# perform any necessary logic 

# You dont have to implement it in the get_current function, if you want each of your path operations to  fetch the users themselves 
# they can because they have the id but un our case we will be doing it here in the get-current_user 