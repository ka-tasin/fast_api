from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2 
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os
from contextlib import asynccontextmanager

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



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")

    init_database()
    yield

    print("Shutting down...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def get_root():
    return {"message": "Welcome to person application"}


@app.post("/persons", response_model=Person)
def create_person(person: Person):
        try: 
            conn = getDBconnection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(
                "INSERT INTO persons (name, age) VALUES (%s, %s) RETURNING *",
                (person.name, person.age)
            )

            new_person = cursor.fetchone()
            conn.commit()

            return Person(**new_person)
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")            
        finally:
            if conn:
                cursor.close()
                conn.close()



