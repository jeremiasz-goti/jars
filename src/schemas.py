from typing import List, Optional

from pydantic import BaseModel

# schema for jar creation
class JarCreate(BaseModel):
    name : str
    value : int

# schema for displaying jar
class Jar(BaseModel):
    id : int
    name : str
    value : int
    
    class Config():
        orm_mode = True

# schema for taking from the jar
class JarOperation(BaseModel):
    id : int
    value : int
    title : str

# schema for displaying all operations for a jar
class History(BaseModel):
    jar_id : int
    jar_name : str
    change : int
    date : str
    title : str

# schema for transfering
class Transfer(BaseModel):
    from_id : int
    to_id : int
    value : int
