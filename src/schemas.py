from typing import List, Optional

from pydantic import BaseModel

# schema for displaying jar
class Jar(BaseModel):
    id : int
    name : str
    value : int
    
    class Config():
        orm_mode = True

# schema for jar creation
class JarCreate(BaseModel):
    name : str

# schema for jar operations
class JarOperation(BaseModel):
    id : int
    value : int
    title : str

# schema for displaying all operations for a jar
class History(BaseModel):    
    title : str
    value : int
    date : str
    operation_type : str
    
    class Config():
        orm_mode = True

# schema for transfering
class Transfer(BaseModel):
    from_jar : int
    to_jar : int
    value : int
    title : str
