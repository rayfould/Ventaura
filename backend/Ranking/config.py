import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import random
from collections import deque
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime, timezone, timedelta
import logging
import math
import time
import os
from functools import lru_cache
import traceback
from pathlib import Path
from networkx.classes import non_edges
from sklearn.manifold import TSNE
from torch.fx.traceback import get_current_meta
from tqdm import tqdm
import seaborn as sns
#from torchviz import make_dot
import time
from pathlib import Path
from decimal import Decimal, getcontext
import pytz
import psutil
from contextlib import contextmanager
from collections import defaultdict
from fastapi import FastAPI, HTTPException
import uvicorn


# Constants
DEBUG_MODE = False
DEEP_DEBUG = False

# Training/Testing flags
TRAIN_MODEL = True  # Set to False to skip training
TEST_MODEL = False   # Set to False to skip testing
LOAD_MODEL_PATH = "Training/models/Model_11/recommender/final_model_20241114_195704.pth"  # Specific model path


# Hyperparameters
GAMMA = 0.99
LEARNING_RATE = 8e-3
BATCH_SIZE = 64
BUFFER_SIZE = 10000
NUM_EPISODES = 100
INITIAL_EPSILON = 1.0
FINAL_EPSILON = 0.01
TRAINING_PROGRESS = 0.8
DIVERSITY_WEIGHT = 0.3  # Weight for diversity bonus in reward
TARGET_UPDATE_FREQUENCY = 10
YOUR_MODEL_SIZE = 1000
TEMPERATURE = 0.5  # Controls exploration randomness
# Calculate DECAY_EPISODES before using it
DECAY_EPISODES = int(NUM_EPISODES * TRAINING_PROGRESS)

# Now calculate EPSILON_DECAY
# if DECAY_EPISODES > 0:
#     EPSILON_DECAY = float(Decimal('1.0') - (Decimal('1.0') - Decimal(str(FINAL_EPSILON))) ** (Decimal('1.0') / Decimal(str(DECAY_EPISODES))))
# else:
#     # Fallback value if DECAY_EPISODES is 0
#     EPSILON_DECAY = 0.995


EPSILON_DECAY = 0.999
# Base directory (project root)
BASE_DIR = Path(__file__).parent

# Main directories
TEST_DIR = BASE_DIR / 'Testing'
TRAIN_DIR = BASE_DIR / 'Training'

# Testing subdirectories
TEST_DATA_DIR = TEST_DIR / 'data'

# Training subdirectories
ANALYTICS_DIR = TRAIN_DIR / 'Analytics'
MODELS_DIR = TRAIN_DIR / 'Models'
LOGS_DIR = BASE_DIR / 'Logs'

# Create base directories
TEST_DIR.mkdir(parents=True, exist_ok=True)
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
TRAIN_DIR.mkdir(parents=True, exist_ok=True)
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)
current_dir = os.path.dirname(os.path.abspath(__file__))


def create_model_directories(model_num):
    """Create directory structure for a specific model number."""

    # Define base paths using Path objects
    analytics_base = ANALYTICS_DIR / f'Model_{model_num}'
    models_base = MODELS_DIR / f'Model_{model_num}'

    # Define directory structure
    directories = {
        'analytics': {
            'component_analysis': analytics_base / 'component_analysis',
            'training_metrics': analytics_base / 'training_metrics',
            'additional_analysis': analytics_base / 'additional_analysis'
        },
        'models': {
            'checkpoints': models_base / 'checkpoints',
            'recommender': models_base / 'recommender'
        },
        'base': {
            'analytics': analytics_base,
            'models': models_base
        }
    }

    # Create all directories
    for category in directories.values():
        if isinstance(category, dict):
            for dir_path in category.values():
                dir_path.mkdir(parents=True, exist_ok=True)
                debug_print(f"Created directory: {dir_path}")

    return directories



# Data file paths
EVENTS_CSV_PATH = TEST_DATA_DIR / '100_generated_events.csv'
USERS_CSV_PATH = TEST_DATA_DIR / 'diverse_users.csv'


def get_next_model_number():
    """Get the next available model number."""
    if not ANALYTICS_DIR.exists():
        return 1

    existing_models = [
        int(d.name.split('_')[1])
        for d in ANALYTICS_DIR.glob('Model_*')
        if d.name.split('_')[1].isdigit()
    ]
    return max(existing_models, default=0) + 1


# Create base directories
TEST_DIR.mkdir(parents=True, exist_ok=True)
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
TRAIN_DIR.mkdir(parents=True, exist_ok=True)
ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)



PRICE_RANGES = {
    '$': {'min': 0, 'max': 30},
    '$$': {'min': 31, 'max': 100},
    '$$$': {'min': 101, 'max': 300},
    'irrelevant': {'min': 0, 'max': float('inf')}
}

POPULARITY_RANGES = {
    'Small': {'min': 0, 'max': 100},      # Local events, workshops, meetups
    'Medium': {'min': 101, 'max': 500},   # Community events, local festivals
    'Large': {'min': 501, 'max': float('inf')},   # Major events, large festivals
    'irrelevant': {'min': 0, 'max': float('inf')}
}


PRICE_SCORING_CONFIG = {
    'free_event_score': .50,          # Score for free events
    'in_range_min_score': .50,        # Minimum score for events within range
    'under_budget_score': .50,        # Score for under-budget events
    'center_deviation_penalty': .50,   # How much to penalize deviation from center
    'over_budget_penalty_factor':.50  # Factor for over-budget penalty
}

RBS_PRICE_SCORING = {
    'free_event_score': 75,           # Free events are good for everyone
    'in_range_score': 100,            # Perfect match for user's range
    'under_budget_close_score': 75,    # Within 30% below range
    'under_budget_far_score': 50,      # More than 30% below range
    'over_budget_close_score': 50,     # Within 30% above range
    'over_budget_far_score': 0,        # More than 30% above range
    'irrelevant_score': 50,           # When price doesn't matter
    'tolerance_percentage': 0.3        # 30% tolerance for "close" scores
}


TIME_SCORING_CONFIG = {
    'max_preferred_hours': 336,  # 14 days
    'past_event_penalty': -100,
    'future_penalty_factor': 25
}

TIME_PREFERENCES = {
    'Morning': {'start': 6, 'end': 12},
    'Afternoon': {'start': 12, 'end': 17},
    'Evening': {'start': 17, 'end': 22},
    'Night': {'start': 22, 'end': 6},
    'Mixed': {'start': 0, 'end': 24},  # All times acceptable
    'irrelevant': {'start': 0, 'end': 24}
}



DISTANCE_SCORING_CONFIG = {
    'over_max_penalty_factor': 100
}

DISTANCE_RANGES = {
        "Very Local": 5,      # 0-5 km
        "Local": 15,          # 5-15 km
        "City-wide": 30,      # 15-30 km
        "Regional": 100,      # 30-100 km
        "Any Distance": 500   # No real limit
    }

# Add center-targeting config for other features
CENTER_TARGETING_CONFIG = {
    'popularity': {
        'deviation_penalty': 0.5,    # Changed from previous value to ensure scores stay in [-1, 1]
        'out_of_range_penalty': 0.5  # Changed from previous value to ensure scores stay in [-1, 1]
    },
    'distance': {
        'sweet_spot_percentage': 0.4, # Percentage of max distance that's ideal
        'deviation_penalty': .30       # How much to penalize deviation from sweet spot
    },
    'time': {
        'sweet_spot_hours': 48,       # Ideal number of hours in the future
        'deviation_penalty': .30       # How much to penalize deviation from sweet spot
    }
}



# Load common data
events_df = pd.read_csv(EVENTS_CSV_PATH)
users = pd.read_csv(USERS_CSV_PATH)
class TimeHandler:
    def __init__(self):
        self._timezone = pytz.UTC
        self._current_time = None

    def set_current_time(self, time=None):
        """Set current time for testing purposes"""
        self._current_time = time

    def get_current_time(self):
        """Get current time or mocked time if set (always timezone-naive)"""
        if self._current_time is not None:
            return self._current_time.replace(tzinfo=None)  # Return naive version of the mocked time
        return datetime.now(self._timezone).replace(tzinfo=None)  # Return naive current time

    def get_timestamp(self):
        """Get current timestamp in seconds"""
        return self.get_current_time().timestamp()


# Create singleton instance
time_handler = TimeHandler()
# Export functions
get_current_time = time_handler.get_current_time
get_timestamp = time_handler.get_timestamp

CURRENT_TIME = get_current_time()

# Setup logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def debug_print(message, force=False):
    """
    Print debug messages based on DEBUG_MODE.
    Args:
        message: Message to print
        force: If True, print regardless of DEBUG_MODE
    """
    if DEBUG_MODE or force:
        print(message)

def info_print(message):
    """Always print important information."""
    print(message)

def deep_print(message):
    if DEEP_DEBUG:
        print(message)

def log_edge_case(event_id, field_name, fallback_value):
    logging.info(f"Event {event_id} is missing {field_name}. Fallback value used: {fallback_value}")

# Common utility functions
def normalize_weights(weights):
    total = sum(weights.values())
    return {key: (value / total) for key, value in weights.items()}

def count_nan_events(df):
    nan_rows = df.isna().any(axis=1)
    return nan_rows.sum()


# Add helper function for case-insensitive lookup
def get_popularity_range(crowd_size):
    """Get popularity range with case-insensitive lookup."""
    if pd.isna(crowd_size):
        return POPULARITY_RANGES['IRRELEVANT']
    return POPULARITY_RANGES[crowd_size.upper()]



def monitor_memory():
    """Monitor memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


@contextmanager
def plot_context(figsize=(10, 6), subplots=False, *subplot_args, **subplot_kwargs):
    try:
        if subplots:
            fig, ax = plt.subplots(figsize=figsize, *subplot_args, **subplot_kwargs)
            yield fig, ax
        else:
            plt.figure(figsize=figsize)
            yield
    finally:
        plt.close('all')



# Existing configurations like PENALTY_CONFIG
PENALTY_CONFIG = {
    "price": {
        "tolerance_multiplier": 1.5,  # Allow 50% above max price before penalty
        "severe_penalty": 0.7        # Reduce score to 70% for severe price deviations
    },
    "distance": {
        "tolerance_multiplier": 1.2,  # Allow 20% above max distance before penalty
        "severe_penalty": 0.8         # Reduce score to 80% for severe distance deviations
    },
    "event_type": {
        "disliked_penalty": 0.5       # Reduce score to 50% for disliked event types
    },
    "time": {
        "far_future_threshold": 168,  # 7 days (in hours)
        "base_penalty": 0.9,  # Initial penalty (10%)
        "daily_decay": 0.05,  # Additional 5% penalty per day
        "min_penalty": 0.5  # Maximum 50% penalty
    }
}


# Helper function to get price range
def get_price_range(price_pref):
    return PRICE_RANGES.get(price_pref, PRICE_RANGES['irrelevant'])

@lru_cache(maxsize=128)
def normalize_event_type(event_type):
    """Normalize event type for consistent comparison."""
    if pd.isna(event_type):
        return np.nan
    return event_type.strip().lower().rstrip('s')  # Normalize case and remove trailing 's'


# Centralized penalty function
def apply_penalty(final_score, event, user):
    """
    Apply penalties to the final score if any field deviates significantly from user preferences.
    """
    penalty_multiplier = 1.0  # No penalty by default
    # Price penalty
    event_price = event['Price ($)']
    if event_price > 0:  # Ensure event price is valid
        user_price_pref = get_price_range(user['Price Range'])
        max_price = user_price_pref['max']
        tolerance_limit = max_price * PENALTY_CONFIG["price"]["tolerance_multiplier"]

        if event_price > tolerance_limit:  # Severe deviation from budget
            penalty_multiplier *= PENALTY_CONFIG["price"]["severe_penalty"]

    # Distance penalty
    event_distance = event['Distance (km)']
    max_distance = DISTANCE_RANGES[user['Max Distance']]
    tolerance_limit = max_distance * PENALTY_CONFIG["distance"]["tolerance_multiplier"]

    if event_distance > tolerance_limit:  # Severe deviation from max distance
        penalty_multiplier *= PENALTY_CONFIG["distance"]["severe_penalty"]

    # Event type penalty (Disliked category)
    event_type = normalize_event_type(event['Event Type'])
    if event_type in user['Disliked']:
        penalty_multiplier *= PENALTY_CONFIG["event_type"]["disliked_penalty"]

    # Far future event penalty
    time_difference = (event['Date/Time'] - CURRENT_TIME).total_seconds() / 3600
    if time_difference > PENALTY_CONFIG["time"]["far_future_threshold"]:
        # Calculate how many additional days beyond threshold
        days_beyond = (time_difference - PENALTY_CONFIG["time"]["far_future_threshold"]) / 24
        # Apply increasing penalty based on how far beyond threshold
        time_penalty = max(PENALTY_CONFIG["time"]["min_penalty"],
                           PENALTY_CONFIG["time"]["base_penalty"] - (
                                       days_beyond * PENALTY_CONFIG["time"]["daily_decay"]))
        penalty_multiplier *= time_penalty

    # Apply penalty multiplier to the final score
    penalized_score = final_score * penalty_multiplier
    return penalized_score
