from typing import List
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine

# create tables in database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/jar")
def create(request : schemas.Jar, db: Session = Depends(get_db)):
    new_jar = models.Jar(name=request.name, value=(abs(request.value)))
    db.add(new_jar)
    db.commit()
    db.refresh(new_jar)
    return new_jar
