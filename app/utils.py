import os
import uuid
from typing import List
import PyPDF2
import re
from llama_index.core import Document as LlamaDocument
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client
from qdrant_client.models import Distance, VectorParams

from app.models import Section, Citation, SearchResponse

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

class DocumentService:
    
    @staticmethod
    def extract_sections_from_pdf(file_path: str) -> List[Section]:
        sections = []
        section_map = {}
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            # Extract all text first
            full_text = []
            for page_num in range(total_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                full_text.append((page_num + 1, text))
            
            # Join all text and split into lines
            all_lines = []
            for page_num, text in full_text:
                lines = text.split('\n')
                for line in lines:
                    all_lines.append((page_num, line.strip()))
            
            current_section = None
            current_content = []
            current_page = 1
            
            for page_num, line in all_lines:
                if not line:
                    continue
                
                section_match = re.match(r'^(\d+(?:\.\d+)*)\.\s+(.+?)$', line)
                header_only_match = re.match(r'^(\d+(?:\.\d+)*)\.$', line)
                
                if section_match:
                    # Save previous section if exists
                    if current_section:
                        section = Section(
                            id=current_section['id'],
                            title=current_section['title'],
                            content='\n'.join(current_content).strip(),
                            page_number=current_section['page_number'],
                            parent_id=current_section.get('parent_id'),
                            children=[]
                        )
                        sections.append(section)
                        section_map[current_section['id']] = section
                    
                    section_num = section_match.group(1)
                    section_title = section_match.group(2).strip()
                    
                    if not section_title or len(section_title) < 3:
                        section_title = f"Section {section_num}"
                    
                    parent_id = None
                    num_parts = section_num.split('.')
                    if len(num_parts) > 1:
                        # This is a subsection, find parent
                        parent_num = '.'.join(num_parts[:-1])
                        parent_id = f"section_{parent_num}"
                    
                    section_id = f"section_{section_num}"
                    current_section = {
                        'id': section_id,
                        'title': f"{section_num}. {section_title}",
                        'page_number': page_num,
                        'parent_id': parent_id
                    }
                    current_content = []
                    current_page = page_num
                    
                elif header_only_match:
                    # Section number on its own line, skip for now
                    # Content will be captured as regular content
                    continue
                else:
                    # Regular content
                    if current_section:
                        current_content.append(line)
                    else:
                        # Before first section - create intro
                        if not section_map.get('section_intro'):
                            current_section = {
                                'id': 'section_intro',
                                'title': 'Introduction',
                                'page_number': page_num,
                                'parent_id': None
                            }
                            current_content = [line]
            
            # Save last section
            if current_section:
                section = Section(
                    id=current_section['id'],
                    title=current_section['title'],
                    content='\n'.join(current_content).strip(),
                    page_number=current_section.get('page_number', current_page),
                    parent_id=current_section.get('parent_id'),
                    children=[]
                )
                sections.append(section)
                section_map[current_section['id']] = section
        
        # Build parent-child relationships
        for section in sections:
            if section.parent_id and section.parent_id in section_map:
                parent = section_map[section.parent_id]
                if section.id not in parent.children:
                    parent.children.append(section.id)
        
        # Sort sections by their numeric ID for proper ordering
        def section_sort_key(section):
            if section.id == 'section_intro':
                return [0]
            try:
                # Extract numbers from section_1.2.3 -> [1, 2, 3]
                num_str = section.id.replace('section_', '')
                return [int(x) for x in num_str.split('.')]
            except:
                return [999999]
        
        sections.sort(key=section_sort_key)
        
        if not sections:
            sections.append(Section(
                id="section_1",
                title="Full Document",
                content="No structured sections found",
                page_number=1,
                parent_id=None,
                children=[]
            ))
        
        print(f"Extracted {len(sections)} sections")
        for sec in sections[:10]:  # Print first 10 for debugging
            print(f"  - {sec.title} (ID: {sec.id}, Parent: {sec.parent_id})")
        
        return sections
    
    @staticmethod
    def sections_to_llama_documents(sections: List[Section], document_id: str, document_name: str) -> List[LlamaDocument]:
        llama_docs = []
        
        for section in sections:
            llama_doc = LlamaDocument(
                text=section.content,
                metadata={
                    "document_id": document_id,
                    "document_name": document_name,
                    "section_id": section.id,
                    "section_title": section.title,
                    "page_number": section.page_number
                }
            )
            llama_docs.append(llama_doc)
        
        return llama_docs


class QdrantService:
    def __init__(self, k: int = 5):
        self.client = None
        self.index = None
        self.k = k
        self.collection_name = "pdf_documents"
    
    def connect(self) -> None:
        self.client = qdrant_client.QdrantClient(location=":memory:")
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
        )
        
        vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            enable_hybrid=False,
        )
        
        Settings.embed_model = OpenAIEmbedding(
            api_key=OPENAI_API_KEY,
            model="text-embedding-ada-002"
        )
        Settings.llm = OpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-4o-mini"
        )
        
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
    
    def load(self, docs: List[LlamaDocument]):
        if not self.index:
            raise ValueError("Index not initialized. Call connect() first.")
        
        print(f"Loading {len(docs)} documents into Qdrant...")
        for i, doc in enumerate(docs):
            print(f"Inserting document {i+1}/{len(docs)}: {doc.metadata.get('section_title', 'Unknown')}")
            self.index.insert(doc)
        print(f"Successfully loaded {len(docs)} documents")
    
    def query(self, query_str: str) -> SearchResponse:
        if not self.index:
            raise ValueError("Index not initialized. Call connect() first.")
        
        try:
            print(f"Searching for: {query_str}")
            retriever = self.index.as_retriever(similarity_top_k=self.k)
            nodes = retriever.retrieve(query_str)
            print(f"Found {len(nodes)} nodes from retriever")
            
            query_engine = self.index.as_query_engine(
                similarity_top_k=self.k,
                response_mode="compact"
            )
            
            response = query_engine.query(query_str)
            print(f"Query engine response: {str(response)[:200]}")
            
            citations = []
            source_nodes = response.source_nodes if hasattr(response, 'source_nodes') else nodes
            print(f"Processing {len(source_nodes)} source nodes")
            
            for node in source_nodes[:self.k]:
                if hasattr(node, 'node'):
                    metadata = node.node.metadata
                    node_text = node.node.text
                else:
                    metadata = node.metadata if hasattr(node, 'metadata') else {}
                    node_text = node.text if hasattr(node, 'text') else str(node)
                
                print(f"Citation metadata: {metadata}")
                citation = Citation(
                    document_id=metadata.get("document_id", "unknown"),
                    document_name=metadata.get("document_name", "unknown"),
                    section_id=metadata.get("section_id", "unknown"),
                    section_title=metadata.get("section_title", "Unknown Section"),
                    text=node_text[:500] if node_text else "",
                    score=node.score if hasattr(node, 'score') else 0.0
                )
                citations.append(citation)
            
            print(f"Returning {len(citations)} citations")
            return SearchResponse(
                query=query_str,
                response=str(response) if response else "No response generated",
                citations=citations
            )
        except Exception as e:
            print(f"Search error: {str(e)}")
            import traceback
            traceback.print_exc()
            return SearchResponse(
                query=query_str,
                response=f"Search error: {str(e)}",
                citations=[]
            )

qdrant_service = QdrantService(k=5)
