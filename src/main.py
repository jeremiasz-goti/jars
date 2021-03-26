from typing import List
from enum import Enum
from fastapi import Depends, FastAPI, HTTPException, status
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
@app.post("/jar", status_code=status.HTTP_201_CREATED, response_model=schemas.Jar)
def create(request : schemas.JarCreate, db: Session = Depends(get_db)):
    new_jar = models.Jar(name=request.name, value=(abs(request.value)))
    db.add(new_jar)
    db.commit()
    db.refresh(new_jar)
    return new_jar

# list jars
@app.get("/jar/all", response_model=List[schemas.Jar])
def list_jars(db: Session = Depends(get_db)):
    return db.query(models.Jar).all()


# deposit and withdraw resources from specific jar
@app.put("/jar/operations", response_model=schemas.Jar)
def operations(request : schemas.JarOperation, db: Session = Depends(get_db)):
    jar = db.query(models.Jar).get(request.id)
    # check if jar exists
    if not jar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'detail' : f'No jar with id: '+ str(request.id)})
    else:
        jar.value += request.value
        # check if jar has the resources for withdraw
        if jar.value < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={'detail' : f'Withdraw cannot be larger than the ammount of resources in the jar'})
        else:
            db.commit()
            log = models.History(jar_id=jar.id, jar_name=jar.name, change=request.value, date=datetime.datetime.utcnow(), title=request.title)
            db.add(log)
            db.commit()
            db.refresh(jar)
            return jar


# transfers between jars
@app.put("/jar/transfer")
def transfer(request : schemas.Transfer, db: Session = Depends(get_db)):
    from_jar = db.query(models.Jar).get(request.from_id)
    to_jar = db.query(models.Jar).get(request.to_id)
    if not from_jar or not to_jar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'detail' : f'Wrong jar id'})
    else:        
        from_jar.value -= request.value
        to_jar.value += request.value
        db.commit()

        log = models.Transfers(from_id=from_jar.id, to_id=to_jar.id, value=request.value, date=datetime.datetime.utcnow())
        db.add(log)
        db.commit()

        return {"msg" : "Transfer completed"}

# show all operations
@app.get("/history")
def history(db: Session = Depends(get_db)):
    return db.query(models.History).all()

# show all transfers
@app.get("/history/transfers")
def transfers_history(db: Session = Depends(get_db)):
    return db.query(models.Transfers).order_by(desc(models.Transfers.date)).all()



class SortModel(str, Enum):
    date = "date"
    value = "value"
    title = "title"

# sort operations
@app.get("/history/sort/sort={sort_type}")
def sort_operations(sort_type : SortModel, db: Session = Depends(get_db)):
    if sort_type == SortModel.date:
        return db.query(models.History).order_by(desc(models.History.date)).all()

    elif sort_type == SortModel.value:
        return db.query(models.History).order_by(desc(models.History.change)).all()

    elif sort_type == SortModel.title:
        return db.query(models.History).order_by(asc(models.History.title)).all()

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"detail" : f'Wrong sorting type - use date, value or title'})
