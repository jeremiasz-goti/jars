from typing import List, Optional
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from sqlalchemy import desc, asc
from sqlalchemy.orm import Session

import models, schemas, datetime

from schemas import SortModel, CurrencyModel 
from database import SessionLocal, engine, get_db

# create tables in database
models.Base.metadata.create_all(bind=engine)

# initialize app
app = FastAPI()

# --- ROUTINGS ---

# redirect to docs
@app.get("/", tags=["Docs"])
def home():
    return RedirectResponse("http://localhost:8000/docs/")

# create jar
@app.post("/createjar", status_code=status.HTTP_201_CREATED, response_model=schemas.Jar, tags=["Jars"])
def create(name : str, request : schemas.JarCreate, currency: CurrencyModel = "PLN", db: Session = Depends(get_db)):
    # check for existing jars
    jar = db.query(models.Jar).filter(models.Jar.name == name).first()
    if jar:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail={'detail' : 'Jar with name {} already exists!'.format(name)})
    else:
        # commit to database    
        jar = models.Jar(name=name, value=0, currency=currency)
        db.add(jar)
        db.commit()
        db.refresh(jar)
        log = models.AccountHistory(jar_id=jar.id, value=0, date=datetime.datetime.utcnow(), title="Jar created", operation_type="Create jar")
        db.add(log)
        db.commit()        
        return jar

# list all jars
@app.get("/jars/", response_model=List[schemas.Jar], tags=["Jars"])
def list_jars(db: Session = Depends(get_db)):
    return db.query(models.Jar).all()

# show and sort jar specific operations
@app.get("/jars/{jar_id}", response_model=List[schemas.History], tags=["Jars"])
def jar_history(jar_id: int, order_by: SortModel = "date", db: Session = Depends(get_db)):
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
            return db.query(models.AccountHistory).filter(models.AccountHistory.jar_id == jar_id).order_by(desc(models.AccountHistory.value)).all()

        # sort by title    
        elif order_by == SortModel.title:
            return db.query(models.AccountHistory).filter(models.AccountHistory.jar_id == jar_id).order_by(desc(models.AccountHistory.title)).all()
    
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"detail" : f'Wrong sorting type - use date, value or title'})


# add resources to jar
@app.put("/jars/{jar_id}/deposit/value={value}&title={title}", response_model=schemas.Jar, tags=["Jar Operations"])
def deposit(request : schemas.JarOperation, jar_id : int, value : int, title : Optional[str] = "Deposit", db : Session = Depends(get_db)):
    jar = db.query(models.Jar).get(jar_id)
    # check if jar exists
    if not jar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'detail' : 'No jar with id {}'.format(request.id)})
    # check if input is
    if value <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'detail' : 'Can`t add negative values or 0'})
    else:
        # commit to database
        jar.value += value
        log = models.AccountHistory(jar_id=jar.id, value=value, date=datetime.datetime.utcnow(), title=title, operation_type="Deposited {} in jar {}".format(value, jar.id ))
        db.add(log)
        db.commit()
        db.refresh(jar)
        return jar

# withdraw resources from jar
@app.put("/jars/{jar_id}/withdraw/value={value}&title={title}", response_model=schemas.Jar, tags=["Jar Operations"])
def withdraw(request : schemas.JarOperation, jar_id : int, value : int, title : Optional[str] = "Deposit", db : Session = Depends(get_db)):
    jar = db.query(models.Jar).get(jar_id)
    # check if jar exists
    if not jar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'detail' : 'No jar with id {}'.format(request.id)})
    if value <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'detail' : 'Use positive values'})
    if request.value > jar.value:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'detail' : "Not enough resources"})
    else:
        jar.value -= value
        # check if jar has the resources for withdraw
        if jar.value < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'detail' : f'Withdraw cannot be larger than the ammount of resources in the jar'})
        else:
            # commit to database
            log = models.AccountHistory(jar_id=jar.id, value=value, date=datetime.datetime.utcnow(), title=request.title, operation_type="Withdrawed {} from jar {}".format(value, jar.id ))
            db.add(log)
            db.commit()
            db.refresh(jar)
            return jar

# send resources from jar to jar
@app.put("/jars/{jar_id}/send/to={to_jar}&value={value}&title={title}", tags=["Jar Operations"])
def send(jar_id : int, to_jar : int, value : int, title : str, request : schemas.Transfer, db : Session = Depends(get_db)):
    # define sender and reciver
    from_jar = db.query(models.Jar).get(jar_id)
    to_jar = db.query(models.Jar).get(to_jar)
    # check if given jars exist
    if not from_jar or not to_jar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'detail' : f'Wrong jar id'})

    elif from_jar.currency != to_jar.currency:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'detail' : f'Wrong currency'})

    else:
        # check if sender has the resources for payment        
        from_jar.value -= value
        if from_jar.value < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'detail' : f'Not enough resources'})
        else:
            # commit to database
            to_jar.value += value
            db.commit()
            sender_log = models.AccountHistory(jar_id=from_jar.id, value=value, date=datetime.datetime.utcnow(), title=title, operation_type="Transfered {} from jar {} to jar {}.".format(value, from_jar.id, to_jar.id))
            db.add(sender_log)
            reciver_log = models.AccountHistory(jar_id=to_jar.id, value=value, date=datetime.datetime.utcnow(), title=title, operation_type="Recived {} from jar {}.".format(value, from_jar.id))
            db.add(reciver_log)
            db.commit()
            return {"msg" : "Transfer completed"}