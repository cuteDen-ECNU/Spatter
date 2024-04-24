#!/bin/bash


python_processes=$(ps aux | grep '[p]ython')


echo "Terminating Python processes..."
echo "$python_processes" | while read -r line; do
    process_id=$(echo "$line" | awk '{print $2}')
    process_name=$(echo "$line" | awk '{print $11}')
    
    echo "Terminating process: $process_name (PID: $process_id)"
    kill -15 "$process_id"
done

echo "All Python processes terminated."
