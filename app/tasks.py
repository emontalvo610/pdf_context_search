import asyncio
from typing import Dict
from app.models import DocumentStatus
from app.storage import storage
from app.utils import DocumentService, qdrant_service
import os

class TaskProcessor:
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_tasks: Dict[str, asyncio.Task] = {}
    
    async def process_document(self, doc_id: str, file_path: str, filename: str):
        async with self.semaphore:
            try:
                print(f"Starting processing for document {doc_id} ({filename})")
                await storage.update_status(doc_id, DocumentStatus.IN_PROGRESS)
                
                print(f"Extracting sections from {file_path}")
                sections = DocumentService.extract_sections_from_pdf(file_path)
                print(f"Extracted {len(sections)} sections")
                
                await storage.update_sections(doc_id, sections)
                
                print(f"Converting sections to LlamaIndex documents")
                llama_docs = DocumentService.sections_to_llama_documents(
                    sections, doc_id, filename
                )
                print(f"Created {len(llama_docs)} LlamaIndex documents")
                
                print(f"Loading documents into Qdrant")
                qdrant_service.load(llama_docs)
                print(f"Successfully loaded documents into Qdrant")
                
                await storage.update_status(doc_id, DocumentStatus.COMPLETED)
                print(f"Document {doc_id} processing completed")
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error processing document {doc_id}: {error_msg}")
                import traceback
                traceback.print_exc()
                await storage.update_status(doc_id, DocumentStatus.FAILED, error_msg)
            finally:
                if doc_id in self.active_tasks:
                    del self.active_tasks[doc_id]
                
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
    
    def start_processing(self, doc_id: str, file_path: str, filename: str):
        task = asyncio.create_task(self.process_document(doc_id, file_path, filename))
        self.active_tasks[doc_id] = task
        return task

task_processor = TaskProcessor(max_concurrent=5)

