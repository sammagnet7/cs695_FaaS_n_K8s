#!/bin/bash

# Function to calculate CPU utilization percentage
calculate_cpu_utilization_percentage() {
    local cpu_usage=$1
    local total_cpu_allocated=$2
    local cpu_percentage=$(echo "scale=2; ($cpu_usage / $total_cpu_allocated) * 100" | bc)
    echo "CPU Utilization Percentage: $cpu_percentage%"
}

# Function to calculate memory utilization percentage
calculate_memory_utilization_percentage() {
    local memory_usage=$1
    local total_memory_allocated=$2
    local memory_percentage=$(echo "scale=2; ($memory_usage / $total_memory_allocated) * 100" | bc)
    echo "Memory Utilization Percentage: $memory_percentage%"
}

# Get CPU and memory usage
cpu_usage=$(kubectl top pod --no-headers <pod_name >--containers | awk '{print $2}')
memory_usage=$(kubectl top pod --no-headers <pod_name >--containers | awk '{print $3}')

# Get total CPU and memory allocated to the pod
total_cpu_allocated=$(kubectl get pod <pod_name >-o=jsonpath='{.spec.containers[0].resources.requests.cpu}' | sed 's/m$//')
total_memory_allocated=$(kubectl get pod <pod_name >-o=jsonpath='{.spec.containers[0].resources.requests.memory}' | sed 's/Mi$//')

# Calculate and display utilization percentages
calculate_cpu_utilization_percentage "$cpu_usage" "$total_cpu_allocated"
calculate_memory_utilization_percentage "$memory_usage" "$total_memory_allocated"
