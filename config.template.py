# Configuration constants

TARGET = "google.com"
LOG_FILE = "ping_log.csv"
ROLLING_WINDOW_SIZE = 60  # Number of entries to use for rolling average and std deviation
THRESHOLD_MULTIPLIER = 2  # Number of standard deviations to define a spike
MAX_ENTRIES = 600  # Maximum number of entries to keep; sufficient for 10-minute averages

# Emoji configurations for visual representation of ping status

EMOJI_NORMAL = "✅"
EMOJI_MILD_SPIKE = "⚠️"
EMOJI_MODERATE_SPIKE = "❗"
EMOJI_SEVERE_SPIKE = "🚨"
EMOJI_TIMEOUT = "❌"
