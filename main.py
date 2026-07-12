from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2 
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

app = FastAPI()

load_dotenv()

database_url = os.getenv("DATABASE_URL")

class PersonCreate(BaseModel):
    name: str
    age: int

class Person(BaseModel):
    id: int
    name: str
    age: int

class PersonUpdate(BaseModel):
    name: str
    age: int


def getDBconnection():
    return psycopg2.connect(database_url)

def init_database():
    try:
        conn = getDBconnection()
        cursor = conn.cursor()

        conn.commit()
        print("Database connected successfully")
    
    except Exception as e:
        print("Database initialization failed")
    
    finally:
        if conn:
            cursor.close()
            conn.close()



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
            persons[index] = updatedPerson
            return updatePerson
    
    return {"message": "Person not found"}

@app.delete("/persons/{person_id}")
def deletePerson(person_id):
    for index, person in enumerate(persons):
        if person_id == person.id:
            deletedPerson = persons.pop(index)
            return deletedPerson
        
    return {"message": "Person not found. Delete failed"}

