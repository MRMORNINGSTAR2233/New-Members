#!/bin/bash

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Starting Backend and Frontend Development Servers ===${NC}"

# Navigate to project root directory
cd "$(dirname "$0")"

# Start backend server
echo -e "${GREEN}Starting FastAPI backend on port 8000...${NC}"
python3 run.py &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 2

# Start frontend server
echo -e "${GREEN}Starting Vite frontend on port 8080...${NC}"
cd frontend && npm run dev &
FRONTEND_PID=$!

# Function to cleanup processes on exit
cleanup() {
    echo -e "\n${RED}Stopping servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID
    exit 0
}

# Set up trap to catch termination and interrupt signals
trap cleanup SIGINT SIGTERM

# Wait for user to press Ctrl+C
echo -e "\n${BLUE}Both servers are running:${NC}"
echo -e "${GREEN}- Backend: http://localhost:8000${NC}"
echo -e "${GREEN}- Frontend: http://localhost:8080${NC}"
echo -e "\n${BLUE}Press Ctrl+C to stop both servers${NC}"

# Keep script running
wait
