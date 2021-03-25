from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Jar(Base):
    __tablename__ = "jars"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    value = Column(Integer, index=True)
