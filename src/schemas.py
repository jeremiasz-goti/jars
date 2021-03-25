from typing import List, Optional

from pydantic import BaseModel

# schema for jar creation
class JarCreate(BaseModel):
    name: str
    value: int

# schema for displaying jar
class Jar(BaseModel):
    id : int
    name : str
    value : int

# schema for adding to the jar
class JarDeposit(BaseModel):
    id : int
    value : int

# schema for taking from the jar
class JarWithdraw(BaseModel):
    id : int
    value : int
