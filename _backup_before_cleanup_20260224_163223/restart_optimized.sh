#!/bin/bash
# Optimized restart script with intelligent process management
# 1. First try to kill using saved PID
# 2. Then kill by port
# 3. Then kill by process pattern
# 4. Finally start new process

set -e  # Exit on error

echo "=========================================="
echo "OPTIMIZED BACKEND RESTART SCRIPT"
echo "=========================================="
echo "Goal: Intelligent process management"
echo "      1. Kill using saved PID first"
echo "      2. Then kill by port"
echo "      3. Then kill by process pattern"
echo "      4. Start new process"
echo "=========================================="
echo

# Configuration
BACKEND_PORT=8000
BACKEND_DIR="/Users/felix/bmad/backend"
LOG_FILE="/Users/felix/bmad/backend_restart.log"
PID_FILE="/Users/felix/bmad/backend.pid"
MAX_WAIT_SECONDS=30

# Function to kill process by PID from file
kill_by_pid_file() {
    echo "🔫 Step 1: Killing using saved PID from $PID_FILE..."
    
    local killed_any=false
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE" 2>/dev/null || echo "")
        
        if [ -n "$PID" ] && [ "$PID" -gt 0 ] 2>/dev/null; then
            echo "   Found PID: $PID"
            
            # Check if process exists
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "   Process $PID is running, killing..."
                kill -9 "$PID" 2>/dev/null || true
                sleep 1
                
                # Check if killed
                if ps -p "$PID" > /dev/null 2>&1; then
                    echo "   ⚠️  Process $PID still running, force killing..."
                    kill -9 "$PID" 2>/dev/null || true
                    sleep 2
                    killed_any=true
                else
                    echo "   ✅ Process $PID killed successfully"
                    killed_any=true
                fi
            else
                echo "   ℹ️  Process $PID not found (already dead)"
            fi
        else
            echo "   ℹ️  No valid PID found in $PID_FILE"
        fi
    else
        echo "   ℹ️  PID file $PID_FILE not found"
    fi
    
    # Return whether we killed anything
    if [ "$killed_any" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to kill processes on specific port
kill_by_port() {
    echo "🔫 Step 2: Killing processes on port $BACKEND_PORT..."
    
    # Find PIDs using port 8000
    PORT_PIDS=$(lsof -ti:$BACKEND_PORT 2>/dev/null || echo "")
    
    if [ -n "$PORT_PIDS" ]; then
        echo "   Found PIDs on port $BACKEND_PORT: $PORT_PIDS"
        
        # Kill all processes on this port
        for PID in $PORT_PIDS; do
            echo "   Killing PID $PID..."
            kill -9 "$PID" 2>/dev/null || true
        done
        
        sleep 2
        
        # Check if any remain
        REMAINING_PIDS=$(lsof -ti:$BACKEND_PORT 2>/dev/null || echo "")
        if [ -n "$REMAINING_PIDS" ]; then
            echo "   ⚠️  Some processes still running: $REMAINING_PIDS"
            echo "   Using pkill for uvicorn processes..."
            pkill -f "uvicorn" 2>/dev/null || true
            sleep 2
        fi
        
        echo "   ✅ Port $BACKEND_PORT cleared"
    else
        echo "   ✅ No processes found on port $BACKEND_PORT"
    fi
}

# Function to kill Python backend processes by pattern
kill_by_pattern() {
    echo "🔫 Step 3: Killing Python backend processes by pattern..."
    
    # Kill by specific patterns
    PATTERNS=(
        "uvicorn app.main:app"
        "python.*main.py"
        "python.*backend"
    )
    
    for pattern in "${PATTERNS[@]}"; do
        echo "   Checking for pattern: $pattern"
        PIDS=$(pgrep -f "$pattern" 2>/dev/null || echo "")
        
        if [ -n "$PIDS" ]; then
            echo "   Found PIDs for '$pattern': $PIDS"
            pkill -f "$pattern" 2>/dev/null || true
        fi
    done
    
    sleep 2
    echo "   ✅ Python processes cleared"
}

# Function to clean up zombie processes
cleanup_zombies() {
    echo "🧹 Cleaning up zombie processes..."
    
    # Kill any remaining uvicorn processes
    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "python.*:8000" 2>/dev/null || true
    
    # Clean up PID file if process doesn't exist
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE" 2>/dev/null || echo "")
        if [ -n "$PID" ] && [ "$PID" -gt 0 ] 2>/dev/null; then
            if ! ps -p "$PID" > /dev/null 2>&1; then
                echo "   Removing stale PID file (PID $PID not found)"
                rm -f "$PID_FILE"
            fi
        fi
    fi
    
    sleep 1
}

# Function to check if backend is running
check_backend_running() {
    if curl -s "http://localhost:$BACKEND_PORT/api/v1/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to start backend
start_backend() {
    echo "🚀 Step 4: Starting backend..."
    
    cd "$BACKEND_DIR"
    
    # Clean up old log file
    if [ -f "$LOG_FILE" ]; then
        echo "   📝 Rotating log file..."
        mv "$LOG_FILE" "${LOG_FILE}.old" 2>/dev/null || true
    fi
    
    # Start in background and save PID
    echo "   Starting uvicorn..."
    nohup uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload > "$LOG_FILE" 2>&1 &
    BACKEND_PID=$!
    
    echo $BACKEND_PID > "$PID_FILE"
    echo "   ✅ Started with PID: $BACKEND_PID"
    echo "   📝 Logs: $LOG_FILE"
    echo "   💾 PID saved: $PID_FILE"
    
    # Wait for backend to start
    echo "   ⏳ Waiting for backend to start (max $MAX_WAIT_SECONDS seconds)..."
    
    for ((i=1; i<=MAX_WAIT_SECONDS; i++)); do
        if check_backend_running; then
            echo "   ✅ Backend started successfully!"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    echo
    echo "   ⚠️  Backend might be slow to start or failed"
    echo "   Check logs: tail -f $LOG_FILE"
    
    # Check if process is still running
    if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
        echo "   ℹ️  Backend process $BACKEND_PID is still running"
        return 0
    else
        echo "   ❌ Backend process died. Check logs above."
        return 1
    fi
}

# Function to show process status
show_status() {
    echo
    echo "📊 FINAL STATUS:"
    echo "----------------"
    
    # Show current PID from file
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE" 2>/dev/null || echo "N/A")
        echo "Saved PID: $PID"
        
        if [ -n "$PID" ] && [ "$PID" -gt 0 ] 2>/dev/null; then
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "Process status: ✅ RUNNING (PID: $PID)"
            else
                echo "Process status: ❌ NOT RUNNING (PID $PID not found)"
            fi
        fi
    else
        echo "Saved PID: No PID file"
    fi
    
    # Show processes on port 8000
    echo
    echo "Processes on port $BACKEND_PORT:"
    lsof -i:$BACKEND_PORT 2>/dev/null | head -10 || echo "   None"
    
    # Check if backend responds
    echo
    if check_backend_running; then
        echo "✅ Backend is HEALTHY and responding to API calls"
    else
        echo "❌ Backend is NOT responding to API calls"
    fi
}

# Main execution
main() {
    echo "Starting optimized restart procedure..."
    echo
    
    # Step 1: Kill using saved PID first (most efficient)
    kill_by_pid_file || true  # Continue even if no process was killed
    
    # Step 2: Kill by port
    kill_by_port
    
    # Step 3: Kill by pattern
    kill_by_pattern
    
    # Step 4: Cleanup zombies
    cleanup_zombies
    
    # Step 5: Wait a moment
    echo
    echo "⏳ Waiting 2 seconds for cleanup..."
    sleep 2
    
    # Step 6: Start backend
    start_backend
    
    # Step 7: Show final status
    show_status
    
    echo
    echo "=========================================="
    echo "RESTART COMPLETE"
    echo "=========================================="
    echo
    echo "Quick commands:"
    echo "  tail -f $LOG_FILE          # View logs"
    echo "  cat $PID_FILE              # Show backend PID"
    echo "  ./restart_optimized.sh     # Restart again"
    echo
    echo "Test the backend:"
    echo "  curl http://localhost:8000/api/v1/health"
    echo "  python test_direct_token.py"
    echo
}

# Run main function
main "$@"