import json
import os
from typing import Dict, Optional, List
from app.models import Document, DocumentMetadata, Section, DocumentStatus
from datetime import datetime
import aiofiles

STORAGE_DIR = "data"
DOCUMENTS_DIR = os.path.join(STORAGE_DIR, "documents")
METADATA_FILE = os.path.join(STORAGE_DIR, "metadata.json")

class DocumentStorage:
    def __init__(self):
        os.makedirs(DOCUMENTS_DIR, exist_ok=True)
        self._ensure_metadata_file()
    
    def _ensure_metadata_file(self):
        if not os.path.exists(METADATA_FILE):
            with open(METADATA_FILE, 'w') as f:
                json.dump({}, f)
    
    async def save_document(self, document: Document):
        doc_path = os.path.join(DOCUMENTS_DIR, f"{document.metadata.id}.json")
        async with aiofiles.open(doc_path, 'w') as f:
            await f.write(document.model_dump_json())
        
        await self._update_metadata(document.metadata)
    
    async def _update_metadata(self, metadata: DocumentMetadata):
        async with aiofiles.open(METADATA_FILE, 'r') as f:
            content = await f.read()
            all_metadata = json.loads(content)
        
        all_metadata[metadata.id] = json.loads(metadata.model_dump_json())
        
        async with aiofiles.open(METADATA_FILE, 'w') as f:
            await f.write(json.dumps(all_metadata, indent=2))
    
    async def get_document(self, doc_id: str) -> Optional[Document]:
        doc_path = os.path.join(DOCUMENTS_DIR, f"{doc_id}.json")
        if not os.path.exists(doc_path):
            return None
        
        async with aiofiles.open(doc_path, 'r') as f:
            content = await f.read()
            return Document.model_validate_json(content)
    
    async def get_all_metadata(self) -> List[DocumentMetadata]:
        async with aiofiles.open(METADATA_FILE, 'r') as f:
            content = await f.read()
            all_metadata = json.loads(content)
        
        return [DocumentMetadata(**meta) for meta in all_metadata.values()]
    
    async def update_status(self, doc_id: str, status: DocumentStatus, error_message: Optional[str] = None):
        doc = await self.get_document(doc_id)
        if doc:
            doc.metadata.status = status
            if error_message:
                doc.metadata.error_message = error_message
            await self.save_document(doc)
    
    async def update_sections(self, doc_id: str, sections: List[Section]):
        doc = await self.get_document(doc_id)
        if doc:
            doc.sections = sections
            doc.metadata.total_sections = len(sections)
            await self.save_document(doc)
    
    async def delete_document(self, doc_id: str):
        """Delete a document from storage"""
        # Delete document file
        doc_path = os.path.join(DOCUMENTS_DIR, f"{doc_id}.json")
        if os.path.exists(doc_path):
            os.remove(doc_path)
        
        # Remove from metadata
        async with aiofiles.open(METADATA_FILE, 'r') as f:
            content = await f.read()
            all_metadata = json.loads(content)
        
        if doc_id in all_metadata:
            del all_metadata[doc_id]
        
        async with aiofiles.open(METADATA_FILE, 'w') as f:
            await f.write(json.dumps(all_metadata, indent=2))

storage = DocumentStorage()

