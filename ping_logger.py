import subprocess
import csv
import time
from datetime import datetime
from config import TARGET, LOG_FILE, ROLLING_WINDOW_SIZE, THRESHOLD_MULTIPLIER, MAX_ENTRIES

# List to store all response times
response_times = []

def ping_host(host):
    # Use the system's ping command to ping the host
    process = subprocess.Popen(["ping", "-c", "1", host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    if process.returncode == 0:
        # Parse the output to get the response time
        for line in stdout.splitlines():
            if b"time=" in line:
                time_ms = float(line.split(b"time=")[1].split()[0])
                return time_ms
    return None

def calculate_rolling_average_and_std(times_list):
    if len(times_list) > 1:
        avg = sum(times_list) / len(times_list)
        variance = sum((x - avg) ** 2 for x in times_list) / len(times_list)
        std_dev = variance ** 0.5
        return avg, std_dev
    return None, None

def is_spike(response_time, average, std_dev, threshold=2):
    if response_time is not None and average is not None and std_dev is not None:
        return response_time > average + (threshold * std_dev)
    return False

def calculate_average_of_last_n_entries(times_list, n):
    if len(times_list) == 0:
        return None
    return sum(times_list[-n:]) / min(len(times_list), n)

# Open the CSV file in write mode and create a CSV writer
with open(LOG_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(["Timestamp", "Response Time (ms)", "1m Avg (ms)", "5m Avg (ms)", "10m Avg (ms)", "Spike"])

    # Continuous ping loop
    try:
        while True:
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Ping the target host
            response_time = ping_host(TARGET)
            
            # Update the list of response times
            if response_time is not None:
                response_times.append(response_time)
                
                # Keep only the last MAX_ENTRIES entries for calculating averages
                if len(response_times) > MAX_ENTRIES:
                    response_times.pop(0)
            
            # Calculate averages
            one_min_avg = calculate_average_of_last_n_entries(response_times, 60)
            five_min_avg = calculate_average_of_last_n_entries(response_times, 300)
            ten_min_avg = calculate_average_of_last_n_entries(response_times, 600)
            
            # Calculate rolling average and standard deviation for spike detection
            avg, std_dev = calculate_rolling_average_and_std(response_times[-ROLLING_WINDOW_SIZE:])
            
            # Check for spikes
            spike_detected = is_spike(response_time, avg, std_dev, THRESHOLD_MULTIPLIER)
            
            # Log the timestamp, response time, and averages to the CSV file
            writer.writerow([timestamp, response_time, one_min_avg, five_min_avg, ten_min_avg, spike_detected])
            
            # Print the log to the console
            if response_time is not None:
                spike_msg = "Spike detected" if spike_detected else "No spike"
                print(f"{timestamp}: {response_time} ms | 1m Avg: {one_min_avg:.2f} ms | 5m Avg: {five_min_avg:.2f} ms | 10m Avg: {ten_min_avg:.2f} ms | {spike_msg}")
            else:
                print(f"{timestamp}: Request timed out | 1m Avg: {one_min_avg:.2f} ms | 5m Avg: {five_min_avg:.2f} ms | 10m Avg: {ten_min_avg:.2f} ms")
            
            # Wait for a second before the next ping
            time.sleep(1)
    except KeyboardInterrupt:
        print("Ping operation stopped.")