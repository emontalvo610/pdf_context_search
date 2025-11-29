#!/bin/bash

# PDF Context Search - Frontend Startup Script
# ============================================

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting PDF Context Search Frontend${NC}"
echo ""

# Check if node_modules exists
if [ ! -d "fe-app/node_modules" ]; then
    echo -e "${RED}❌ Dependencies not installed!${NC}"
    echo "Run: cd fe-app && pnpm install"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies found${NC}"
echo ""

# Export environment variables
export NEXT_PUBLIC_API_URL=http://localhost:8000

cd fe-app

echo -e "${GREEN}Starting Next.js development server on http://localhost:3000${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

pnpm dev

