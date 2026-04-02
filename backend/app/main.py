import os
from fastapi import FastAPI
from fastapi import Depends, UploadFile, File
from sqlalchemy.orm import session
from app.database import SessionLocal
from app.database import get_db
from app.database import engine
from app import models, crud
from app.tasks import process_document
from fastapi.responses import JSONResponse
import redis
import json
from fastapi.responses import StreamingResponse
import io
import csv
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)


models.Base.metadata.create_all(bind=engine)

UPLOAD_DIR = "uploads"

@app.get("/")
def root():
    return {"message": "API running"}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload")
def upload_file(file: UploadFile = File(...), db: session = Depends(get_db)):

    if not file.filename:
        return {"error": "No file uploaded"}

    if not file.filename.endswith((".txt", ".pdf", ".jpg", ".png")):
        return {"error": "Unsupported file type"}

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    doc = crud.create_document(
        db,
        filename=file.filename,
        filepath=file_path
    )

    process_document.delay(doc.id)

    return {
        "message": "File uploaded",
        "document_id": doc.id
    }

@app.get("/documents")
def get_documents(db: session = Depends(get_db)):
    return db.query(models.Document).all()    

@app.get("/documents/{document_id}")
def get_document(document_id: int, db: session = Depends(get_db)):
    doc = crud.get_document(db, document_id=document_id)

    if not doc:
        return {"error": "Document not found"}

    return {
        "id": doc.id,
        "filename": doc.filename,
        "status": doc.status,
        "progress": doc.progress,
        "result": doc.result,
        "error": doc.error_message
    }

@app.get("/progress")
def get_progress():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("document_progress")

    message = pubsub.get_message(timeout=1)

    if message and message["type"] == "message":
        return json.loads(message["data"])

    return {"message": "No new updates"}

from app.tasks import process_document

@app.post("/retry/{doc_id}")
def retry_document(doc_id: int, db: session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()

    if not doc:
        return {"error": "Document not found"}

    doc.status = "queued"
    doc.progress = 0
    db.commit()

    process_document.delay(doc.id)

    return {"message": "Retry triggered"}

@app.put("/documents/{doc_id}")
def update_document(doc_id: int, data: dict, db: session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()

    if not doc:
        return {"error": "Document not found"}

    doc.result = data.get("result", doc.result)
    db.commit()

    return {"message": "Document updated"}

@app.post("/documents/{doc_id}/retry")
def retry_document(doc_id: int, db: session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()

    if not doc:
        return {"error": "Document not found"}

    if doc.status != "failed":
        return {"message": "Only failed documents can be retried"}

    # reset state
    doc.status = "queued"
    doc.progress = 0
    doc.error_message = None
    db.commit()

    # trigger again
    process_document.delay(doc.id)

    return {"message": "Retry started"}

@app.put("/documents/{doc_id}/finalize")
def finalize_document(doc_id: int, db: session = Depends(get_db)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()

    if not doc:
        return {"error": "Document not found"}

    doc.is_finalized = True
    db.commit()

    return {"message": "Document finalized"}

@app.get("/documents/export/json")
def export_json(db: session = Depends(get_db)):
    docs = db.query(models.Document).filter(models.Document.is_finalized == True).all()

    result = []

    for doc in docs:
        result.append({
            "id": doc.id,
            "filename": doc.filename,
            "status": doc.status,
            "result": doc.result
        })

    return JSONResponse(content=result)

@app.get("/documents/export/csv")
def export_csv(db: session = Depends(get_db)):
    docs = db.query(models.Document).filter(models.Document.is_finalized == True).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # header
    writer.writerow(["id", "filename", "status", "title", "category", "summary"])

    for doc in docs:
        result = doc.result or {}
        writer.writerow([
            doc.id,
            doc.filename,
            doc.status,
            result.get("title"),
            result.get("category"),
            result.get("summary")
        ])

    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=documents.csv"
    })

@app.get("/documents/{doc_id}/progress")
def get_progress(doc_id: int):
    data = redis_client.get(f"doc:{doc_id}")

    if not data:
        return {"message": "No updates yet"}

    return json.loads(data)