import time
import redis
import json
from celery import Celery
from app.database import SessionLocal
from app import models

redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)

def publish_progress(doc_id, status, progress):
    event = {
        "doc_id": doc_id,
        "status": status,
        "progress": progress
    }
    redis_client.set(f"doc:{doc_id}", json.dumps(event))
    redis_client.publish("document_progress", json.dumps(event))

celery = Celery(
    "worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery.task
def process_document(doc_id: int):
    db = SessionLocal()
    
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()

    try:
        doc.status = "processing"
        doc.progress = 10
        db.commit()

        publish_progress(doc_id, doc.status, doc.progress)

        print(f"Processing document {doc_id}")

        time.sleep(2)

        doc.progress = 30
        db.commit()

        publish_progress(doc_id, doc.status, doc.progress)

        time.sleep(2)

        doc.progress = 60
        db.commit()

        publish_progress(doc_id, doc.status, doc.progress)

        time.sleep(2)

        result = {
            "title": doc.filename,
            "category": "general",
            "summary": "This is a processed document",
            "keywords": ["sample", "document", "test"]
        }

        doc.result = result
        doc.progress = 90
        db.commit()

        publish_progress(doc_id, doc.status, doc.progress)

        time.sleep(1)

        doc.status = "completed"
        doc.progress = 100
        doc.is_finalized = False

        db.commit()

        publish_progress(doc_id, doc.status, doc.progress)

        print(f"Completed document {doc_id}")

    except Exception as e:
        doc.status = "failed"
        doc.error_message = str(e)
        db.commit()

        publish_progress(doc_id, doc.status, doc.progress)

    finally:
        db.close()