from sqlalchemy.orm import Session
from . import models


def get_search(db: Session, search_id: int):
    return db.query(models.Search).filter(models.Search.id == search_id).first()

def get_searchs(db: Session):
    return db.query(models.Search).all()

def create_search(db: Session, search: models.Search):
    db_var = models.Search(
        seq = search.seq,
        lables = search.lables,
        scores = search.scores
    )
    db.add(db_var)
    db.commit()
    db.refresh(db_var)
    return db_var

