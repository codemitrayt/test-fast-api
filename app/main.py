from fastapi import FastAPI, HTTPException
from .models import Todo, SignUp
from .configs.db import collection_name, user_collection
from .schema import list_serial
from bson import ObjectId
import bcrypt

app = FastAPI()

# Hash a password using bcrypt
def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password

# Check if the provided password matches the stored password (hashed)
def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password)

@app.get('/')
def index():
    return {'message': 'Hello, World!'}

@app.get('/todos')
async def get_todos():
    todos = list_serial(collection_name.find())
    return todos

@app.post('/todos')
async def create_todo(todo: Todo):
      collection_name.insert_one(dict(todo))

@app.put('/todos/{id}')
async def update_todo(id: str, todo : Todo):
    collection_name.find_one_and_update({"_id" : ObjectId(id)}, {"$set" : dict(todo)})
  

@app.delete('/todos/{id}')
async def delete_todo(id: str):
    collection_name.find_one_and_delete({"_id" : ObjectId(id)})


@app.post('/auth/signup')
async def signup(request : SignUp):
    user = user_collection.find_one({'email' : dict(request).get('email')})
    if user:
        raise HTTPException(status_code=400, detail='Email already exists')
    
    if dict(request).get('password') != dict(request).get('confirm_password'):
        raise HTTPException(status_code=400, detail='Passwords do not match')
    
    hash_password = get_password_hash(dict(request).get('password'))
    
    return {'message': 'User signed up successfully'}