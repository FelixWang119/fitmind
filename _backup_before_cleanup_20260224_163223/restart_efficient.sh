#!/bin/bash
# Efficient restart script that kills existing processes before restarting
# Avoids machine slowdowns and errors from leftover processes

set -e  # Exit on error

echo "=========================================="
echo "EFFICIENT BACKEND RESTART SCRIPT"
echo "=========================================="
echo "Goal: Kill existing processes before restarting"
echo "      Avoid machine slowdowns and errors"
echo "=========================================="
echo

# Configuration
BACKEND_PORT=8000
BACKEND_DIR="/Users/felix/bmad/backend"
LOG_FILE="/Users/felix/bmad/backend_restart.log"
PID_FILE="/Users/felix/bmad/backend.pid"

# Function to kill processes on port 8000
kill_port_processes() {
    echo "🔫 Killing processes on port $BACKEND_PORT..."
    
    # Find PIDs using port 8000
    PIDS=$(lsof -ti:$BACKEND_PORT 2>/dev/null || echo "")
    
    if [ -n "$PIDS" ]; then
        echo "   Found PIDs: $PIDS"
        kill -9 $PIDS 2>/dev/null || true
        sleep 1
        
        # Verify they're killed
        REMAINING_PIDS=$(lsof -ti:$BACKEND_PORT 2>/dev/null || echo "")
        if [ -n "$REMAINING_PIDS" ]; then
            echo "   ⚠️  Some processes still running: $REMAINING_PIDS"
            echo "   Force killing with pkill..."
            pkill -f "uvicorn" 2>/dev/null || true
            pkill -f "python.*backend" 2>/dev/null || true
            sleep 2
        fi
        
        echo "   ✅ Port $BACKEND_PORT cleared"
    else
        echo "   ✅ No processes found on port $BACKEND_PORT"
    fi
}

# Function to kill Python backend processes
kill_python_processes() {
    echo "🔫 Killing Python backend processes..."
    
    # Kill by process name patterns
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "python.*main.py" 2>/dev/null || true
    pkill -f "python.*backend" 2>/dev/null || true
    
    sleep 2
    echo "   ✅ Python processes cleared"
}

# Function to check if backend is running
check_backend_running() {
    echo "🔍 Checking if backend is running..."
    
    if curl -s "http://localhost:$BACKEND_PORT/api/v1/health" > /dev/null 2>&1; then
        echo "   ✅ Backend is running on port $BACKEND_PORT"
        return 0
    else
        echo "   ❌ Backend is NOT running on port $BACKEND_PORT"
        return 1
    fi
}

# Function to start backend
start_backend() {
    echo "🚀 Starting backend..."
    
    cd "$BACKEND_DIR"
    
    # Start in background and save PID
    nohup uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > "$LOG_FILE" 2>&1 &
    BACKEND_PID=$!
    
    echo $BACKEND_PID > "$PID_FILE"
    echo "   ✅ Started with PID: $BACKEND_PID"
    echo "   📝 Logs: $LOG_FILE"
    echo "   💾 PID saved: $PID_FILE"
    
    # Wait for backend to start
    echo "   ⏳ Waiting for backend to start (max 30 seconds)..."
    
    for i in {1..30}; do
        if curl -s "http://localhost:$BACKEND_PORT/api/v1/health" > /dev/null 2>&1; then
            echo "   ✅ Backend started successfully!"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    echo
    echo "   ⚠️  Backend might be slow to start. Check logs: tail -f $LOG_FILE"
    return 1
}

# Function to show process status
show_status() {
    echo
    echo "📊 CURRENT STATUS:"
    echo "------------------"
    
    # Show processes on port 8000
    echo "Processes on port $BACKEND_PORT:"
    lsof -i:$BACKEND_PORT 2>/dev/null || echo "   None"
    
    # Show Python processes
    echo
    echo "Python backend processes:"
    ps aux | grep -E "(uvicorn|python.*main|python.*backend)" | grep -v grep || echo "   None"
    
    # Check if backend responds
    echo
    if check_backend_running; then
        echo "✅ Backend is HEALTHY and responding"
    else
        echo "❌ Backend is NOT responding"
    fi
}

# Main execution
main() {
    echo "Starting efficient restart procedure..."
    echo
    
    # Step 1: Kill existing processes
    kill_port_processes
    kill_python_processes
    
    # Step 2: Wait a moment
    echo
    echo "⏳ Waiting 3 seconds for cleanup..."
    sleep 3
    
    # Step 3: Start backend
    start_backend
    
    # Step 4: Show final status
    show_status
    
    echo
    echo "=========================================="
    echo "RESTART COMPLETE"
    echo "=========================================="
    echo
    echo "Quick commands:"
    echo "  tail -f $LOG_FILE          # View logs"
    echo "  cat $PID_FILE              # Show backend PID"
    echo "  kill \$(cat $PID_FILE)     # Stop backend"
    echo "  ./restart_efficient.sh     # Restart again"
    echo
    echo "Test the backend:"
    echo "  curl http://localhost:8000/api/v1/health"
    echo "  python test_direct_token.py"
    echo
}

# Run main function
main "$@"