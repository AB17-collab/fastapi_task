from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "Arnab Deb"}

@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"Hello, {name}!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, item: Optional[str] = None, free: Optional[str] = None):
    return {"item_id": item_id, "item": item, "free": free}

@app.get("/status")
def get_status():
    return {"status": "API is running smoothly"}

class Student(BaseModel):
    name: str
    age: int
    roll: int

@app.post("/create_student")
def create_student(student: Student):   
    return {
        "name": student.name,
        "age": student.age,
        "roll": student.roll
    }
