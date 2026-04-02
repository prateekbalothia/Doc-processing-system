from sqlalchemy.orm import session
from app import models

def create_document(db, filename: str, filepath: str):
    doc = models.Document(
        filename=filename,
        filepath=filepath
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_document(db, document_id: int):
    return db.query(models.Document).filter(models.Document.id == document_id).first()