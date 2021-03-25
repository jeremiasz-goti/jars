from typing import List, Optional

from pydantic import BaseModel

# base model interpretation
class JarBase(BaseModel):
    name: str
    # currency: str
    value: int

# for creation
class JarCreate(JarBase):
    pass

# for reading
class Jar(BaseModel):

    id : int
    name : str
    # currency : str
    value : int

    class Config:
        orm_mode = True