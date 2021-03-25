from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from db import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/jar/create/name={jar_name}", response_model=schemas.Jar)
def create_jar(Jar: schemas.JarCreate, db: Session = Depends(get_db)):
    return crud.create_jar(db=db, Jar=Jar)