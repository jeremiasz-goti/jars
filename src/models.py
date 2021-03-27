from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Jar(Base):
    __tablename__ = "jars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True, nullable=False)
    value = Column(Integer, index=True)

class AccountHistory(Base):
    __tablename__ = "account_history"
    
    id = Column(Integer, primary_key=True, index=True)
    jar_id = Column(Integer, index=True)
    value = Column(Integer)
    date = Column(String, index=True)
    title = Column(String, index=True)
    operation_type = Column(String)

    

