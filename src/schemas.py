from typing import List, Optional
from enum import Enum

from pydantic import BaseModel

# schema for sorting operations
class SortModel(str, Enum):
    date = "date"
    value = "value"
    title = "title"

class CurrencyModel(str, Enum):
    PLN = "PLN"
    USD = "USD"
    EUR = "EUR"

# schema for displaying jar
class Jar(BaseModel):
    id : int
    name : str
    value : int
    currency : str
    
    class Config():
        orm_mode = True

# schema for jar creation
class JarCreate(BaseModel):
    name : str
    currency : str

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
    to_jar : int
    value : int
    title : str

