from sqlalchemy.orm import Session

import models
from main import app

@app.get("/")
def read_root():
    return {"Hello": "World"}

# list all jars
@app.get("/jars/")
async def list_jars():
    return {"msg" : "list of all jars"}


# create jar
@app.get("/jars/create/name={jar_name}")
async def jar_create(jar_name):
    return {"msg" : "Jar {} created!".format(jar_name)}

# add to jar


# take from jar