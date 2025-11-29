# PDF Context Search

A full-stack application for uploading, analyzing, and searching PDF documents using AI-powered semantic search.

## Features

- **Document Upload**: Upload PDF documents for automatic analysis
- **Automatic Analysis**: Documents are processed section by section in the background
- **Concurrent Processing**: Process up to 5 documents simultaneously
- **Status Tracking**: Monitor document processing status (pending/in progress/completed/failed)
- **Document Viewer**: Browse documents with a TreeView sidebar and content viewer
- **Semantic Search**: AI-powered search across all documents with relevant citations
- **Citation Navigation**: Click citations to jump directly to relevant document sections

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Qdrant**: Vector database for semantic search
- **LlamaIndex**: LLM framework for document indexing and querying
- **OpenAI**: Embeddings and language models
- **PyPDF2**: PDF parsing and text extraction

### Frontend
- **Next.js 16**: React framework with App Router
- **ShadCN UI**: Beautiful, accessible components
- **TanStack Query**: Data fetching and state management
- **Tailwind CSS**: Utility-first styling
- **TypeScript**: Type-safe development

## Project Structure

```
pdf_context_search/
├── app/                      # Backend application
│   ├── main.py              # FastAPI application and endpoints
│   ├── models.py            # Pydantic data models
│   ├── utils.py             # Document and search services
│   ├── storage.py           # File storage management
│   └── tasks.py             # Background task processing
├── fe-app/                  # Frontend application
│   ├── app/                 # Next.js pages
│   │   ├── page.tsx        # Home page (document list + upload)
│   │   ├── documents/[id]/ # Document viewer
│   │   └── search/         # Search page
│   ├── components/          # React components
│   │   └── ui/             # ShadCN UI components
│   └── lib/                # Utilities and API client
├── docs/                    # Sample documents
├── data/                    # Document storage (created at runtime)
├── uploads/                 # Temporary upload storage
├── qdrant_data/            # Vector database storage
├── docker-compose.yml      # Docker composition for dev environment
├── Dockerfile              # Backend Docker configuration
└── requirements.txt        # Python dependencies
```

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### Environment Variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_api_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Running with Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd pdf_context_search
```

2. Create `.env` file with your OpenAI API key

3. Start the application:
```bash
docker-compose up
```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Running Locally (Development)

#### Backend

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variable:
```bash
export OPENAI_API_KEY=your_key_here
```

4. Run the server:
```bash
uvicorn app.main:app --reload --port 8000
```

#### Frontend

1. Navigate to frontend directory:
```bash
cd fe-app
```

2. Install dependencies:
```bash
pnpm install
```

3. Run the development server:
```bash
pnpm dev
```

## Usage

### 1. Upload Documents

1. Navigate to the home page (http://localhost:3000)
2. Click "Upload Document" and select a PDF file
3. Click "Upload" to start processing
4. Monitor the status in the documents list

### 2. View Documents

1. Click on any completed document in the list
2. Use the sidebar to navigate between sections
3. Read section content in the main viewer

### 3. Search

1. Click the "Search" button in the top right
2. Enter your search query
3. View the AI-generated answer and citations
4. Click "View" on any citation to see the full section

## API Documentation

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for detailed API specifications.

## Data Models

See [DATA_MODELS.md](./DATA_MODELS.md) for detailed data model documentation.

## Architecture

### Document Processing Pipeline

1. **Upload**: User uploads PDF via frontend
2. **Storage**: File saved temporarily, document record created
3. **Background Processing**: Task processor picks up document (max 5 concurrent)
4. **Section Extraction**: PDF parsed and sections identified
5. **Vectorization**: Sections embedded using OpenAI embeddings
6. **Storage**: Vectors stored in Qdrant, document metadata saved
7. **Status Update**: Document marked as completed

### Search Flow

1. **Query**: User enters search query
2. **Embedding**: Query converted to vector using OpenAI
3. **Similarity Search**: Qdrant finds top 5 most similar sections
4. **LLM Generation**: OpenAI generates answer using retrieved context
5. **Response**: Answer and citations returned to user

## Configuration

### Backend Configuration

- **Max Concurrent Processing**: 5 documents (configurable in `tasks.py`)
- **Vector Database**: Qdrant (file-based storage in `./qdrant_data`)
- **Document Storage**: JSON files in `./data/documents`
- **Embeddings**: OpenAI `text-embedding-ada-002`
- **LLM**: GPT-4

### Frontend Configuration

- **API Polling**: Document list refreshes every 3 seconds
- **Query Stale Time**: 60 seconds
- **Refetch on Window Focus**: Disabled

## Troubleshooting

### Backend Issues

1. **OpenAI API errors**: Verify your API key is correct and has credits
2. **PDF parsing errors**: Ensure PDF is not encrypted or corrupted
3. **Storage errors**: Check write permissions for `data/` and `uploads/` directories

### Frontend Issues

1. **API connection errors**: Verify backend is running on port 8000
2. **Build errors**: Delete `.next` folder and `node_modules`, reinstall dependencies
3. **CORS errors**: Ensure CORS is properly configured in FastAPI

## Development

### Adding New Features

1. **Backend**: Add endpoints in `app/main.py`, models in `app/models.py`
2. **Frontend**: Add components in `components/`, pages in `app/`
3. **API Integration**: Update `lib/api.ts` with new API functions

### Testing

The application includes example documents in the `docs/` folder for testing.

## Performance Considerations

- **Concurrent Processing**: Limited to 5 documents to manage resource usage
- **Vector Search**: Uses Qdrant for fast similarity search
- **Caching**: Frontend uses React Query for intelligent caching
- **Pagination**: Consider implementing pagination for large document lists

## Security Notes

This is a development application. For production deployment:

1. Add authentication and authorization
2. Implement rate limiting
3. Configure CORS properly
4. Use environment-specific configurations
5. Secure file uploads with validation
6. Implement proper error handling and logging

## License

MIT License

## Contributing

Contributions are welcome! Please follow the existing code style and add tests for new features.
