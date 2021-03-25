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


# create jar
@app.post("/jar")
def create(request : schemas.JarCreate, db: Session = Depends(get_db)):
    new_jar = models.Jar(name=request.name, value=(abs(request.value)))
    db.add(new_jar)
    db.commit()
    db.refresh(new_jar)
    return new_jar

# list jars
@app.get("/jar/all")
def list_jars(db: Session = Depends(get_db)):
    return db.query(models.Jar).all()


# add to jar
@app.put("/jar/deposit")
def deposit(request : schemas.JarDeposit, db: Session = Depends(get_db)):
    jar = db.query(models.Jar).get(request.id)
    jar.value += abs(request.value)
    db.commit()
    db.refresh(jar)
    return jar

# take from jar
@app.put("/jar/withdraw")
def withdraw(request : schemas.JarWithdraw, db: Session = Depends(get_db)):
    jar = db.query(models.Jar).get(request.id)
    jar.value -= abs(request.value)
    db.commit()
    db.refresh(jar)
    return jar

# show and sort jar operations