import subprocess
import csv
import time
from datetime import datetime, timedelta
import platform
import logging
from config import (
    TARGET,
    LOG_FILE,
    ROLLING_WINDOW_SIZE,
    THRESHOLD_MULTIPLIER,
    MAX_ENTRIES,
    EMOJI_NORMAL,
    EMOJI_MILD_SPIKE,
    EMOJI_MODERATE_SPIKE,
    EMOJI_SEVERE_SPIKE,
    EMOJI_TIMEOUT,
    PERIODS
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List to store all response times
response_times = []

def load_last_12_hours(log_file):
    try:
        with open(log_file, mode='r') as file:
            logging.info(f"Loading data from {log_file}")
            reader = list(csv.DictReader(file))
            now = datetime.now()
            twelve_hours_ago = now - timedelta(hours=12)
            temp_times = []

            for row in reversed(reader):
                timestamp_str = row.get('Timestamp', '')
                response_time_str = row.get('Response Time (ms)', '')

                if not timestamp_str or not response_time_str:
                    continue

                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except ValueError as e:
                    logging.error(f"Error parsing timestamp '{timestamp_str}': {e}")
                    continue

                if timestamp < twelve_hours_ago:
                    break

                try:
                    response_time = float(response_time_str)
                    temp_times.append(response_time)
                except ValueError as e:
                    logging.error(f"Error parsing response time '{response_time_str}': {e}")
                    continue
            
            response_times.extend(reversed(temp_times))
            logging.info(f"Loaded {len(temp_times)} entries from the last 12 hours")
            calculate_data_availability(len(temp_times))
    except FileNotFoundError:
        logging.warning(f"Log file {log_file} not found, starting with an empty list")

def calculate_data_availability(entries):
    for period, label in PERIODS:
        percentage = (entries / period) * 100 if entries <= period else 100
        logging.info(f"Data availability for {label}: {percentage:.2f}%")

def ping_host(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    if process.returncode == 0:
        for line in stdout.splitlines():
            if platform.system().lower() == 'windows':
                if b'Time=' in line:
                    time_ms = float(line.split(b'Time=')[1].split()[0].replace(b'ms', b''))
                    return time_ms
            else:
                if b'time=' in line:
                    time_ms = float(line.split(b'time=')[1].split()[0])
                    return time_ms
    return None

def calculate_rolling_average_and_std(times_list):
    if len(times_list) > 1:
        avg = sum(times_list) / len(times_list)
        variance = sum((x - avg) ** 2 for x in times_list) / len(times_list)
        std_dev = variance ** 0.5
        return avg, std_dev
    return None, None

def calculate_network_status(response_time, average, std_dev, threshold=2):
    if response_time is None:
        return EMOJI_TIMEOUT
    if average is not None and std_dev is not None:
        spike_value = (response_time - (average + threshold * std_dev)) / std_dev
        if spike_value > 3:
            return EMOJI_SEVERE_SPIKE
        elif spike_value > 2:
            return EMOJI_MODERATE_SPIKE
        elif spike_value > 1:
            return EMOJI_MILD_SPIKE
        elif spike_value > 0:
            return EMOJI_NORMAL
    return EMOJI_NORMAL

def calculate_average_of_last_n_entries(times_list, n):
    if len(times_list) > 0:
        return sum(times_list[-min(len(times_list), n):]) / min(len(times_list), n)
    return None

def main():
    # Load the last 12 hours of data
    load_last_12_hours(LOG_FILE)
    
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        headers = ["Timestamp", "Response Time (ms)"] + [label for _, label in PERIODS] + ["Status"]
        writer.writerow(headers)

        try:
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                response_time = ping_host(TARGET)
                
                if response_time is not None:
                    response_times.append(response_time)
                    if len(response_times) > MAX_ENTRIES:
                        response_times.pop(0)
                
                averages = [calculate_average_of_last_n_entries(response_times, period) for period, _ in PERIODS]
                avg, std_dev = calculate_rolling_average_and_std(response_times[-ROLLING_WINDOW_SIZE:])
                
                network_status = calculate_network_status(response_time, avg, std_dev, THRESHOLD_MULTIPLIER)

                # Prepare the printout message
                avg_info = ""
                for average, (_, label) in zip(averages, PERIODS):
                    if average is not None:
                        avg_info += f" | {label}: {average:8.2f} ms"

                if response_time is not None:
                    log_message = f"{network_status} {timestamp}: {response_time:8.3f} ms{avg_info}"
                else:
                    log_message = f"{network_status} {timestamp}: Timed out{avg_info}"
                
                writer.writerow([timestamp, response_time] + averages + [network_status])
                logging.info(log_message)
                
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Ping operation stopped.")

if __name__ == "__main__":
    main()
