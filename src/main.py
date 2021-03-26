# from typing import List, Dict
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

import models, schemas, datetime
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


"""

ROUTINGS

"""

# redirect to docs
@app.get("/")
def home():
    return RedirectResponse("http://localhost:8000/docs/")

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

    log = models.History(jar_id=jar.id, jar_name=jar.name, change=request.value, date=datetime.datetime.utcnow(), title=request.title)
    db.add(log)
    db.commit()

    db.refresh(jar)
    return jar

# take from jar
@app.put("/jar/withdraw")
def withdraw(request : schemas.JarWithdraw, db: Session = Depends(get_db)):
    jar = db.query(models.Jar).get(request.id)
    jar.value -= abs(request.value)
    db.commit()

    log = models.History(jar_id=jar.id, jar_name=jar.name, change=-abs(request.value), date=datetime.datetime.utcnow(), title=request.title)
    db.add(log)
    db.commit()

    db.refresh(jar)
    return jar

# show all operations
@app.get("/history")
def history(db: Session = Depends(get_db)):
    return db.query(models.History).all()

# sort operations
@app.get("/history/sort/sort={sort_type}")
def sort_operations(sort_type : str, db: Session = Depends(get_db)):
    if sort_type == "date":
        query = db.query(models.History).order_by(desc(models.History.date)).all()
        return query
    elif sort_type == "value":
        query = db.query(models.History).order_by(desc(models.History.change)).all()
        return query
    elif sort_type == "title":
        query = db.query(models.History).order_by(asc(models.History.title)).all()
        return query

# transfers between jars
@app.put("/jar/transfer")
def transfer(request : schemas.Transfer, db: Session = Depends(get_db)):
    from_jar = db.query(models.Jar).get(request.from_id)
    to_jar = db.query(models.Jar).get(request.to_id)
    
    from_jar.value -= request.value
    to_jar.value += request.value
    db.commit()

    log = models.Transfers(from_id=from_jar.id, to_id=to_jar.id)
    db.add(log)
    db.commit()


    return {"msg" : "Transfer completed"}
    
