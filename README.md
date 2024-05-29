# Python Ping Logger

<img src="./python-ping-logger-demo.gif" alt="Demo" width="500">

## tl;dr

- It has no dependencies other than Python's standard library and `ping`.
- It logs the pings to a target into a `csv` file.
- It prints out the 1m / 5m / 10m averages.
- It also detects spikes and shows you how big the spike is visually (mild: ⚠️, moderate: ❗, severe: 🚨).

## Why I created this?

Oh... I just want to know how stable is my BambuLab P1S to my network. If you
have one, you know its network is a bit flakey... Thus this tool.

## Who wrote this?

I pair-programmed this thing with ChatGPT. Mostly written solely by ChatGPT. I
only did the "driving" part of pair-programming.

You can find my chat (so far) here:

https://chatgpt.com/share/cf266469-0913-4ffd-a2ba-bfd12c784ec3

## How to Use

Ensure you have Python installed.

1. Clone the repository `git clone https://github.com/GPTInfused/python-ping-logger.git`
2. Configure:
   - Copy the `config.tempalte.py` as `config.py` file (`cp config.template.py config.py`)
   - Edit the `config.py` file to set your target host and other configurations
4. Run the Script: `python3 ping_logger.py`

## Configuration

- `TARGET`: The host you want to ping.
- `LOG_FILE`: The name of the CSV file where logs will be saved.
- `ROLLING_WINDOW_SIZE`: The number of entries for calculating rolling averages and standard deviations.
- `THRESHOLD_MULTIPLIER`: The number of standard deviations to consider for spike detection.
- `MAX_ENTRIES`: The maximum number of entries to keep in memory.

## Example Output

```
2024-05-29 12:34:56: 30 ms | 1m Avg: 25.67 ms | 5m Avg: 27.45 ms | 10m Avg: 28.34 ms | Spike detected !!
2024-05-29 12:34:57: 28 ms | 1m Avg: 25.70 ms | 5m Avg: 27.50 ms | 10m Avg: 28.37 ms | No spike
```

## Contributing

Feel free to submit issues or pull requests. Contributions are welcome!
License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

