from passlib.context import CryptContext


# for the password hash, here we are specifying the hashing algorithm that we want to use, in this case bcrypt
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

#user passes in a password of type string and then it gets hashed
def hash(password: str):
    return pwd_context.hash(password)


# Function to compare the two passwords 
def verify(plain_password, hashed_password):
    # note that this .verify performs the logic of combining the both of then and it comes from the passlib 
    return pwd_context.verify(plain_password, hashed_password)
