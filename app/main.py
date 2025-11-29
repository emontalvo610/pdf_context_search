from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import uuid
from datetime import datetime

from app.models import (
    UploadResponse, DocumentListResponse, DocumentDetailResponse,
    SearchResponse, DocumentStatus, DocumentMetadata, Document as DocModel
)
from app.storage import storage
from app.utils import qdrant_service
from app.tasks import task_processor

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("data/documents", exist_ok=True)
os.makedirs("qdrant_data", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    qdrant_service.connect()
    yield

app = FastAPI(
    title="PDF Context Search API",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "PDF Context Search API"}

@app.post("/api/documents/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    doc_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.pdf")
    
    contents = await file.read()
    with open(file_path, 'wb') as f:
        f.write(contents)
    
    metadata = DocumentMetadata(
        id=doc_id,
        filename=file.filename,
        status=DocumentStatus.PENDING,
        upload_date=datetime.now(),
        total_sections=0
    )
    
    document = DocModel(metadata=metadata, sections=[])
    await storage.save_document(document)
    
    task_processor.start_processing(doc_id, file_path, file.filename)
    
    return UploadResponse(
        document_id=doc_id,
        filename=file.filename,
        status=DocumentStatus.PENDING,
        message="Document uploaded successfully and processing started"
    )

@app.get("/api/documents", response_model=DocumentListResponse)
async def list_documents():
    metadata_list = await storage.get_all_metadata()
    return DocumentListResponse(documents=metadata_list)

@app.get("/api/documents/{document_id}", response_model=DocumentDetailResponse)
async def get_document(document_id: str):
    document = await storage.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentDetailResponse(
        metadata=document.metadata,
        sections=document.sections
    )

@app.get("/api/documents/{document_id}/sections/{section_id}")
async def get_section(document_id: str, section_id: str):
    document = await storage.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    section = next((s for s in document.sections if s.id == section_id), None)
    
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    return section

@app.get("/api/search", response_model=SearchResponse)
async def search(q: str = Query(..., description="Search query")):
    if not q or len(q.strip()) == 0:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        result = qdrant_service.query(q)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    document = await storage.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete the document from storage
    await storage.delete_document(document_id)
    
    # Delete the uploaded file
    file_path = os.path.join(UPLOAD_DIR, f"{document_id}.pdf")
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return {"message": "Document deleted successfully", "document_id": document_id}

@app.post("/api/documents/reset")
async def reset_all_documents():
    """Delete all documents and reset the system"""
    # Get all documents
    metadata_list = await storage.get_all_metadata()
    
    # Delete each document
    for metadata in metadata_list:
        await storage.delete_document(metadata.id)
        file_path = os.path.join(UPLOAD_DIR, f"{metadata.id}.pdf")
        if os.path.exists(file_path):
            os.remove(file_path)
    
    # Reconnect to Qdrant to clear the index
    qdrant_service.connect()
    
    return {"message": f"Successfully deleted {len(metadata_list)} documents and reset the system"}
