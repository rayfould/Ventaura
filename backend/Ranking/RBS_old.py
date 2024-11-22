from config import *
from quicksort import *

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
users = pd.read_csv('Testing/data/diverse_users.csv')

users = users.rename(columns={
    'priceRange': 'Price Range',
    'preferences': 'Preferences',
    'disliked': 'Disliked',
    'distance': 'Max Distance'
})


# Start measuring time
start_time = time.time()

original_input = len(events_df)

# Current time for filtering out past events
current_time = get_current_time()


def load_user_events(user_id: int) -> pd.DataFrame:
    """Load events from user-specific CSV file."""
    csv_path = f"content/{user_id}.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"No events file found for user {user_id}")
    return pd.read_csv(csv_path)



events_df = events_df.rename(columns={
    'contentId': 'Event ID',
    'title': 'Event Type',  # Using title as event type
    'amount': 'Price ($)',  # Amount is the price
    'start': 'Date/Time',   # start is the datetime
    'distance': 'Distance (km)'  # distance is already correct
})

events_df['Date/Time'] = pd.to_datetime(events_df['Date/Time'], errors='coerce').dt.tz_localize(None)


# Create a mask for vectorized filtering
mask = (
    events_df['Date/Time'].notna() &  # Check start is not NaN
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
    'Event Type': 45,
    'Distance': 25,
    'Time': 15,
    'Price': 15
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
# Update user preferences processing
users['preferences'] = users['Preferences'].apply(
    lambda x: frozenset(normalize_event_type(e.strip())
                       for e in str(x).lower().split(',')
                       if pd.notna(e) and e.strip())
)
users['disliked'] = users['Disliked'].apply(
    lambda x: frozenset(normalize_event_type(e.strip())
                       for e in str(x).lower().split(',')
                       if pd.notna(e) and e.strip())
)



@lru_cache(maxsize=256)
def get_event_type_weight(preferred_events, undesirable_events, event_type):
    if event_type in preferred_events:
        return 1.0
    elif event_type in undesirable_events:
        return 0
    return .5



def get_price_range(price_pref):
    """Get price range with exact match."""
    if pd.isna(price_pref):
        return PRICE_RANGES['irrelevant']
    return PRICE_RANGES[price_pref]  # $ signs need exact match

@lru_cache(maxsize=128)
def score_price_relative(event_price, user_price_pref):
    """
    Score price based on user's preferred range (0-100 scale):
    - Within range: 100
    - Below range but within 30%: 75
    - Below range more than 30%: 50
    - Above range but within 30%: 50
    - Above range more than 30%: 0
    - Free events: 75
    - Irrelevant preference: 50
    """
    if pd.isna(event_price):
        return 0
    if event_price == 0:
        return RBS_PRICE_SCORING['free_event_score']

    price_range = get_price_range(user_price_pref)
    min_price, max_price = price_range['min'], price_range['max']
    tolerance = RBS_PRICE_SCORING['tolerance_percentage']

    if min_price <= event_price <= max_price:
        return RBS_PRICE_SCORING['in_range_score']
    if event_price < min_price:
        percent_below = (min_price - event_price) / min_price
        return RBS_PRICE_SCORING['under_budget_close_score'] if percent_below <= tolerance else RBS_PRICE_SCORING[
            'under_budget_far_score']
    if event_price > max_price:
        if max_price == float('inf'):
            return RBS_PRICE_SCORING['irrelevant_score']
        percent_above = (event_price - max_price) / max_price
        return RBS_PRICE_SCORING['over_budget_close_score'] if percent_above <= tolerance else RBS_PRICE_SCORING[
            'over_budget_far_score']


def time_score_multi_peak(time_difference):
    """
    Compute time score with a multi-peak strategy:
    - Immediate events get high scores.
    - Events close to the sweet spot get the highest scores.
    - Gradual decay for events far in the future.
    :param time_difference: Hours until the event starts.
    :return: Score between 0 and 100.
    """
    IMMEDIATE_PEAK = 6     # Immediate events peak at 6 hours
    SWEET_SPOT = 36        # Sweet spot for short-term planning (36 hours)
    TOLERANCE = 24         # Tolerance for sweet spot decay (1 day)
    LONG_TERM_DECAY_START = 72  # Start penalizing after 3 days
    LONG_TERM_DECAY_FACTOR = 0.05  # Gradual decay factor for long-term events

    if time_difference < 0:
        return 0  # Past events are invalid and scored lowest.

    # Immediate events (boost scores)
    if time_difference <= IMMEDIATE_PEAK:
        return 80 + (20 * (time_difference / IMMEDIATE_PEAK))  # Scale linearly to max 100.

    # Sweet spot events
    deviation = abs(time_difference - SWEET_SPOT)
    sweet_spot_score = 100 * math.exp(-((deviation / TOLERANCE) ** 2))

    # Gradual long-term decay for future events
    if time_difference > LONG_TERM_DECAY_START:
        decay = LONG_TERM_DECAY_FACTOR * (time_difference - LONG_TERM_DECAY_START)
        sweet_spot_score -= decay

    return max(0, min(100, sweet_spot_score))  # Clamp the score between 0 and 100.


def score_distance(distance, max_distance):
    """
    Score distances with a very lenient approach:
    - 0-30% of max: 100 points (perfect)
    - 30-100% of max: 98-90 points (very minimal penalty)
    - 100-200% of max: 90-40 points (gradual penalty zone)
    - >200% of max: 0 points

    Example for Very Local (5km):
    - 0-1.5km: 100 points (perfect)
    - 1.5-5km: 98-90 points (almost no penalty)
    - 5-10km: 90-40 points (gradual penalty)
    - >10km: 0 points
    """
    buffer_end = max_distance * 2.0  # Double the max distance for buffer zone

    # Perfect score for close distances (within 30% of max)
    if distance <= (max_distance * 0.3):
        return 100

    # Very minimal penalty for distances within max range
    if distance <= max_distance:
        # Extremely gentle linear decay from 98 to 90
        portion = (distance - (max_distance * 0.3)) / (max_distance * 0.7)
        return 98 - (8 * portion)  # Only 8 point drop across the whole range

    # Extended penalty zone - gradual decay from 90 to 40
    if distance <= buffer_end:
        portion = (distance - max_distance) / max_distance
        return 90 - (50 * portion)  # 50 point drop across the buffer zone

    # Too far
    return 0




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
    """Calculate score and optionally return breakdown if DEBUG_MODE is on."""
    scores = np.zeros(4)
    breakdown = {} if DEBUG_MODE else None

    # Event Type Score
    event_type = normalize_event_type(event['Event Type'])
    if pd.isna(event_type):
        scores[0] = 0
    else:
        scores[0] = get_event_type_weight(
            user['preferences'],
            user['disliked'],
            event_type
        ) * 100
    if DEBUG_MODE:
        breakdown[
            'Event Type'] = f"{round(scores[0] * normalized_weights['Event Type'], 2)}/{relative_weights['Event Type']}"

    # Distance Score
    event_distance = event['Distance (km)']
    max_distance = DISTANCE_RANGES.get(user.get('Max Distance', 'Any Distance'), DISTANCE_RANGES['Any Distance'])
    if pd.isna(event_distance):
        scores[1] = 0
    else:
        scores[1] = score_distance(float(event_distance), max_distance)
    if DEBUG_MODE:
        breakdown['Distance'] = f"{round(scores[1] * normalized_weights['Distance'], 2)}/{relative_weights['Distance']}"

    # Time Score
    time_difference = (event['Date/Time'] - CURRENT_TIME)
    time_in_hours = time_difference.total_seconds() / 3600
    scores[2] = time_score_multi_peak(time_in_hours)
    if DEBUG_MODE:
        breakdown['Time'] = f"{round(scores[2] * normalized_weights['Time'], 2)}/{relative_weights['Time']}"
        breakdown['Hours Until Event'] = f"{time_in_hours:.1f} hours"

    # Price Score
    scores[3] = score_price_relative(event['Price ($)'], user['Price Range'])
    if DEBUG_MODE:
        breakdown['Price'] = f"{round(scores[3] * normalized_weights['Price'], 2)}/{relative_weights['Price']}"

    # Calculate final score
    final_score = round(np.dot(scores, [normalized_weights['Event Type'],
                                        normalized_weights['Distance'],
                                        normalized_weights['Time'],
                                        normalized_weights['Price']]), 2)

    # Apply penalty
    penalized_score = apply_penalty(final_score, event, user)

    if DEBUG_MODE:
        breakdown['Raw Score'] = f"{final_score}/100"
        breakdown['Penalized Score'] = f"{penalized_score}/100"
        return penalized_score, breakdown

    return penalized_score


# List to hold tuples
event_scores = []
user = users.iloc[3]
# Calculate scores and create tuples of (event_id, score)
for index, event in events_df.iterrows():
    if DEBUG_MODE:
        score, _ = calculate_score(user, event)
    else:
        score = calculate_score(user, event)
    event_scores.append([event['Event ID'], score])

# Sort the events based on their scores
quick_sort(event_scores, 0, len(event_scores) - 1)

# Extract sorted Event IDs and scores
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
# Extract sorted Event IDs and scores
event_scores_detailed = []
for event_id, score in event_scores:
    event = events_df[events_df['Event ID'] == event_id].iloc[0]
    if DEBUG_MODE:
        final_score, breakdown = calculate_score(user, event)
    else:
        final_score = calculate_score(user, event)
    event_scores_detailed.append((event_id, score, final_score))

# Sort by penalized score
event_scores_detailed.sort(key=lambda x: x[2], reverse=True)
print("\nUser Preferences:")
print("=" * 50)  # Shorter separator since we have less columns

# Format user preferences
user_prefs = {
    'Preferred Events': user['Preferences'],
    'Disliked Events': user['Disliked'],
    'Price Range': user['Price Range'],
    'Max Distance': user['Max Distance']
}

# Calculate maximum key length for alignment
max_key_length = max(len(key) for key in user_prefs.keys())

# Print formatted user preferences
for key, value in user_prefs.items():
    print(f"{key:<{max_key_length + 2}}: {value}")

print("=" * 50)  # Bottom separator

print("\nTop Recommended Events:")
print("=" * 170)
print(f"{'Rank':<6}{'Event ID':<12}{'Event Type':<20}{'Price':<12}{'Distance':<15}{'Hours Until':<15}"
      f"{'Raw Score':<12}{'Final Score':<10}")
print("=" * 170)

for idx, (event_id, raw_score, final_score) in enumerate(event_scores_detailed, start=1):
    if idx > 10:  # Limit to top 10 events
        break

    event = events_df[events_df['Event ID'] == event_id].iloc[0]
    time_until = (event['Date/Time'] - CURRENT_TIME).total_seconds() / 3600

    print(f"{idx:<6}"  # Rank
          f"{event_id:<12}"  # Event ID
          f"{str(event['Event Type']).title():<20}"  # Event Type
          f"${float(event['Price ($)']):>8.2f}  "  # Price
          f"{float(event['Distance (km)']):>8.2f} km   "  # Distance with "km"
          f"{time_until:>8.1f} hrs  "  # Hours Until with "hrs"
          f"{raw_score:>8.2f}    "  # Raw Score
          f"{final_score:>8.2f}")  # Final Score

    # Detailed breakdown if DEBUG_MODE is enabled
    if DEBUG_MODE:
        score, breakdown = calculate_score(user, event)
        print("\nDetailed Breakdown:")
        for category, value in breakdown.items():
            print(f"{category}: {value}")
        print("-" * 100)

# Create DataFrame with rankings and save to CSV
ranked_df = events_df.copy()
ranked_df['Raw Score'] = ranked_df['Event ID'].map({id: raw for id, raw, _ in event_scores_detailed})
ranked_df['Final Score'] = ranked_df['Event ID'].map({id: final for id, _, final in event_scores_detailed})
ranked_df['Rank'] = ranked_df['Event ID'].map({id: idx for idx, (id, _, _) in enumerate(event_scores_detailed, 1)})

# Sort and save
ranked_df = ranked_df.sort_values('Final Score', ascending=False)
ranked_df = ranked_df[['Rank', 'Event ID', 'Raw Score', 'Final Score', 'Event Type', 'Price ($)',
                       'Distance (km)', 'Date/Time'] +
                      [col for col in ranked_df.columns if col not in
                       ['Rank', 'Event ID', 'Raw Score', 'Final Score', 'Event Type', 'Price ($)',
                        'Distance (km)', 'Date/Time']]]

ranked_df.to_csv("ranked_events.csv", index=False)
print(f"\nFull rankings saved to: ranked_events.csv")

def save_ranked_events(user_id: int, ranked_df: pd.DataFrame):
    """Save ranked events back to user's CSV file."""
    csv_path = f"content/{user_id}.csv"
    ranked_df.to_csv(csv_path, index=False)
