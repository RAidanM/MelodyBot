#!/bin/bash

WATCH_DIR="./"

RESTART_CMD="python ./main.py"

echo "Starting the server..."
$RESTART_CMD &
SERVER_PID=$!

cleanup() {
    echo "Stopping the server..."
    kill $SERVER_PID 2>/dev/null
    echo "Server stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

inotifywait -m -e modify,create,delete --format '%w%f' -r "$WATCH_DIR" --include '\.(py)$' |
while read FILE
do
    echo "Change detected in: $FILE"
    
    # Restart the server
    echo "Restarting the server..."
    kill $SERVER_PID
    $RESTART_CMD &
    SERVER_PID=$!
    echo "Server started"
done
