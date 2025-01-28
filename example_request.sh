#!/bin/bash

response=$(curl -s -X 'POST' \
  'http://127.0.0.1:8000/token' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=heman&password=password&scope=&client_id=string&client_secret=string')

# Extract the access_token from the response
access_token=$(echo "$response" | jq -r '.access_token')

# Run an instance of the model
task_response=$(curl -s -X 'POST' \
  'http://127.0.0.1:8000/tasks/run' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $access_token" \
  -H 'Content-Type: application/json' \
  -d '{
  "prune_measure": 0,
  "prune_quantiles": 0,
  "h3_zoom": 10,
  "sliders": [
    0
  ],
  "buffer_walk_distance": 0
}')

task_id=$(echo "$task_response" | jq -r '.task_id')

# And we download the map
output_dir="./output"  # Specify the directory where files will be saved
mkdir -p "$output_dir"       # Create the directory if it doesn't exist
output_file="$output_dir/map_$task_id.jpeg"

response=$(curl -s -X 'GET' \
  "http://127.0.0.1:8000/tasks/map/$task_id" \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $access_token" \
  --output "$output_file")
