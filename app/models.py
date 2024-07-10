from pydantic import BaseModel

class Todo(BaseModel):
    name : str
    description : str
    isCompleted : bool
    
class SignUp(BaseModel):
    first_name : str
    last_name : str
    email : str
    password : str
    confirm_password :  str
