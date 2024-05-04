#!/bin/bash

URL="http://localhost:8003/api/v1/test"

# Function to send request and measure time
send_request() {
    start=$(date +%s.%N)           # Capture start time
    curl -s "$URL" >>responses.txt # Send the request and discard the output
    end=$(date +%s.%N)             # Capture end time
    echo "Time taken: $(echo "$end - $start" | bc) seconds" >>log
}

# Number of concurrent requests
NUM_REQUESTS=500
lstart=$(date +%s.%N)
# Send requests concurrently
for ((i = 1; i <= $NUM_REQUESTS; i++)); do
    send_request &
done
lend=$(date +%s.%N) # Capture end time
echo "Time taken: $(echo "$lend - $lstart" | bc) seconds"

# Wait for all requests to finish
wait
