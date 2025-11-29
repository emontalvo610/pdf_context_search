#!/bin/bash

echo "Starting PDF Context Search Application..."
echo ""

if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with the following content:"
    echo "OPENAI_API_KEY=your_openai_api_key_here"
    echo "NEXT_PUBLIC_API_URL=http://localhost:8000"
    exit 1
fi

echo "Docker Compose will automatically load .env file"
echo "Building and starting containers..."
echo ""

docker-compose up --build

echo ""
echo "Application stopped."

