# Async Document Processing System

## 🚀 Overview

This project is a full-stack application that allows users to upload documents, process them asynchronously, track progress in real-time, review results, and export finalized data.

---

## 🏗️ Tech Stack

### Backend

* FastAPI
* PostgreSQL
* Celery
* Redis

### Frontend

* React (TypeScript)

### Infrastructure

* Docker & Docker Compose

---

## ⚙️ Features

* Upload documents
* Async background processing (Celery)
* Live progress tracking (Redis Pub/Sub)
* Dashboard with document list
* Status tracking (Queued, Processing, Completed, Failed)
* Retry failed jobs
* View & edit processed results
* Finalize documents
* Export finalized data (JSON & CSV)

---

## 🔄 Processing Flow

1. Document uploaded
2. Job queued
3. Worker processes document in stages:

   * Parsing
   * Extraction
   * Result generation
4. Progress updates published via Redis
5. Final result stored in PostgreSQL

---

## 📡 API Endpoints

* `POST /upload`
* `GET /documents`
* `GET /documents/{id}`
* `PUT /documents/{id}`
* `PUT /documents/{id}/finalize`
* `POST /documents/{id}/retry`
* `GET /documents/export/json`
* `GET /documents/export/csv`

---

## ▶️ Run Locally

```bash
docker compose up --build
```

Frontend:

```bash
cd frontend
npm install
npm start
```

---

## 🧪 Testing

Upload any file (txt, pdf, image)

---

## 📦 Assumptions

* File processing is simulated
* Focus is on async workflow, not OCR accuracy

---

## ⚠️ Limitations

* No authentication
* Basic UI styling
* File storage is local

---

## 🎥 Demo

(Attach video link here)

---

## 🤖 AI Usage

Used AI tools for guidance, debugging, and structuring the project.

---
