# API Documentation

## Overview

The PDF Context Search API provides endpoints for uploading, analyzing, and searching PDF documents. The API automatically processes documents section by section and enables semantic search across all analyzed content.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. In production, implement appropriate authentication mechanisms.

## Endpoints

### 1. Upload Document

Upload a PDF document for analysis.

**Endpoint:** `POST /api/documents/upload`

**Request:**
- Content-Type: `multipart/form-data`
- Body: Form data with a `file` field containing the PDF

**Response:**
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "example.pdf",
  "status": "pending",
  "message": "Document uploaded successfully and processing started"
}
```

**Status Codes:**
- `200 OK`: Document uploaded successfully
- `400 Bad Request`: Invalid file type (only PDF allowed)
- `500 Internal Server Error`: Server error during upload

### 2. List Documents

Retrieve all uploaded documents with their metadata.

**Endpoint:** `GET /api/documents`

**Response:**
```json
{
  "documents": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "filename": "example.pdf",
      "status": "completed",
      "upload_date": "2025-11-28T10:30:00",
      "total_sections": 15,
      "error_message": null
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Documents retrieved successfully

### 3. Get Document Details

Retrieve a specific document with all its sections.

**Endpoint:** `GET /api/documents/{document_id}`

**Path Parameters:**
- `document_id` (string): UUID of the document

**Response:**
```json
{
  "metadata": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "filename": "example.pdf",
    "status": "completed",
    "upload_date": "2025-11-28T10:30:00",
    "total_sections": 15,
    "error_message": null
  },
  "sections": [
    {
      "id": "section_1",
      "title": "Introduction",
      "content": "This is the introduction section...",
      "page_number": 1,
      "parent_id": null,
      "children": []
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Document retrieved successfully
- `404 Not Found`: Document not found

### 4. Get Section

Retrieve a specific section from a document.

**Endpoint:** `GET /api/documents/{document_id}/sections/{section_id}`

**Path Parameters:**
- `document_id` (string): UUID of the document
- `section_id` (string): ID of the section

**Response:**
```json
{
  "id": "section_1",
  "title": "Introduction",
  "content": "This is the introduction section...",
  "page_number": 1,
  "parent_id": null,
  "children": []
}
```

**Status Codes:**
- `200 OK`: Section retrieved successfully
- `404 Not Found`: Document or section not found

### 5. Search

Search across all analyzed documents and retrieve relevant citations.

**Endpoint:** `GET /api/search`

**Query Parameters:**
- `q` (string, required): Search query

**Example:**
```
GET /api/search?q=what%20happens%20if%20I%20steal
```

**Response:**
```json
{
  "query": "what happens if I steal",
  "response": "Based on the documents, theft is punishable by hanging according to Law 1...",
  "citations": [
    {
      "document_id": "123e4567-e89b-12d3-a456-426614174000",
      "document_name": "laws.pdf",
      "section_id": "section_1",
      "section_title": "Law 1",
      "text": "Theft is punishable by hanging...",
      "score": 0.95
    }
  ]
}
```

**Status Codes:**
- `200 OK`: Search completed successfully
- `400 Bad Request`: Empty query
- `500 Internal Server Error`: Search failed

## Document Processing

### Processing Pipeline

1. **Upload**: Document is uploaded via the `/api/documents/upload` endpoint
2. **Pending**: Document is queued for processing (status: `pending`)
3. **In Progress**: Document is being analyzed (status: `in_progress`)
4. **Completed**: Document analysis finished (status: `completed`)
5. **Failed**: Document processing failed (status: `failed`)

### Concurrent Processing

The system can process up to 5 documents simultaneously. Additional documents are queued and processed as slots become available.

### Section Extraction

The system automatically detects and extracts sections from PDFs based on:
- Headers matching patterns like "CHAPTER", "SECTION", "ARTICLE", "LAW"
- Document structure and formatting
- Page boundaries

## Error Handling

All endpoints return appropriate HTTP status codes and error messages in the following format:

```json
{
  "detail": "Error message description"
}
```

Common error codes:
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

No rate limiting is currently implemented. Consider adding rate limiting in production environments.

## CORS

CORS is enabled for all origins in development. Configure appropriately for production.

