# Data Models Documentation

## Overview

This document describes all data models used in the PDF Context Search application.

## Enums

### DocumentStatus

Represents the current processing status of a document.

```python
class DocumentStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
```

**Values:**
- `pending`: Document uploaded, waiting to be processed
- `in_progress`: Document is currently being analyzed
- `completed`: Document analysis finished successfully
- `failed`: Document processing failed due to an error

## Core Models

### Section

Represents a section or chapter within a document.

```python
class Section(BaseModel):
    id: str
    title: str
    content: str
    page_number: int
    parent_id: Optional[str] = None
    children: List[str] = []
```

**Fields:**
- `id` (string): Unique identifier for the section (e.g., "section_1")
- `title` (string): Title or heading of the section
- `content` (string): Full text content of the section
- `page_number` (integer): Page number where the section starts
- `parent_id` (string, optional): ID of parent section for hierarchical structure
- `children` (list of strings): IDs of child sections

**Example:**
```json
{
  "id": "section_1",
  "title": "Chapter 1: Introduction",
  "content": "This is the introduction...",
  "page_number": 1,
  "parent_id": null,
  "children": ["section_1_1", "section_1_2"]
}
```

### DocumentMetadata

Contains metadata about a document without its full content.

```python
class DocumentMetadata(BaseModel):
    id: str
    filename: str
    status: DocumentStatus
    upload_date: datetime
    total_sections: int = 0
    error_message: Optional[str] = None
```

**Fields:**
- `id` (string): Unique UUID for the document
- `filename` (string): Original filename of the uploaded PDF
- `status` (DocumentStatus): Current processing status
- `upload_date` (datetime): Timestamp when document was uploaded
- `total_sections` (integer): Number of sections extracted from the document
- `error_message` (string, optional): Error message if processing failed

**Example:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "company_handbook.pdf",
  "status": "completed",
  "upload_date": "2025-11-28T10:30:00",
  "total_sections": 25,
  "error_message": null
}
```

### Document

Complete document representation including metadata and all sections.

```python
class Document(BaseModel):
    metadata: DocumentMetadata
    sections: List[Section] = []
```

**Fields:**
- `metadata` (DocumentMetadata): Document metadata
- `sections` (list of Section): All sections extracted from the document

**Example:**
```json
{
  "metadata": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "filename": "handbook.pdf",
    "status": "completed",
    "upload_date": "2025-11-28T10:30:00",
    "total_sections": 2
  },
  "sections": [
    {
      "id": "section_1",
      "title": "Chapter 1",
      "content": "Content here...",
      "page_number": 1,
      "parent_id": null,
      "children": []
    }
  ]
}
```

## Search Models

### Citation

Represents a citation from a document section that matches a search query.

```python
class Citation(BaseModel):
    document_id: str
    document_name: str
    section_id: str
    section_title: str
    text: str
    score: float
```

**Fields:**
- `document_id` (string): UUID of the source document
- `document_name` (string): Filename of the source document
- `section_id` (string): ID of the section containing the citation
- `section_title` (string): Title of the section
- `text` (string): Relevant excerpt from the section (max 500 chars)
- `score` (float): Relevance score (0.0 to 1.0)

**Example:**
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "document_name": "laws.pdf",
  "section_id": "section_5",
  "section_title": "Law 5: Theft",
  "text": "Theft of property is punishable by...",
  "score": 0.95
}
```

### SearchResponse

Response from a search query containing the answer and citations.

```python
class SearchResponse(BaseModel):
    query: str
    response: str
    citations: List[Citation]
```

**Fields:**
- `query` (string): The original search query
- `response` (string): AI-generated answer based on the documents
- `citations` (list of Citation): Top 5 most relevant citations

**Example:**
```json
{
  "query": "what are the penalties for theft?",
  "response": "According to the documents, theft is punishable by hanging...",
  "citations": [
    {
      "document_id": "123e4567-e89b-12d3-a456-426614174000",
      "document_name": "laws.pdf",
      "section_id": "section_5",
      "section_title": "Law 5",
      "text": "Theft is punishable by hanging...",
      "score": 0.95
    }
  ]
}
```

## API Response Models

### UploadResponse

Response after uploading a document.

```python
class UploadResponse(BaseModel):
    document_id: str
    filename: str
    status: DocumentStatus
    message: str
```

**Fields:**
- `document_id` (string): UUID of the newly created document
- `filename` (string): Original filename
- `status` (DocumentStatus): Initial status (typically "pending")
- `message` (string): Success message

### DocumentListResponse

Response for listing all documents.

```python
class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
```

**Fields:**
- `documents` (list of DocumentMetadata): All documents in the system

### DocumentDetailResponse

Response for retrieving a single document with all details.

```python
class DocumentDetailResponse(BaseModel):
    metadata: DocumentMetadata
    sections: List[Section]
```

**Fields:**
- `metadata` (DocumentMetadata): Document metadata
- `sections` (list of Section): All sections in the document

## Storage Format

Documents are stored as JSON files in the `data/documents/` directory:
- Filename format: `{document_id}.json`
- Content: Serialized Document model

Document metadata index is stored in:
- File: `data/metadata.json`
- Content: Dictionary mapping document IDs to DocumentMetadata

## Vector Storage

Sections are embedded and stored in Qdrant vector database with metadata:
- `document_id`: UUID of the source document
- `document_name`: Filename of the source document
- `section_id`: ID of the section
- `section_title`: Title of the section
- `page_number`: Page number in the original PDF

