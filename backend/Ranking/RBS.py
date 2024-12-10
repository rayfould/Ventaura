import os
import pandas as pd
import numpy as np
import math
import logging
from functools import lru_cache
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

    def debug_print(self, message):
        if self.DEBUG_MODE or self.DEEP_DEBUG:
            print(message)
            logging.info(message)

    def deep_print(self, message):
        if self.DEEP_DEBUG:
            self.debug_print(message)
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
        self.debug_print("Columns in events_df before processing: " + ", ".join(self.events_df.columns.tolist()))
        if 'start' not in self.events_df.columns:
            logging.error("The 'start' column is missing from events_df.")
            raise KeyError("The 'start' column is missing from events_df.")
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
        self.debug_print(f"Filtered events: Removed {events_removed} invalid events")
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
        return 0.5

    @lru_cache(maxsize=128)
    def score_price_relative(self, event_price, user_price_pref):
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
            return RBS_PRICE_SCORING['under_budget_close_score'] if percent_below <= tolerance else RBS_PRICE_SCORING['under_budget_far_score']
        if event_price > max_price:
            if max_price == float('inf'):
                return RBS_PRICE_SCORING['irrelevant_score']
            percent_above = (event_price - max_price) / max_price
            return RBS_PRICE_SCORING['over_budget_close_score'] if percent_above <= tolerance else RBS_PRICE_SCORING['over_budget_far_score']

    def time_score_multi_peak(self, time_difference):
        IMMEDIATE_PEAK = 6
        SWEET_SPOT = 36
        TOLERANCE = 24
        LONG_TERM_DECAY_START = 72
        LONG_TERM_DECAY_FACTOR = 0.05

        if time_difference < 0:
            return 0

        if time_difference <= IMMEDIATE_PEAK:
            return 80 + (20 * (time_difference / IMMEDIATE_PEAK))

        deviation = abs(time_difference - SWEET_SPOT)
        sweet_spot_score = 100 * math.exp(-((deviation / TOLERANCE) ** 2))

        if time_difference > LONG_TERM_DECAY_START:
            decay = LONG_TERM_DECAY_FACTOR * (time_difference - LONG_TERM_DECAY_START)
            sweet_spot_score -= decay

        return max(0, min(100, sweet_spot_score))

    def score_distance(self, distance, max_distance):
        buffer_end = max_distance * 2.0

        if distance <= (max_distance * 0.3):
            return 100

        if distance <= max_distance:
            portion = (distance - (max_distance * 0.3)) / (max_distance * 0.7)
            return 98 - (8 * portion)

        if distance <= buffer_end:
            portion = (distance - max_distance) / max_distance
            return 90 - (50 * portion)

        return 0

    def calculate_score(self, user, event):
        # Compute dimension scores as fractions (0.0 to 1.0)
        # Then final score is sum of (dimension_score * dimension_weight)
        # This ensures no dimension exceeds its assigned weight.
        breakdown = {} if self.DEBUG_MODE else None

        # Type Score (fraction)
        event_type = self.normalize_event_type(event['type'])
        if pd.isna(event_type):
            type_fraction = 0.0
        else:
            type_fraction = self.get_event_type_weight(
                user['Preferences'],
                user['Disliked'],
                event_type
            )  # 0.0, 0.5, or 1.0
        # Distance Score (fraction)
        event_distance = event['distance']
        user_max_distance = user.get('Max Distance', 'Any Distance')
        if isinstance(user_max_distance, (int, float)):
            max_distance = user_max_distance
        else:
            max_distance = DISTANCE_RANGES.get(user_max_distance, DISTANCE_RANGES['Any Distance'])

        if pd.isna(event_distance):
            distance_fraction = 0.0
        else:
            distance_fraction = self.score_distance(float(event_distance), max_distance) / 100.0

        # Time Score (fraction)
        time_difference = (event['start'] - self.CURRENT_TIME)
        time_in_hours = time_difference.total_seconds() / 3600
        time_fraction = self.time_score_multi_peak(time_in_hours) / 100.0

        # Price Score (fraction)
        price_fraction = self.score_price_relative(event['amount'], user['Price Range']) / 100.0

        # Compute weighted sum
        final_score = (
            (type_fraction * self.normalized_weights['type']) +
            (distance_fraction * self.normalized_weights['Distance']) +
            (time_fraction * self.normalized_weights['Time']) +
            (price_fraction * self.normalized_weights['Price'])
        )

        penalized_score = apply_penalty(final_score, event, user)

        if self.DEBUG_MODE:
            # Show each dimension as actual points out of their weight
            breakdown['Type Score'] = f"{round(type_fraction * self.normalized_weights['type'], 2)}/{self.normalized_weights['type']}"
            breakdown['Distance Score'] = f"{round(distance_fraction * self.normalized_weights['Distance'], 2)}/{self.normalized_weights['Distance']}"
            breakdown['Time Score'] = f"{round(time_fraction * self.normalized_weights['Time'], 2)}/{self.normalized_weights['Time']}"
            breakdown['Price Score'] = f"{round(price_fraction * self.normalized_weights['Price'], 2)}/{self.normalized_weights['Price']}"

            breakdown['Hours Until Event'] = f"{time_in_hours:.1f} hours"
            breakdown['Raw Score'] = f"{final_score}/100"
            breakdown['Penalized Score'] = f"{penalized_score}/100"
            event_info = f"Event ID: {event['contentId']} | Final Score: {penalized_score}/100"
            self.debug_print(event_info)
            for key, value in breakdown.items():
                self.debug_print(f"    {key}: {value}")
            self.debug_print("-" * 50)
            return final_score, penalized_score, breakdown

        return final_score, penalized_score

    def rank_events(self, user):
        event_scores_detailed = []
        event_scores = []

        for index, event in self.events_df.iterrows():
            if self.DEBUG_MODE:
                raw_score, final_score, breakdown = self.calculate_score(user, event)
                event_scores_detailed.append((event['contentId'], raw_score, final_score, breakdown))
            else:
                raw_score, final_score = self.calculate_score(user, event)
                event_scores_detailed.append((event['contentId'], raw_score, final_score))
            event_scores.append([event['contentId'], final_score])

        quick_sort(event_scores, 0, len(event_scores) - 1)

        event_ids = [event_id for event_id, score in event_scores]
        scores = [score for event_id, score in event_scores]

        sorted_events_df = self.events_df.set_index('contentId').loc[event_ids].reset_index()

        ranked_df = self.events_df.copy()

        if self.DEBUG_MODE:
            ranked_df['Raw Score'] = ranked_df['contentId'].map({eid: rs for eid, rs, fs, bd in event_scores_detailed})
            ranked_df['Final Score'] = ranked_df['contentId'].map({eid: fs for eid, rs, fs, bd in event_scores_detailed})
        else:
            ranked_df['Raw Score'] = ranked_df['contentId'].map({eid: rs for eid, rs, fs in event_scores_detailed})
            ranked_df['Final Score'] = ranked_df['contentId'].map({eid: fs for eid, rs, fs in event_scores_detailed})

        ranked_df = ranked_df.sort_values('Final Score', ascending=False)
        ranked_df = ranked_df.drop(['Raw Score', 'Final Score'], axis=1)

        return ranked_df, event_scores_detailed

    def save_ranked_events(self, user_id, ranked_df, save_dir=None):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if save_dir is None:
            output_dir = os.path.join(current_dir, "API", "content")
        else:
            output_dir = save_dir

        print(f"Attempting to save ranked events to directory: {output_dir}")

        if not os.path.exists(output_dir):
            print(f"Directory {output_dir} does not exist, creating it.")
            os.makedirs(output_dir)
        else:
            print(f"Directory {output_dir} exists.")

        csv_path = os.path.join(output_dir, f"{user_id}.csv")
        print(f"Saving ranked events to file: {csv_path}")
        ranked_df.to_csv(csv_path, index=False)

    def save_detailed_scores(self, user_id, event_scores_detailed, save_dir=None):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if save_dir is None:
            output_dir = os.path.join(current_dir, "API", "detailed_scores")
        else:
            output_dir = save_dir

        self.debug_print(f"Attempting to save detailed scores to directory: {output_dir}")

        if not os.path.exists(output_dir):
            self.debug_print(f"Directory {output_dir} does not exist, creating it.")
            os.makedirs(output_dir)
        else:
            self.debug_print(f"Directory {output_dir} exists.")

        detailed_data = []
        if self.DEBUG_MODE:
            for event_id, raw_score, final_score, breakdown in event_scores_detailed:
                if breakdown:
                    breakdown_str = "; ".join([f"{k}: {v}" for k, v in breakdown.items()])
                else:
                    breakdown_str = ""
                detailed_data.append({
                    'contentId': event_id,
                    'Raw Score': raw_score,
                    'Final Score': final_score,
                    'Breakdown': breakdown_str
                })
        else:
            for event_id, raw_score, final_score in event_scores_detailed:
                detailed_data.append({
                    'contentId': event_id,
                    'Raw Score': raw_score,
                    'Final Score': final_score,
                    'Breakdown': ""
                })

        detailed_df = pd.DataFrame(detailed_data)

        csv_path = os.path.join(output_dir, f"{user_id}_detailed_scores.csv")
        self.debug_print(f"Saving detailed scores to file: {csv_path}")
        detailed_df.to_csv(csv_path, index=False)


if __name__ == "__main__":
    ranker = EventRanking(debug_mode=True)
    events_df = pd.read_csv("API/content/17.csv")  # Replace with your test file path
    ranker.load_events(events_df)

    events_removed = ranker.filter_events()
    print(f"Removed {events_removed} invalid events")

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)

    test_user = {
        'Preferences': frozenset(['hockey', 'music', 'hiking']),
        'Disliked': frozenset(['baseball', 'film', 'lectures']),
        'Price Range': '$$',
        'Max Distance': 20
    }

    print("\nUser Preferences:")
    print(f"Preferred Events: {', '.join(sorted(test_user['Preferences']))}")
    print(f"Disliked Events: {', '.join(sorted(test_user['Disliked']))}")
    print(f"Price Range: {test_user['Price Range']}")
    print(f"Max Distance: {test_user['Max Distance']} km")
    print("\n" + "=" * 80)

    ranked_df, detailed_scores = ranker.rank_events(test_user)
    print("\nTop 10 Ranked Events:")
    print(ranked_df[['contentId', 'type', 'amount', 'distance']].head(10).to_string(index=False))

    ranker.save_ranked_events(17, ranked_df)
    ranker.save_detailed_scores(17, detailed_scores)
