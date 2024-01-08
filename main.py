from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from sqlalchemy import Column, Integer, String
# from .database import Base

class Search(Base):
    __tablename__ = "search"
    id = Column(Integer, primary_key=True, index=True,autoincrement= "auto")
    seq = Column(String, index=True)
    labels = Column(String, index=True)
    scores = Column(String, index=True)

from pydantic import BaseModel

class SearchBase(BaseModel):
    seq: str
    labels: list

class SearchCreate(SearchBase):
    scores: list

class SearchResponse(SearchBase):
    id: int
    seq : str
    labels : list
    scores : list
    class Config:
        orm_mode = True


from sqlalchemy.orm import Session
# from . import models


def get_search(db: Session, search_id: int):
    return dbToSchema(db.query(Search).filter(Search.id == search_id).first())

# for loop needed
def get_searchs(db: Session):
    results : list[SearchResponse] = []
    for serach in db.query(Search).all():
        results.append(dbToSchema(serach))
    return results
    

def create_search(db: Session, search: SearchBase):
    result = pipe(search.__getattribute__('seq'),search.__getattribute__('labels'))
    modifiedSearch : SearchCreate = {
        'seq' : result['sequence'],
        'labels' : '#'.join(result['labels']),
        'scores' : '#'.join(map(str,result['scores'])),
    }
    db_var = Search(
        seq = modifiedSearch['seq'],
        labels = modifiedSearch['labels'],
        scores = modifiedSearch['scores']
    )
    db.add(db_var)
    db.commit()
    db.refresh(db_var)

    if(db_var):
        arr = result['scores']
        max_value = max(arr)
        idx : int = arr.index(max_value)
        return result['labels'][idx]

    return "DONT KNOW"


def dbToSchema (db : Search):
    schema : SearchResponse = {
        'id' : db.__getattribute__('id'),
        'seq' : db.__getattribute__('seq'),
        'lables' : str (db.__getattribute__('labels')).split('#'),
        'scores' : str (db.__getattribute__('scores')).split('#'),
    }
    return schema

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from transformers import pipeline
# import crud,models
# from .database import SessionLocal, engine

Base.metadata.create_all(bind=engine)
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

pipe = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

@app.get("/")
def example():
    ex_seq = 'I have a problem with my iphone that needs to be resolved asap!!'
    ex_lables = ['urgent', 'not urgent', 'phone', 'tablet', 'computer']
    result = pipe(ex_seq,ex_lables)
    return result

@app.get("/searchs/{id}",response_model=SearchResponse)
def read_search(id: int, db: Session = Depends(get_db)):
    db_result = get_search(db, search_id=id)
    if db_result is None:
        raise HTTPException(status_code=404, detail="Search not found")
    return db_result

@app.get("/searchs/",response_model=list[SearchResponse])
def read_searchs(db: Session = Depends(get_db)):
    searchs = get_searchs(db)
    return searchs

@app.post("/searchs/",response_model=str)
def add_search(search : SearchBase, db: Session = Depends(get_db)):
# def add_search(db: Session = Depends(get_db)):
    # search : SearchBase = {
    #     'seq' : 'I have a problem with my iphone that needs to be resolved asap!!',
    #     'labels' : ['urgent', 'not urgent', 'phone', 'tablet', 'computer']
    # }
    return create_search(db,search)
