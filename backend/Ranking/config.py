import numpy as np
import pandas as pd
import os
from datetime import datetime, timezone
from functools import lru_cache
import logging

# Constants
DEBUG_MODE = False
DEEP_DEBUG = False
BACKEND_URL = os.getenv("BACKEND_URL", "https://ventaura-backend-rayfould.fly.dev")

# Pricing and scoring configs
PRICE_RANGES = {
    '$': {'min': 0, 'max': 30},
    '$$': {'min': 31, 'max': 100},
    '$$$': {'min': 101, 'max': 300},
    'irrelevant': {'min': 0, 'max': float('inf')}
}

POPULARITY_RANGES = {
    'Small': {'min': 0, 'max': 100},
    'Medium': {'min': 101, 'max': 500},
    'Large': {'min': 501, 'max': float('inf')},
    'irrelevant': {'min': 0, 'max': float('inf')}
}

PRICE_SCORING_CONFIG = {
    'free_event_score': .50,
    'in_range_min_score': .50,
    'under_budget_score': .50,
    'center_deviation_penalty': .50,
    'over_budget_penalty_factor': .50
}

RBS_PRICE_SCORING = {
    'free_event_score': 75,
    'in_range_score': 100,
    'under_budget_close_score': 75,
    'under_budget_far_score': 50,
    'over_budget_close_score': 50,
    'over_budget_far_score': 0,
    'irrelevant_score': 50,
    'tolerance_percentage': 0.3
}

TIME_SCORING_CONFIG = {
    'max_preferred_hours': 336,
    'past_event_penalty': -100,
    'future_penalty_factor': 25
}

TIME_PREFERENCES = {
    'Morning': {'start': 6, 'end': 12},
    'Afternoon': {'start': 12, 'end': 17},
    'Evening': {'start': 17, 'end': 22},
    'Night': {'start': 22, 'end': 6},
    'Mixed': {'start': 0, 'end': 24},
    'irrelevant': {'start': 0, 'end': 24}
}

DISTANCE_SCORING_CONFIG = {
    'over_max_penalty_factor': 100
}

DISTANCE_RANGES = {
    "Very Local": 5,
    "Local": 15,
    "City-wide": 30,
    "Regional": 100,
    "Any Distance": 500
}

CENTER_TARGETING_CONFIG = {
    'popularity': {
        'deviation_penalty': 0.5,
        'out_of_range_penalty': 0.5
    },
    'distance': {
        'sweet_spot_percentage': 0.4,
        'deviation_penalty': .30
    },
    'time': {
        'sweet_spot_hours': 48,
        'deviation_penalty': .30
    }
}

PENALTY_CONFIG = {
    "price": {
        "tolerance_multiplier": 1.5,
        "severe_penalty": 0.7
    },
    "distance": {
        "tolerance_multiplier": 1.2,
        "severe_penalty": 0.8
    },
    "event_type": {
        "disliked_penalty": 0.5
    },
    "time": {
        "far_future_threshold": 168,
        "base_penalty": 0.9,
        "daily_decay": 0.05,
        "min_penalty": 0.5
    }
}

# No events_df needed here - app.py fetches it
events_df = None

# Time handling
class TimeHandler:
    def __init__(self):
        self._timezone = timezone.utc
        self._current_time = None

    def set_current_time(self, time=None):
        self._current_time = time

    def get_current_time(self):
        if self._current_time is not None:
            return self._current_time.replace(tzinfo=None)
        return datetime.now(self._timezone).replace(tzinfo=None)

    def get_timestamp(self):
        return self.get_current_time().timestamp()

time_handler = TimeHandler()
get_current_time = time_handler.get_current_time
get_timestamp = time_handler.get_timestamp
CURRENT_TIME = get_current_time()

# Logging setup
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Helper methods
def debug_print(message, force=False):
    if DEBUG_MODE or force:
        print(message)

def info_print(message):
    print(message)

def deep_print(message):
    if DEEP_DEBUG:
        print(message)

def log_edge_case(event_id, field_name, fallback_value):
    logging.info(f"Event {event_id} is missing {field_name}. Fallback value used: {fallback_value}")

def normalize_weights(weights):
    total = sum(weights.values())
    return {key: (value / total) for key, value in weights.items()}

def count_nan_events(df):
    nan_rows = df.isna().any(axis=1)
    return nan_rows.sum()

def get_popularity_range(crowd_size):
    if pd.isna(crowd_size):
        return POPULARITY_RANGES['irrelevant']
    return POPULARITY_RANGES[crowd_size.capitalize()]

def monitor_memory():
    import psutil
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def get_price_range(price_pref):
    return PRICE_RANGES.get(price_pref, PRICE_RANGES['irrelevant'])

@lru_cache(maxsize=128)
def normalize_event_type(event_type):
    if pd.isna(event_type):
        return np.nan
    return event_type.strip().lower().rstrip('s')

def apply_penalty(final_score, event, user):
    user_max_distance = user.get('Max Distance', 'Any Distance')
    max_distance = DISTANCE_RANGES.get(user_max_distance, float('inf')) if isinstance(user_max_distance, str) else user_max_distance
    penalty_multiplier = 1.0

    event_price = event['amount']
    if event_price > 0:
        user_price_pref = user.get('Price Range', 'irrelevant')
        if user_price_pref != 'irrelevant':
            price_range = get_price_range(user_price_pref)
            max_price = price_range['max']
            tolerance_limit = max_price * PENALTY_CONFIG["price"]["tolerance_multiplier"]
            if event_price > tolerance_limit:
                penalty_multiplier *= PENALTY_CONFIG["price"]["severe_penalty"]

    event_distance = event['distance']
    tolerance_limit = max_distance * PENALTY_CONFIG["distance"]["tolerance_multiplier"]
    if event_distance > tolerance_limit:
        penalty_multiplier *= PENALTY_CONFIG["distance"]["severe_penalty"]

    event_type = normalize_event_type(event['type'])
    if event_type in user['Disliked']:
        penalty_multiplier *= PENALTY_CONFIG["event_type"]["disliked_penalty"]

    time_difference = (event['start'] - CURRENT_TIME).total_seconds() / 3600
    if time_difference > PENALTY_CONFIG["time"]["far_future_threshold"]:
        days_beyond = (time_difference - PENALTY_CONFIG["time"]["far_future_threshold"]) / 24
        time_penalty = max(PENALTY_CONFIG["time"]["min_penalty"],
                           PENALTY_CONFIG["time"]["base_penalty"] - (days_beyond * PENALTY_CONFIG["time"]["daily_decay"]))
        penalty_multiplier *= time_penalty

    return final_score * penalty_multiplier