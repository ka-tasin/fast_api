from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Person(BaseModel):
    id: int
    name: str
    age: int


persons: List[Person] = []


@app.get('/')
def getPerson():
    return {"message": "Welcome to person route"}

@app.get("/persons")
def getAllPerson():
    return persons

@app.post("/persons")
def addPerson(person: Person):
    persons.append(person)
    return persons

@app.put("/persons/{person_id}")
def updatePerson(person_id: int, updatedPerson: Person):
    for index, person in enumerate(persons):
        if person.id == person_id:
            person[index] = updatedPerson
            return updatePerson
    
    return {"message": "Person not found"}

