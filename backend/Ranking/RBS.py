from config import *
from quicksort import *

class EventRanking:
    def __init__(self, debug_mode=True, deep_debug=False):
        self.DEBUG_MODE = debug_mode
        self.DEEP_DEBUG = deep_debug
        self.CURRENT_TIME = self.get_current_time()
        self.events_df = None
        self.users = None
        self.event_scores = []
        self.nan_score_count = 0
        self.normalized_weights = {
            'type': 45,
            'Distance': 25,
            'Time': 15,
            'Price': 15
        }

        logging.basicConfig(filename='app.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

    @staticmethod
    def debug_print(message):
        if DEBUG_MODE or DEEP_DEBUG:
            print(message)

    @staticmethod
    def deep_print(message):
        if DEEP_DEBUG:
            debug_print(message)
            print(message)

    @staticmethod
    def log_edge_case(event_id, field_name, fallback_value):
        logging.info(f"Event {event_id} is missing {field_name}. Fallback value used: {fallback_value}")

    @staticmethod
    def get_current_time():
        return pd.Timestamp.now()

    def load_users(self, filepath='Testing/data/diverse_users.csv'):
        self.users = pd.read_csv(filepath)
        self.users = self.users.rename(columns={
            'priceRange': 'Price Range',
            'preferences': 'Preferences',
            'disliked': 'Disliked',
            'distance': 'Max Distance'
        })

    def load_events(self, events_df):
        self.events_df = events_df.copy()
        self.events_df['start'] = pd.to_datetime(self.events_df['start'], errors='coerce').dt.tz_localize(None)

    def filter_events(self):
        mask = (
            self.events_df['start'].notna() &
            (pd.to_datetime(self.events_df['start']) >= self.CURRENT_TIME) &
            (self.events_df[['type', 'distance', 'start']].isna().sum(axis=1) <= 2) &
            (self.events_df.isna().sum(axis=1) <= 4)
        )
        original_input = len(self.events_df)
        self.events_df = self.events_df[mask].reset_index(drop=True)
        events_removed = original_input - len(self.events_df)
        return events_removed

    def preprocess_users(self):
        self.users['preferences'] = self.users['Preferences'].apply(
            lambda x: frozenset(self.normalize_event_type(e.strip())
                                for e in str(x).lower().split(',')
                                if pd.notna(e) and e.strip())
        )
        self.users['disliked'] = self.users['Disliked'].apply(
            lambda x: frozenset(self.normalize_event_type(e.strip())
                                for e in str(x).lower().split(',')
                                if pd.notna(e) and e.strip())
        )

    @staticmethod
    @lru_cache(maxsize=128)
    def normalize_event_type(event_type):
        if pd.isna(event_type):
            return np.nan
        return event_type.lower().rstrip('s')
    @staticmethod
    @lru_cache(maxsize=256)
    def get_event_type_weight(preferred_events, undesirable_events, event_type):
        if event_type in preferred_events:
            return 1.0
        elif event_type in undesirable_events:
            return 0.0
        return 0.5  # Neutral score if not explicitly preferred or disliked

    @lru_cache(maxsize=128)
    def score_price_relative(self, event_price, user_price_pref):
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

    def time_score_multi_peak(self, time_difference):
        """
        Compute time score with a multi-peak strategy:
        - Immediate events get high scores.
        - Events close to the sweet spot get the highest scores.
        - Gradual decay for events far in the future.
        :param time_difference: Hours until the event starts.
        :return: Score between 0 and 100.
        """
        IMMEDIATE_PEAK = 6  # Immediate events peak at 6 hours
        SWEET_SPOT = 36  # Sweet spot for short-term planning (36 hours)
        TOLERANCE = 24  # Tolerance for sweet spot decay (1 day)
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

    def score_distance(self, distance, max_distance):
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

    def calculate_score(self, user, event):
        """Calculate score and optionally return breakdown if DEBUG_MODE is on."""
        scores = np.zeros(4)
        breakdown = {} if self.DEBUG_MODE else None

        # Type Score
        event_type = self.normalize_event_type(event['type'])
        if pd.isna(event_type):
            scores[0] = 0
        else:
            scores[0] = self.get_event_type_weight(
                user['Preferences'],
                user['Disliked'],
                event_type
            ) * 100
        if self.DEBUG_MODE:
            breakdown[
                'type'] = f"{round(scores[0] * self.normalized_weights['type'], 2)}/{self.normalized_weights['type']}"

        # Distance Score
        event_distance = event['distance']
        max_distance = DISTANCE_RANGES.get(user.get('Max Distance', 'Any Distance'), DISTANCE_RANGES['Any Distance'])
        if pd.isna(event_distance):
            scores[1] = 0
        else:
            scores[1] = self.score_distance(float(event_distance), max_distance)
        if self.DEBUG_MODE:
            breakdown[
                'Distance'] = f"{round(scores[1] * self.normalized_weights['Distance'], 2)}/{self.normalized_weights['Distance']}"

        # Time Score
        time_difference = (event['start'] - self.CURRENT_TIME)
        time_in_hours = time_difference.total_seconds() / 3600
        scores[2] = self.time_score_multi_peak(time_in_hours)
        if self.DEBUG_MODE:
            breakdown[
                'Time'] = f"{round(scores[2] * self.normalized_weights['Time'], 2)}/{self.normalized_weights['Time']}"
            breakdown['Hours Until Event'] = f"{time_in_hours:.1f} hours"

        # Price Score
        scores[3] = self.score_price_relative(event['amount'], user['Price Range'])
        if self.DEBUG_MODE:
            breakdown[
                'Price'] = f"{round(scores[3] * self.normalized_weights['Price'], 2)}/{self.normalized_weights['Price']}"

        # Calculate final score
        final_score = round(float(np.dot(scores, [self.normalized_weights['type'],
                                                  self.normalized_weights['Distance'],
                                                  self.normalized_weights['Time'],
                                                  self.normalized_weights['Price']])) / 100, 2)

        # Apply penalty
        penalized_score = apply_penalty(final_score, event, user)

        if self.DEBUG_MODE:
            breakdown['Raw Score'] = f"{final_score}/100"
            breakdown['Penalized Score'] = f"{penalized_score}/100"
            return penalized_score, breakdown

        return penalized_score

    def rank_events(self, user):
        """
        Rank events for a given user.

        Args:
            user: User preferences and settings

        Returns:
            tuple: (ranked_df, event_scores_detailed)
        """
        # Calculate scores and create tuples of (event_id, score)
        event_scores = []
        for index, event in self.events_df.iterrows():
            if self.DEBUG_MODE:
                score, _ = self.calculate_score(user, event)
            else:
                score = self.calculate_score(user, event)
            event_scores.append([event['contentId'], score])

        # Sort the events based on their scores
        quick_sort(event_scores, 0, len(event_scores) - 1)

        # Extract sorted contentIds and scores
        event_ids = [event_id for event_id, score in event_scores]
        scores = [score for event_id, score in event_scores]

        # Reorder events_df based on sorted event_ids
        sorted_events_df = self.events_df.set_index('contentId').loc[event_ids].reset_index()

        # Create detailed scores
        event_scores_detailed = []
        for event_id, score in event_scores:
            event = self.events_df[self.events_df['contentId'] == event_id].iloc[0]
            if self.DEBUG_MODE:
                final_score, breakdown = self.calculate_score(user, event)
            else:
                final_score = self.calculate_score(user, event)
            event_scores_detailed.append((event_id, score, final_score))

            # Create DataFrame with rankings
        ranked_df = self.events_df.copy()
        ranked_df['Raw Score'] = ranked_df['contentId'].map({id: raw for id, raw, _ in event_scores_detailed})
        ranked_df['Final Score'] = ranked_df['contentId'].map({id: final for id, _, final in event_scores_detailed})
        ranked_df['Rank'] = ranked_df['contentId'].map(
            {id: idx for idx, (id, _, _) in enumerate(event_scores_detailed, 1)})

        # Sort by Final Score
        ranked_df = ranked_df.sort_values('Final Score', ascending=False)

        # Remove scoring columns from the original DataFrame
        ranked_df = ranked_df.drop(['Rank', 'Raw Score', 'Final Score'], axis=1)

        return ranked_df, event_scores_detailed

    def save_ranked_events(self, user_id, ranked_df, save_dir = None):


        # Get the directory where RBS.py is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if save_dir is None:
            output_dir = os.path.join(current_dir, "API", "content")
        else:
            output_dir = save_dir

        print(f"Attempting to save ranked events to directory: {output_dir}")

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            print(f"Directory {output_dir} does not exist, creating it.")
            os.makedirs(output_dir)
        else:
            print(f"Directory {output_dir} exists.")

        # Construct the full path to the output CSV file
        csv_path = os.path.join(output_dir, f"{user_id}.csv")
        print(f"Saving ranked events to file: {csv_path}")

        # Save the DataFrame to CSV
        ranked_df.to_csv(csv_path, index=False)


if __name__ == "__main__":
    # Initialize the ranking system
    ranker = EventRanking(debug_mode=True)

    # Load events from a CSV file
    events_df = pd.read_csv("API/content/65.csv")  # Replace with your test file path
    ranker.load_events(events_df)

    # Filter out invalid events
    events_removed = ranker.filter_events()
    print(f"Removed {events_removed} invalid events")

    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.width', None)  # Width of the display in characters
    pd.set_option('display.max_colwidth', None)  # Show full content of each column

    # Create a test user
    test_user = {
        'Preferences': frozenset(['music', 'festival']),
        'Disliked': frozenset(['opera']),
        'Price Range': '$$',
        'Max Distance': 'Local'
    }

    # Print user preferences
    print("\nUser Preferences:")
    print(f"Preferred Events: {', '.join(sorted(test_user['Preferences']))}")
    print(f"Disliked Events: {', '.join(sorted(test_user['Disliked']))}")
    print(f"Price Range: {test_user['Price Range']}")
    print(f"Max Distance: {test_user['Max Distance']}")
    print("\n" + "=" * 80)  # Separator line

    # Rank events for the user
    ranked_df, detailed_scores = ranker.rank_events(test_user)

    # Print results with scores included
    print("\nTop 10 Ranked Events:")
    print(ranked_df[['contentId', 'type', 'amount',
                      'distance']].head(10).to_string(index=False))

    # Save results (without scores)
    ranker.save_ranked_events(65, ranked_df)