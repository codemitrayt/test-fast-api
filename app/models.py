from pydantic import BaseModel

class Todo(BaseModel):
    name : str
    description : str
    isCompleted : bool
    
class SignUp(BaseModel):
    fullName : str
    email : str
    password : str
    confirmPassword : str


class Token(BaseModel):
    token : str
    
class Login(BaseModel):
    email: str
    password : str