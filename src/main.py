from typing import List
from enum import Enum
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

import models, schemas, datetime
from database import SessionLocal, engine, get_db

# create tables in database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- ROUTINGS ---

# redirect to docs
@app.get("/")
def home():
    return RedirectResponse("http://localhost:8000/docs/")

# create jar
@app.post("/createjar", status_code=status.HTTP_201_CREATED, response_model=schemas.Jar)
def create(request : schemas.JarCreate, db: Session = Depends(get_db)):
    # check for existing jars
    jar = db.query(models.Jar).filter(models.Jar.name == request.name).first()
    print(jar)
    if jar:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail={'detail' : 'Jar with name {} already exists!'.format(request.name)})
    else:
        # commit to db and log opperation    
        jar = models.Jar(name=request.name, value=0)
        db.add(jar)
        db.commit()
        db.refresh(jar)
        log = models.AccountHistory(jar_id=jar.id, value=0, date=datetime.datetime.utcnow(), title="Jar created", operation_type="Create jar")
        db.add(log)
        db.commit()        
        return jar

# list jars
@app.get("/all", response_model=List[schemas.Jar])
def list_jars(db: Session = Depends(get_db)):
    return db.query(models.Jar).all()

# model for sorting operations
class SortModel(str, Enum):
    date = "date"
    value = "value"
    title = "title"

# show and sort jar specific operations
@app.get("/{jar_id}", response_model=List[schemas.History])
def history(jar_id: int, order_by: SortModel = "date", db: Session = Depends(get_db)):
    # check if jar exists
    jar = db.query(models.Jar).get(jar_id)
    if not jar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'detail' : 'No jar with id {} '.format(jar_id)})
    else:
        # sort data acording to order_by variable by descending

        # sort by date
        if order_by == SortModel.date:
            return db.query(models.AccountHistory).filter(models.AccountHistory.jar_id == jar_id).order_by(desc(models.AccountHistory.date)).all()

        # sort by value    
        elif order_by == SortModel.value: 
            return db.query(models.AccountHistory).filter(models.AccountHistory.jar_id == jar_id).order_by(asc(models.AccountHistory.value)).all()

        # sort by title    
        elif order_by == SortModel.title:
            return db.query(models.AccountHistory).filter(models.AccountHistory.jar_id == jar_id).order_by(asc(models.AccountHistory.title)).all()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"detail" : f'Wrong sorting type - use date, value or title'})


# add to jar
@app.put("/deposit", response_model=schemas.Jar)
def deposit(request : schemas.JarOperation, db: Session = Depends(get_db)):
    jar = db.query(models.Jar).get(request.id)
    # check if jar exists
    if not jar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'detail' : 'No jar with id {}'.format(request.id)})
    else:
        jar.value += request.value
        log = models.AccountHistory(jar_id=jar.id, value=request.value, date=datetime.datetime.utcnow(), title=request.title, operation_type="Deposited {} in jar {}".format(request.value, jar.id ))
        db.add(log)
        db.commit()
        db.refresh(jar)
        return jar

# take from jar
@app.put("/withdraw", response_model=schemas.Jar)
def withdraw(request : schemas.JarOperation, db: Session = Depends(get_db)):
    jar = db.query(models.Jar).get(request.id)
    # check if jar exists
    if not jar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'detail' : 'No jar with id {}'.format(request.id)})
    else:
        jar.value -= request.value
        # check if jar has the resources for withdraw
        if jar.value < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'detail' : f'Withdraw cannot be larger than the ammount of resources in the jar'})
        else:
            log = models.AccountHistory(jar_id=jar.id, value=request.value, date=datetime.datetime.utcnow(), title=request.title, operation_type="Withdrawed {} from jar {}".format(request.value, jar.id ))
            db.add(log)
            db.commit()
            db.refresh(jar)
            return jar

# send money
@app.put("/send")
def send(request : schemas.Transfer, db: Session = Depends(get_db)):
    # define sender and reciver
    from_jar = db.query(models.Jar).get(request.from_jar)
    to_jar = db.query(models.Jar).get(request.to_jar)
    # check if given jars exist
    if not from_jar or not to_jar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'detail' : f'Wrong jar id'})
    else:
        # check if sender has the resources for payment        
        from_jar.value -= request.value
        if from_jar.value < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'detail' : f'Not enough resources'})
        else:
            to_jar.value += request.value
            db.commit()
            sender_log = models.AccountHistory(jar_id=from_jar.id, value=request.value, date=datetime.datetime.utcnow(), title=request.title, operation_type="Transfered {} from jar {} to jar {}.".format(request.value, from_jar.id, to_jar.id))
            db.add(sender_log)
            reciver_log = models.AccountHistory(jar_id=to_jar.id, value=request.value, date=datetime.datetime.utcnow(), title=request.title, operation_type="Recived {} from jar {}.".format(request.value, from_jar.id))
            db.add(reciver_log)
            db.commit()
            return {"msg" : "Transfer completed"}