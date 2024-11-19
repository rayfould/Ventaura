import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import time
import logging

from config import get_current_time
from quicksort import quick_sort, get_count
from functools import lru_cache
from datetime import datetime, timedelta


DEBUG_MODE = True
DEEP_DEBUG = False
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def debug_print(message):
    if DEBUG_MODE or DEEP_DEBUG:
        print(message)

def deep_print(message):
    if DEEP_DEBUG:
        debug_print(message)
        print(message)

def log_edge_case(event_id, field_name, fallback_value):
    logging.info(f"Event {event_id} is missing {field_name}. Fallback value used: {fallback_value}")

# Load users
users = pd.read_csv('Testing/data/users.csv')

# Start measuring time
start_time = time.time()

# Create DataFrame
#csv_file_path = "venv/100_generated_events.csv"
csv_file_path = "Testing/data/1000_generated_events.csv"
events_df = pd.read_csv(csv_file_path)
#events_df = pd.read_csv('events.csv')
original_input = len(events_df)

# Current time for filtering out past events
current_time = get_current_time()

# Create a mask for vectorized filtering
mask = (
    events_df['Date/Time'].notna() &  # Check Date/Time is not NaN
    (pd.to_datetime(events_df['Date/Time']) >= current_time) &  # Filter out past events
    (events_df[['Event Type', 'Distance (km)', 'Date/Time']].isna().sum(axis=1) <= 2) &  # Critical fields NaN check
    (events_df.isna().sum(axis=1) <= 4)  # Check total NaN count in all fields
)

# Apply the mask and reset index
events_df = events_df[mask].reset_index(drop=True)

# When reading the CSV

final_input = len(events_df)
events_removed = original_input - final_input

# Ensure the 'Date/Time' column is in datetime format
events_df['Date/Time'] = pd.to_datetime(events_df['Date/Time'], errors='coerce')

# Cache frequently accessed values
MAX_POPULARITY = events_df['Popularity'].max()
LAST_EVENT_TIME = events_df['Date/Time'].max()
nan_score_count = 0
CURRENT_TIME = get_current_time()

def normalize_weights(weights):
    total = sum(weights.values())
    return {key: (value / total) for key, value in weights.items()}


def count_nan_events(df):
    nan_rows = df.isna().any(axis=1)  # Check if any column in the row has NaN
    nan_count = nan_rows.sum()        # Sum up all rows with NaN values
    return nan_count


# Relative weights
relative_weights = {
    'Event Type': 3,
    'Distance': 2,
    'Time': 1.8,
    'Popularity': 1.2,
    'Price': 1.75,
    'Duration': .25
}

# Normalize weights once
normalized_weights = normalize_weights(relative_weights)

# Pre-process event types
@lru_cache(maxsize=128)
def normalize_event_type(event_type):
    if pd.isna(event_type):
        return np.nan
    return event_type.lower().rstrip('s')

# Vectorize event type normalization
events_df['Event Type'] = events_df['Event Type'].apply(normalize_event_type)
users['Preferred Events'] = users['Preferred Events'].str.lower().str.split(',').apply(lambda x: set(e.strip().rstrip('s') for e in x))
users['Undesirable Events'] = users['Undesirable Events'].str.lower().str.split(',').apply(lambda x: set(e.strip().rstrip('s') for e in x))

@lru_cache(maxsize=256)
def get_event_type_weight(preferred_events, undesirable_events, event_type):
    if event_type in preferred_events:
        return 1.0
    elif event_type in undesirable_events:
        return -1
    return 0


# Calculate average, min, and max of an arbitrary field for the given event type
@lru_cache(maxsize=1024)
def get_event_type_stats(event_type, field):
    """
    Retrieves the min, max, and mean statistics for a specific field and event type.

    Parameters:
    - source: The DataFrame containing the event data.
    - event_type: The event type to filter on.
    - field: The field (column) to calculate stats for.

    Returns:
    - A dictionary with min, max, and mean values for the specified field and event type.
    """
    event_data = events_df[events_df['Event Type'] == event_type]

    return {
        'min': event_data[field].min(),
        'max': event_data[field].max(),
        'mean': event_data[field].mean(),
        'std': event_data.std() or 1e-5
    }


# Pre-calculate common statistics for each event type and cache them
event_type_stats_cache = {}
for event_type in events_df['Event Type'].unique():
    if pd.notna(event_type):
        event_data = events_df[events_df['Event Type'] == event_type]

        # Price statistics
        price_data = event_data['Price ($)'].dropna()
        price_stats = {
            'mean': price_data.mean() if not price_data.empty else events_df['Price ($)'].mean(),
            'min': price_data.min() if not price_data.empty else events_df['Price ($)'].min(),
            'max': price_data.max() if not price_data.empty else events_df['Price ($)'].max(),
            'std': price_data.std() if not price_data.empty else 1e-5
        }

        # Duration statistics
        duration_data = event_data['Duration (hrs)'].dropna()
        duration_stats = {
            'mean': duration_data.mean() if not duration_data.empty else events_df['Duration (hrs)'].mean(),
            'min': duration_data.min() if not duration_data.empty else events_df['Duration (hrs)'].min(),
            'max': duration_data.max() if not duration_data.empty else events_df['Duration (hrs)'].max(),
            'std': duration_data.std() if not duration_data.empty else 1e-5
        }

        # Distance statistics
        distance_data = event_data['Distance (km)'].dropna()
        distance_stats = {
            'mean': distance_data.mean() if not distance_data.empty else events_df['Distance (km)'].mean(),
            'min': distance_data.min() if not distance_data.empty else events_df['Distance (km)'].min(),
            'max': distance_data.max() if not distance_data.empty else events_df['Distance (km)'].max(),
            'std': distance_data.std() if not distance_data.empty else 1e-5
        }

        # Popularity statistics
        popularity_data = event_data['Popularity'].dropna()
        popularity_stats = {
            'mean': popularity_data.mean() if not popularity_data.empty else events_df['Popularity'].mean(),
            'min': popularity_data.min() if not popularity_data.empty else events_df['Popularity'].min(),
            'max': popularity_data.max() if not popularity_data.empty else events_df['Popularity'].max(),
            'std': popularity_data.std() if not popularity_data.empty else 1e-5
        }

        event_type_stats_cache[event_type] = {
            'price_stats': price_stats,
            'duration_stats': duration_stats,
            'distance_stats': distance_stats,
            'popularity_stats': popularity_stats
        }

# Also create global statistics for fallback
global_stats = {
    'price_stats': {
        'mean': events_df['Price ($)'].mean(),
        'min': events_df['Price ($)'].min(),
        'max': events_df['Price ($)'].max(),
        'std': events_df['Price ($)'].std() or 1e-5
    },
    'duration_stats': {
        'mean': events_df['Duration (hrs)'].mean(),
        'min': events_df['Duration (hrs)'].min(),
        'max': events_df['Duration (hrs)'].max(),
        'std': events_df['Duration (hrs)'].std() or 1e-5
    },
    'distance_stats': {
        'mean': events_df['Distance (km)'].mean(),
        'min': events_df['Distance (km)'].min(),
        'max': events_df['Distance (km)'].max(),
        'std': events_df['Distance (km)'].std() or 1e-5
    },
    'popularity_stats': {
        'mean': events_df['Popularity'].mean(),
        'min': events_df['Popularity'].min(),
        'max': events_df['Popularity'].max(),
        'std': events_df['Popularity'].std() or 1e-5
    }
}

@lru_cache(maxsize=128)
def score_price_relative(event_price, event_type):
    """
    Scores the price of an event relative to its event type.

    Parameters:
    - event_price: The price of the event.
    - event_type: The type of the event.

    Returns:
    - score: A score between -100 and 100.
    """
    if pd.isna(event_type) or event_type not in event_type_stats_cache:
        # Fallback to global statistics
        stats = {
            'mean': events_df['Price ($)'].mean(),
            'min': events_df['Price ($)'].min(),
            'max': events_df['Price ($)'].max()
        }
    else:
        stats = event_type_stats_cache[event_type]['price_stats']

    avg_price = stats['mean']
    min_price = stats['min']
    max_price = stats['max']

    if event_price <= avg_price:
        # Reward for being below or at average price
        if event_price == min_price:
            out = 100  # Best possible score for the lowest price
        else:
            price_range = avg_price - min_price
            if price_range == 0:
                # All prices are the same; assign maximum score
                out = 100
            else:
                ratio = (avg_price - event_price) / price_range
                out = 50 + (ratio * 50)  # Scores between 50 and 100
    else:
        # Penalize for being above average price
        price_range = max_price - avg_price
        if price_range == 0:
            # All prices are the same; assign neutral score
            out = 50
        else:
            ratio = (event_price - avg_price) / price_range
            out = 50 - (ratio * 150)  # Scores between -100 and 50
    return out

@lru_cache(maxsize=128)
def score_minimize(value, best_value, worst_value):
    """
    Scores a value on a scale from -100 to 100, where lower values are better.

    Parameters:
    - value: The current value being evaluated.
    - best_value: The ideal lowest value (e.g., 0 for distance).
    - worst_value: The maximum acceptable value before maximum penalty.

    Returns:
    - score: The calculated score between -100 and 100.
    """
    if value <= best_value:
        return 100  # Best score
    elif value >= worst_value:
        return -100  # Worst score (harsh punishment for far outliers)
    else:
        # Normalize the value and apply a sharper exponential drop-off
        normalized_value = (value - best_value) / (worst_value - best_value)
        penalty = 100 * (1 - np.exp(-5 * normalized_value))  # Steeper drop-off
        return 100 - penalty

@lru_cache(maxsize=128)
def score_maximize(value, best_value, worst_value):
    """
    Scores a value on a scale from -100 to 100, where higher values are better.

    Parameters:
    - value: The current value being evaluated.
    - best_value: The ideal highest value.
    - worst_value: The minimum acceptable value before maximum penalty.

    Returns:
    - score: The calculated score between -100 and 100.
    """
    if value >= best_value:
        return 100  # Best score
    elif value <= worst_value:
        return -100  # Worst score (harsh punishment for far outliers)
    else:
        # Normalize the value and apply a sharper exponential drop-off
        normalized_value = (best_value - value) / (best_value - worst_value)
        reward = 100 * (1 - math.exp(-5 * normalized_value))  # Steeper drop-off
        return 100 - reward

@lru_cache(maxsize=128)
def score_target(value, target_value, acceptable_range):
    """
    Scores a value based on its proximity to a target value.

    Parameters:
    - value: The current value being evaluated.
    - target_value: The ideal target value.
    - acceptable_range: The maximum deviation from the target value before maximum penalty.

    Returns:
    - score: The calculated score between -100 and 100.
    """
    deviation = abs(value - target_value)
    if deviation >= acceptable_range:
        return -100  # Worst score (harsh punishment for far outliers)
    else:
        # Normalize the deviation and apply a sharper exponential drop-off
        normalized_deviation = deviation / acceptable_range
        penalty = 100 * (1 - math.exp(-5 * normalized_deviation))  # Steeper drop-off
        return 100 - penalty


def calculate_score(user, event):
    event_type = event['Event Type']

    # Get cached stats if available, otherwise use global stats
    cached_stats = event_type_stats_cache.get(event_type, global_stats) if pd.notna(event_type) else global_stats

    # Initialize scores array for vectorized calculation
    scores = np.zeros(6)
    weights = np.array([
        normalized_weights['Event Type'],
        normalized_weights['Distance'],
        normalized_weights['Time'],
        normalized_weights['Popularity'],
        normalized_weights['Price'],
        normalized_weights['Duration']
    ])

    # Initialize a dictionary to store individual component scores (for debugging)
    component_scores = {}

    # 1. Event Type Score (Critical field - if null, return low score but not lowest)
    if pd.isna(event_type):
        scores[0] = -50
        log_edge_case(event['Event ID'], 'Event Type', -50)
        fallback_event_type = True
    else:
        scores[0] = get_event_type_weight(
            frozenset(user['Preferred Events']),
            frozenset(user['Undesirable Events']),
            event_type
        ) * 100
        fallback_event_type = False  # Means event type is available

    adjusted_event_score = scores[0] * normalized_weights['Event Type']
    component_scores['Event Type'] = scores[0]

    # Debugging messages
    debug_print(f"Event {event['Event ID']} - Event Type {event_type}")
    debug_print(f"Event {event['Event ID']} - Event Type Score: {scores[0]}")
    debug_print(f"Event {event['Event ID']} - Weight-adjusted Event Type Score: {adjusted_event_score}")

    # 2. Distance Score
    event_distance = event['Distance (km)']
    if pd.isna(event_distance):
        event_distance = cached_stats['distance_stats']['mean']
        log_edge_case(event['Event ID'], 'Distance', f"using mean: {event_distance}")

    scores[1] = score_minimize(event_distance, 0, user['Max Distance (km)'] * 2)
    adjusted_distance_score = scores[1] * normalized_weights['Distance']
    component_scores['Distance'] = scores[1]

    # Debugging messages
    debug_print(f"Event {event['Event ID']} - Distance {event_distance}")
    debug_print(f"Event {event['Event ID']} - Distance Score: {scores[1]}")
    debug_print(f"Event {event['Event ID']} - Weight-adjusted Distance Score: {adjusted_distance_score}")

    # 3. Time Score
    time_difference = (event['Date/Time'] - CURRENT_TIME)
    time_in_hours = time_difference.total_seconds() / 3600
    max_time_difference = (LAST_EVENT_TIME - CURRENT_TIME).total_seconds() / 3600
    scores[2] = score_minimize(time_in_hours, 0, max_time_difference)
    adjusted_time_score = scores[2] * normalized_weights['Time']
    component_scores['Time'] = scores[2]

    # Debugging messages
    debug_print(f"Event {event['Event ID']} - Time Until Event {time_in_hours} hours")
    debug_print(f"Event {event['Event ID']} - Time Score: {scores[2]}")
    debug_print(f"Event {event['Event ID']} - Weight-adjusted Time Score: {adjusted_time_score}")

    # 4. Popularity Score
    event_popularity = event['Popularity']
    if pd.isna(event_popularity):
        event_popularity = cached_stats['popularity_stats']['mean']
        log_edge_case(event['Event ID'], 'Popularity', f"using mean: {event_popularity}")

    scores[3] = score_maximize(event_popularity, MAX_POPULARITY, 0)
    adjusted_popularity_score = scores[3] * normalized_weights['Popularity']
    component_scores['Popularity'] = scores[3]

    # Debugging messages
    deep_print(f"max_popularity = {MAX_POPULARITY}")
    debug_print(f"Event {event['Event ID']} - Popularity {event_popularity}")
    debug_print(f"Event {event['Event ID']} - Popularity Score: {scores[3]}")
    debug_print(f"Event {event['Event ID']} - Weight-adjusted Popularity Score: {adjusted_popularity_score}")

    # 5. Price Score
    event_price = event['Price ($)']
    if pd.isna(event_price):
        event_price = cached_stats['price_stats']['mean']
        log_edge_case(event['Event ID'], 'Price', f"using mean: {event_price}")

    scores[4] = score_price_relative(event_price, event_type)
    adjusted_price_score = scores[4] * normalized_weights['Price']
    component_scores['Price'] = scores[4]

    # Debugging messages
    deep_print(f"Event {event['Event ID']} - Current Event Price {event_price}")
    debug_print(f"Event {event['Event ID']} - Price Score: {scores[4]}")
    debug_print(f"Event {event['Event ID']} - Weight-adjusted Price Score: {adjusted_price_score}")

    # 6. Duration Score
    event_duration = event['Duration (hrs)']
    if pd.isna(event_duration):
        stats = cached_stats['duration_stats']
        event_duration = stats['mean']
        log_edge_case(event['Event ID'], 'Duration', f"using mean: {event_duration}")

    scores[5] = score_target(
        event_duration,
        cached_stats['duration_stats']['min'],
        cached_stats['duration_stats']['max']
    )

    adjusted_duration_score = scores[5] * normalized_weights['Duration']
    component_scores['Duration'] = scores[5]

    # Debugging messages
    deep_print(f"Event {event['Event ID']} - Min Duration Per Event Type {cached_stats['duration_stats']['min']}")
    deep_print(f"Event {event['Event ID']} - Max Duration Per Event Type {cached_stats['duration_stats']['max']}")
    deep_print(f"Event {event['Event ID']} - Mean Duration Per Event Type {event_duration}")
    debug_print(f"Event {event['Event ID']} - Duration Score: {scores[5]}")
    debug_print(f"Event {event['Event ID']} - Weight-adjusted Duration Score: {adjusted_duration_score}")

    # Calculate final score using vectorized operation
    final_score = np.dot(scores, weights)

    # Debugging final score
    debug_print(f"Event {event['Event ID']} - Total Score: {final_score}")

    if pd.isna(final_score):
        global nan_score_count
        nan_score_count += 1
        log_edge_case(event['Event ID'], 'Final Score', 'NaN final score')

    return final_score


# List to hold tuples
event_scores = []
user = users.iloc[0]
# Calculate scores and create tuples of (event_id, score)
for index, event in events_df.iterrows():
    score = calculate_score(user, event)
    event_id = event['Event ID']
    event_scores.append([event_id, score])

# Sort the events based on their scores
quick_sort(event_scores, 0, len(event_scores) - 1)

# Extract sorted event IDs and scores
event_ids = [event_id for event_id, score in event_scores]
scores = [score for event_id, score in event_scores]

# Reorder events_df based on sorted event_ids
sorted_events_df = events_df.set_index('Event ID').loc[event_ids].reset_index()

# End time
end_time = time.time()
elapsed_time = (end_time - start_time) * 1000  # Convert to milliseconds

num_entries = len(events_df)
nan_events = count_nan_events(events_df)
print(f"Number of events processed: {num_entries}")
print(f"Total events excluded due to unfit conditions: {events_removed}")
print(f"Total number of comparisons made during sorting: {get_count()}")
print(f"Events with nan fields:{nan_events} ")
print(f"Number of events with NaN final scores: {nan_score_count}")
print(f"Code execution finished in {elapsed_time:.2f} ms")


# Extract sorted event IDs and scores
sorted_event_ids = [event_id for event_id, score in event_scores]
sorted_event_scores = [score for event_id, score in event_scores]

# Print sorted event IDs and scores
if DEBUG_MODE:
    print("Sorted Events by Score:")
    for idx, (event_id, score) in enumerate(zip(sorted_event_ids, sorted_event_scores), start=1):
        print(f"Rank {idx}: Event ID {event_id}, Score {score}")


# Plot sorted data
if num_entries < 101:
    fig, ax = plt.subplots(figsize=(20, 6))
else:
    fig, ax = plt.subplots(figsize=(350, 150))

if num_entries <= 100:
    ax.bar(range(len(event_ids)), scores, color='blue')  # Use a range for the x-axis instead of event_ids
    ax.set_xlabel('Event ID')
    ax.set_ylabel('Score')
    ax.set_title('Event Scores')
    ax.set_xticks(range(len(event_ids)))  # Make sure x-axis ticks align with the bars
    ax.set_xticklabels(event_ids)  # Label the ticks with sorted event IDs
    ax.grid(True)

    # # Add table below the graph with sorted event details
    # table_data = sorted_events_df[['Event ID', 'Event Type', 'Location', 'Distance (km)', 'Popularity', 'Price ($)']]
    # table = ax.table(cellText=table_data.values, colLabels=table_data.columns, cellLoc='center', loc='bottom', bbox=[0, -0.4, 1, 0.3])

    # Adjust layout
    plt.subplots_adjust(left=0.2, bottom=0.3)

    # Show plot
    plt.show()