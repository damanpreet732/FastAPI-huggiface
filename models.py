from sqlalchemy import Column, Integer, String
from .database import Base

class Search(Base):
    __tablename__ = "search"

    id = Column(Integer, primary_key=True, index=True)
    seq = Column(String, unique=True, index=True)
    lables = Column(String, unique=True, index=True)
    scores = Column(String, unique=True, index=True)

