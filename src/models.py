from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

# class User(Base):
#     __tablename__ = "user"

#     id = Column(Integer, primary_key=True, index=True)


class Jar(Base):
    __tablename__ = "jars"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    value = Column(Integer, index=True)
    # currency = Column(String, nullable=False)
