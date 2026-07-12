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


@app.get("/persons", response_model=List[Person])
def get_person():
    try:
        conn = getDBconnection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM persons ORDER BY id")

        persons = cursor.fetchall()

        return [Person(**person) for person in persons]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")    
    finally:
        if conn:
            cursor.close()
            conn.close()        


@app.get("/persons/{person_id}", response_model=Person)
def get_one_person(person_id: int):
    try:
        conn = getDBconnection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM  persons WHERE id = %s", (person_id,))
        person = cursor.fetchone()

        if not person:
            raise HTTPException(status_code=404, detail="Person not found") 
        
        return Person(**person)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            cursor.close()
            conn.close()


@app.put("/person/{person_id}", response_model=Person)
def update_person(person_id: int, updated_person: PersonUpdate):
    try:
        conn = getDBconnection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        cursor.execute("SELECT * FROM persons WHERE id = %s", (person_id))
        existing_person = cursor.fetchone()

        if not existing_person:
            raise HTTPException(status_code=400, detail='Person not found')
        
        update_fields = []
        params = []

        if updated_person.name is not None:
            update_fields.append("name = %s")
            params.append(updated_person.name)
        
        if updated_person.age is not None:
            update_fields.append("age = %s")
            params.append(updated_person.age)
        
        if not update_fields:
            # No fields to update, return existing person
            return Person(**existing_person) 
    
        params.append(person_id)
        query = f"UPDATE persons SET {','.join(update_fields)} WHERE id = %s RETURNING *"

        cursor.execute(query, params)
        updated = cursor.fetchone()
        conn.commit()

        return Person(**updated)
    
    except HTTPException:
        raise
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn:
            cursor.close()
            conn.close()
    







