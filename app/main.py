from fastapi import FastAPI # type: ignore 

app = FastAPI() 


@app.get('/')
def index():
    return {'message': 'Hello World'}