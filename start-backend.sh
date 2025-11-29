#!/bin/bash

# PDF Context Search - Backend Startup Script
# ============================================

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting PDF Context Search Backend${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check for OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f ".env" ]; then
        echo -e "${YELLOW}⚠️  Loading environment variables from .env file${NC}"
        # Load .env file properly, ignoring comments and empty lines
        while IFS='=' read -r key value; do
            # Skip comments and empty lines
            [[ $key =~ ^#.*$ ]] && continue
            [[ -z $key ]] && continue
            # Remove quotes from value if present
            value="${value%\"}"
            value="${value#\"}"
            value="${value%\'}"
            value="${value#\'}"
            # Export the variable
            export "$key=$value"
        done < .env
    fi
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${RED}❌ OPENAI_API_KEY not found!${NC}"
        echo ""
        echo "Please set your OpenAI API key:"
        echo "  1. Create a .env file with the correct format:"
        echo "     echo 'OPENAI_API_KEY=sk-your-key-here' > .env"
        echo ""
        echo "  2. Or export it directly in terminal:"
        echo "     export OPENAI_API_KEY=sk-your-key-here"
        echo ""
        echo "  3. Then run: ./start-backend.sh"
        echo ""
        exit 1
    fi
fi

echo -e "${GREEN}✅ Environment configured${NC}"
echo -e "${GREEN}✅ Virtual environment found${NC}"
echo ""

# Create necessary directories
echo -e "${GREEN}Creating required directories...${NC}"
mkdir -p uploads data/documents qdrant_data
echo -e "${GREEN}✅ Directories created: uploads/, data/, qdrant_data/${NC}"
echo ""

# Activate virtual environment and run
echo -e "${GREEN}Starting FastAPI server on http://localhost:8000${NC}"
echo -e "${GREEN}API Documentation: http://localhost:8000/docs${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

