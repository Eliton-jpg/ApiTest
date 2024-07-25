from sqlalchemy import Column, Integer, String
from database import Base

class Person(Base):
    __tablename__ = "people"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    cidade = Column(String, index=True)
