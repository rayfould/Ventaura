from config import *
import cProfile
start_time = time.time()

# Logging Configuration
logging.basicConfig(filename='tester.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
CURRENT_TIME = get_current_time()
# Helper Functions
def normalize_weights(weights):
    total = sum(weights.values())
    return {key: (value / total) for key, value in weights.items()}

@lru_cache(maxsize=128)
def normalize_event_type(event_type):
    """Normalize event type for consistency."""
    if pd.isna(event_type):
        return np.nan
    return event_type.lower().rstrip('s')

@lru_cache(maxsize=128)
def get_price_range(price_pref):
    """Retrieve price range based on user preference."""
    return PRICE_RANGES.get(price_pref, PRICE_RANGES['irrelevant'])

def score_minimize(value, best_value, worst_value):
    """Score lower values better on a scale from 0 to 100."""
    if value <= best_value:
        return 100
    elif value >= worst_value:
        return 0
    normalized_value = (value - best_value) / (worst_value - best_value)
    return 100 * np.exp(-2 * normalized_value)  # This will give scores between 0 and 100


def score_price_relative(event_price, user_price_pref):
    """Score event price relative to the user's preference."""
    if pd.isna(event_price):
        return 0
    if event_price == 0:
        return RBS_PRICE_SCORING['free_event_score']

    price_range = get_price_range(user_price_pref)
    min_price, max_price = price_range['min'], price_range['max']
    tolerance = RBS_PRICE_SCORING['tolerance_percentage']

    if min_price <= event_price <= max_price:
        return RBS_PRICE_SCORING['in_range_score']
    elif event_price < min_price:
        percent_below = (min_price - event_price) / min_price
        return (
            RBS_PRICE_SCORING['under_budget_close_score']
            if percent_below <= tolerance else RBS_PRICE_SCORING['under_budget_far_score']
        )
    else:  # event_price > max_price
        if max_price == float('inf'):
            return RBS_PRICE_SCORING['irrelevant_score']
        percent_above = (event_price - max_price) / max_price
        return (
            RBS_PRICE_SCORING['over_budget_close_score']
            if percent_above <= tolerance else RBS_PRICE_SCORING['over_budget_far_score']
        )

@lru_cache(maxsize=256)
def get_event_type_weight(preferred_events, undesirable_events, event_type):
    """Determine the weight for a given event type."""
    if event_type in preferred_events:
        return 1.0
    elif event_type in undesirable_events:
        return 0
    return 0.5
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


def calculate_score(user, event, last_event_time):
    """Calculate the score for a single event for a given user, including penalties."""
    normalized_weights = normalize_weights({
        'Event Type': 45,
        'Distance': 25,
        'Time': 15,
        'Price': 15
    })

    max_scores = {
        'Event Type': 45,
        'Distance': 25,
        'Time': 15,
        'Price': 15
    }

    scores = np.zeros(4)
    breakdown = {}

    # Event Type Score
    event_type = normalize_event_type(event['Event Type'])
    scores[0] = get_event_type_weight(
        user['Preferences'], user['Disliked'], event_type
    ) * 100 if pd.notna(event_type) else 0
    breakdown['Event Type'] = f"{round(scores[0] * normalized_weights['Event Type'], 2)}/{max_scores['Event Type']}"

    # 2. Distance Score
    event_distance = event['Distance (km)']
    max_distance = DISTANCE_RANGES.get(user.get('Max Distance', 'Any Distance'), DISTANCE_RANGES['Any Distance'])
    if pd.isna(event_distance):
        scores[1] = 0
    else:
        event_distance = float(event_distance)
        scores[1] = score_distance(event_distance, max_distance)
    breakdown['Distance'] = f"{round(scores[1] * normalized_weights['Distance'], 2)}/{max_scores['Distance']}"

    # Time Score
    time_difference = (event['Date/Time'] - CURRENT_TIME)
    time_in_hours = time_difference.total_seconds() / 3600
    scores[2] = time_score_multi_peak(time_in_hours)
    breakdown['Time'] = f"{round(scores[2] * normalized_weights['Time'], 2)}/{max_scores['Time']}"
    breakdown['Hours Until Event'] = f"{time_in_hours:.1f} hours"

    # Price Score
    scores[3] = score_price_relative(event['Price ($)'], user['Price Range'])
    breakdown['Price'] = f"{round(scores[3] * normalized_weights['Price'], 2)}/{max_scores['Price']}"

    # Weighted Final Score
    final_score = round(
        sum(scores[i] * normalized_weights[key] for i, key in enumerate(normalized_weights)), 2
    )
    breakdown['Final Score (Unpenalized)'] = f"{final_score}/100"

    # Apply penalty for extreme mismatches
    penalized_score = apply_penalty(final_score, event, user)
    breakdown['Final Score (Penalized)'] = f"{penalized_score}/100"

    return penalized_score, breakdown


# Load Data
users = pd.read_csv('Testing/data/diverse_users.csv').rename(columns={
    'userId': 'User ID',
    'preferences': 'Preferences',
    'disliked': 'Disliked',
    'priceRange': 'Price Range',
    'distance': 'Max Distance'
})

events_df = pd.read_csv('Testing/data/1000_generated_events.csv').rename(columns={
    'contentId': 'Event ID',
    'title': 'Event Type',
    'amount': 'Price ($)',
    'start': 'Date/Time',
    'distance': 'Distance (km)'
})
events_df['Date/Time'] = pd.to_datetime(events_df['Date/Time'], errors='coerce').dt.tz_localize(None)

# CLI Execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Score a single event for a specific user.")
    parser.add_argument("event_id", type=int, help="The ID of the event to score.")
    parser.add_argument("user_id", type=int, help="The ID of the user for whom to calculate the score.")
    args = parser.parse_args()

    event_id = args.event_id
    user_id = args.user_id
    LAST_EVENT_TIME = events_df['Date/Time'].max()

    try:
        user_row = users.loc[users['User ID'] == user_id]
        event_row = events_df.loc[events_df['Event ID'] == event_id]

        if user_row.empty or event_row.empty:
            raise ValueError(f"Event {event_id} or User {user_id} not found.")

        user = {
            'Preferences': frozenset(map(lambda x: normalize_event_type(x.strip()),
                                         str(user_row['Preferences'].values[0]).split(','))),
            'Disliked': frozenset(map(lambda x: normalize_event_type(x.strip()),
                                      str(user_row['Disliked'].values[0]).split(','))),
            'Price Range': user_row['Price Range'].values[0],
            'Max Distance': user_row['Max Distance'].values[0],
            'CURRENT_TIME': get_current_time()
        }

        event = event_row.iloc[0]
        score, breakdown = calculate_score(user, event, LAST_EVENT_TIME)

        print(f"\nScore for Event {event_id} for User {user_id}: {score:.2f}\n")
        print("Event Details:")
        print(event.to_string())
        # After printing event details, add this section:
        print("\nUser Details:")
        print("-" * 50)  # Separator line

        # Format user preferences
        user_prefs = {
            'Preferences': ', '.join(sorted(user['Preferences'])).title(),
            'Disliked Categories': ', '.join(sorted(user['Disliked'])).title(),
            'Price Range': user['Price Range'],
            'Max Distance': user['Max Distance']
        }

        # Calculate maximum key length for alignment
        max_key_length = max(len(key) for key in user_prefs.keys())

        # Print formatted user preferences
        for key, value in user_prefs.items():
            print(f"{key:<{max_key_length + 2}}: {value}")

        print("-" * 50)
        print("\nScore Breakdown:")
        for category, value in breakdown.items():
            print(f"{category}: {value}")
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        print(f"Execution Time: {elapsed_time:.2f} ms")


    except Exception as e:
        print(f"Error: {e}")
