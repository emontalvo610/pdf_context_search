from pydantic import BaseModel  
from typing import Optional, List
from enum import Enum
from datetime import datetime

class DocumentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Section(BaseModel):
    id: str
    title: str
    content: str
    page_number: int
    parent_id: Optional[str] = None
    children: List[str] = []

class DocumentMetadata(BaseModel):
    id: str
    filename: str
    status: DocumentStatus
    upload_date: datetime
    total_sections: int = 0
    error_message: Optional[str] = None

class Document(BaseModel):
    metadata: DocumentMetadata
    sections: List[Section] = []

class Citation(BaseModel):
    document_id: str
    document_name: str
    section_id: str
    section_title: str
    text: str
    score: float

class SearchResponse(BaseModel):
    query: str
    response: str
    citations: List[Citation]

class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: DocumentStatus
    message: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]

class DocumentDetailResponse(BaseModel):
    metadata: DocumentMetadata
    sections: List[Section]

