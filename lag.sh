#!/bin/bash

# Kafka bootstrap server
BOOTSTRAP_SERVER="localhost:9092"

# Function to get consumer groups
get_consumer_groups() {
    kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVER --list
}

# Function to get consumer lag for a group
get_consumer_lag() {
    local group=$1
    kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVER --describe --group $group
}

# Main script
echo "Fetching consumer groups..."
groups=$(get_consumer_groups)

for group in $groups
do
    echo "Consumer group: $group"
    lag_output=$(get_consumer_lag $group)
    
    # Initialize variables
    declare -A topic_total_lag

    echo "$lag_output" | tail -n +3 | while read -r line
    do
        # Use awk to extract fields by column number
        topic=$(echo "$line" | awk '{print $2}')
        lag=$(echo "$line" | awk '{print $6}')
        
        # Skip if lag is 0 or negative
        if [[ -n "$lag" && "$lag" =~ ^[0-9]+$ && "$lag" -gt 0 ]]; then
            topic_total_lag[$topic]=$((${topic_total_lag[$topic]:-0} + lag))
        fi
    done
    
    # Print total lag for each topic
    for topic in "${!topic_total_lag[@]}"; do
        echo "  $topic: ${topic_total_lag[$topic]}"
    done
    
    echo ""
done
