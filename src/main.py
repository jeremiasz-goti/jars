from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

# list all jars
@app.get("/jars/")
async def list_jars():
    return {"msg" : "list of all jars"}


# create jar with currency attached

@app.get("/jars/create/name={jar_name}&currency={currency}")
async def jar_create(jar_name, currency):
    if currency not in ["PLN", "USD", "EUR"]:
        return {"msg" : "Unsupported currency"}
    else:
        return {"msg" : "Jar {} created! Chosen currency: {}".format(jar_name, currency)}

# add to jar


# take from jar