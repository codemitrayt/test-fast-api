import bcrypt
import json
import time
import smtplib
from jose import jws
from bson import ObjectId
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from .schema import list_serial, individual_serial_user
from .models import Todo, SignUp, Token, Login
from fastapi import FastAPI, HTTPException
from .configs.db import collection_name, user_collection
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

SECRET_KEY = "thisisjwtsecretkey"
ALGORITHM = "HS256"
TOKEN_EXPIRE_DAYS = 15

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    
def create_jwt_token(payload : dict):
    to_encode = payload.copy()
    jwt_token = jws.sign(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token

def verify_jwt_token(token):
    return jws.verify(token, SECRET_KEY, algorithms=ALGORITHM)


@app.post('/auth/sign-up')
async def signup(request : SignUp):
    data = dict(request).copy()
    user = user_collection.find_one({'email' : dict(request).get('email')})
    if user:
        raise HTTPException(status_code=400, detail='Email already exists')
    
    if dict(request).get('password') != dict(request).get('confirmPassword'):
        raise HTTPException(status_code=400, detail='Passwords does not match')

    dt = datetime.now(tz=timezone.utc) + timedelta(minutes=5)
    exp = time.mktime(dt.timetuple())
    data.update({'exp': exp})
    jwt_token = create_jwt_token(data)

    verification_link = f"https://workable-ai-official.vercel.app/auth/verify-email?token={jwt_token}"  # Construct the verification link
    msg = MIMEMultipart()
    msg['From'] = 'themailbot0@gmail.com'
    msg['To'] = data.get('email')
    msg['Subject'] = 'Verify Your Email'
    msg.attach(MIMEText(f'Please click on the link to verify your email: {verification_link}', 'plain'))

    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], 'ookogfiezrelknno')
    server.send_message(msg)
    server.quit()

    return {'message' : "Verify link sent successfully", "ok" : True}

@app.post('/auth/verify-email')
async def verify_email(request : Token):
    try:
        token_user = verify_jwt_token(dict(request).get('token'))
        user = json.loads(token_user)
    
        exist = user_collection.find_one({'email' : dict(user).get('email')})
        if exist:
            return HTTPException(status_code=400, detail='Email already exists')

        hash_password = get_password_hash(dict(user).get('password'))
        user_collection.insert_one({'email' : dict(user).get('email'), 'password' : hash_password, 'fullName' : dict(user).get('fullName')})
      
        dt = datetime.now(tz=timezone.utc) + timedelta(days=30)
        exp = time.mktime(dt.timetuple())
        jwt_token = create_jwt_token({'email' : dict(user).get('email'), 'exp' : exp})
        print(jwt_token) 

        return {'jwt_token': jwt_token, 'user': {'email': dict(user).get('email'), 'fullName': dict(user).get('fullName')}}
    
    except Exception as e:
        return HTTPException(status_code=400, detail='Invalid token')


@app.post('/auth/self')
async def get_user_info(request : Token):
    try:
        token_user = verify_jwt_token(dict(request).get('token'))
        user = json.loads(token_user)

        user_info = user_collection.find_one({'email' : dict(user).get('email')})
        if not user_info:
            raise HTTPException(status_code=401, detail='User not found')

        return {'user': individual_serial_user(user_info)}

    except Exception as e:
        return HTTPException(status_code=401, detail='Invalid token')
    

@app.post('/auth/login')
async def login(request : Login):
    user = user_collection.find_one({'email' : dict(request).get('email')})
    if not user:
        raise HTTPException(status_code=400, detail='Invalid email or password')
    
    if not verify_password(dict(request).get('password'), user['password']):
        raise HTTPException(status_code=400, detail='Invalid email or password')
    
    dt = datetime.now(tz=timezone.utc) + timedelta(days=30)
    exp = time.mktime(dt.timetuple())
    token = create_jwt_token({'email' : dict(request).get('email'), 'exp' : exp})
    
    return {'jwt_token': token, "user" : {'email' : user['email'], 'fullName' : user['fullName']}}