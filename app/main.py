from fastapi import FastAPI
from .models.todos import Todo
from .configs.db import collection_name
from .schema.schema import list_serial
from bson import ObjectId

app = FastAPI()

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

@app.put('/todos/${id}')
async def update_todo(id: str, todo : Todo):
    collection_name.find_one_and_update({"_id" : ObjectId(id)}, {"$set" : dict(todo)})
  

@app.delete('/todos/{id}')
async def delete_todo(id: str):
    collection_name.find_one_and_delete({"_id" : ObjectId(id)})