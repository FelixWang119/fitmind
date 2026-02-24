#!/bin/bash
# Simple restart script - kills everything and restarts clean

echo "Killing backend processes..."
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "python.*main" 2>/dev/null || true
pkill -f "python.*backend" 2>/dev/null || true

sleep 2

echo "Starting backend..."
cd /Users/felix/bmad/backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

echo "Backend started. Check: curl http://localhost:8000/api/v1/health"