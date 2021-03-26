from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Jar(Base):
    __tablename__ = "jars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    value = Column(Integer, index=True)


class History(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True)
    jar_id = Column(Integer, index=True)
    jar_name = Column(String, index=True, nullable=False)
    change = Column(Integer)
    date = Column(String, index=True)
    title = Column(String, index=True)

    

