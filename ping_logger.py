import subprocess
import csv
import time
from datetime import datetime

# Set the target host and the log file name
target = "192.168.50.11"
log_file = "ping_log.csv"

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

# Open the CSV file in write mode and create a CSV writer
with open(log_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header row
    writer.writerow(["Timestamp", "Response Time (ms)"])

    # Continuous ping loop
    try:
        while True:
            # Get the current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Ping the target host
            response_time = ping_host(target)
            # Log the timestamp and response time to the CSV file
            writer.writerow([timestamp, response_time])
            # Print the log to the console
            if response_time is not None:
                print(f"{timestamp}: {response_time} ms")
            else:
                print(f"{timestamp}: Request timed out")
            # Wait for a second before the next ping
            time.sleep(1)
    except KeyboardInterrupt:
        print("Ping operation stopped.")
