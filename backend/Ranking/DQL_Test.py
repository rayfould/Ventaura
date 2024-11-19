"""
DQL_Testing.py
Comprehensive testing module for the DQL event recommendation system.
"""

import torch
import pandas as pd
import numpy as np
from Event_Ranking_Environment import EventRecommendationEnv
from config import *
from DQL import QNetwork
import logging

class EventTester:
    def __init__(self, model_path, events_df, user):
        """Initialize the tester with events and user data."""
        # Convert Date/Time to timestamp
        events_df = events_df.copy()
        events_df['Date/Time'] = pd.to_datetime(events_df['Date/Time'])
        events_df['timestamp'] = events_df['Date/Time'].astype(np.int64) // 10 ** 9

        self.events_df = events_df
        self.user = user
        self.env = EventRecommendationEnv(events_df, user)

        # Initialize Q-network with correct dimensions
        self.q_network = QNetwork(state_size=5, action_size=len(events_df))
        self.q_network.load_state_dict(torch.load(model_path, weights_only=True))
        self.q_network.eval()

    def display_recommendations(self, recommendations):
        """Display recommendations in a formatted table."""
        info_print("\nTop Recommended Events:")
        info_print("=" * 120)
        info_print(f"{'Rank':<6}{'Event ID':<10}{'Category':<15}{'Event Type':<20}"
                   f"{'Hours Until':<15}{'Price':<12}{'Distance':<15}{'Popularity':<10}")
        info_print("=" * 120)

        current_time = get_current_time()

        for rec in recommendations:
            try:
                # Calculate hours until event
                event_time = pd.to_datetime(rec['Date/Time'])
                if event_time.tz is None:
                    event_time = event_time.tz_localize('UTC')

                time_diff = event_time - current_time
                hours_until = time_diff.total_seconds() / 3600
                hours_str = f"{hours_until:.1f} hrs"

                # Format other values
                price = f"${float(rec['Price ($)']):.2f}"
                distance = f"{float(rec['Distance (km)']):.2f}"
                popularity = f"{int(float(rec['Popularity']))}"

                info_print(f"{rec['Rank']:<6}"
                           f"{rec['Event ID']:<10}"
                           f"{rec['Category']:<15}"
                           f"{rec['Event Type']:<20}"
                           f"{hours_str:<15}"
                           f"{price:<12}"
                           f"{distance:<15}"
                           f"{popularity:<10}")

            except Exception as e:
                logging.error(f"Error formatting recommendation: {str(e)}")
                continue

        info_print("\nDetailed Recommendations:")
        for rec in recommendations:
            try:
                info_print(f"\nRank {rec['Rank']} (Q-Value: {rec['Q-Value']})")

                # Calculate hours until event for detailed view
                event_time = pd.to_datetime(rec['Date/Time'])
                if event_time.tz is None:
                    event_time = event_time.tz_localize('UTC')

                time_diff = event_time - current_time
                hours_until = time_diff.total_seconds() / 3600

                info_print(f"Event ID: {rec['Event ID']}")
                info_print(f"Category: {rec['Category']}")
                info_print(f"Event Type: {rec['Event Type']}")
                info_print(f"Date/Time: {event_time.strftime('%Y-%m-%d %H:%M')}")
                info_print(f"Hours Until Event: {hours_until:.1f}")
                info_print(f"Price: ${float(rec['Price ($)']):.2f}")
                info_print(f"Distance: {float(rec['Distance (km)']):.2f} km")
                info_print(f"Popularity: {int(float(rec['Popularity']))}")

                # Add categories
                price = float(rec['Price ($)'])
                price_category = next((k for k, v in PRICE_RANGES.items()
                                       if v['min'] <= price <= v['max']), 'Above $$$')
                info_print(f"Price Category: {price_category}")

                popularity = float(rec['Popularity'])
                popularity_category = next((k for k, v in POPULARITY_RANGES.items()
                                            if v['min'] <= popularity <= v['max']), 'Very Large')
                info_print(f"Popularity Category: {popularity_category}")

            except Exception as e:
                logging.error(f"Error displaying detailed recommendation: {str(e)}")
                continue

    def get_top_recommendations(self, num_recommendations=10):
        """Get top N recommendations with their Q-values."""
        try:
            state = self.env.reset()
            state_tensor = torch.FloatTensor(state).unsqueeze(0)

            with torch.no_grad():
                q_values = self.q_network(state_tensor).squeeze()

            # Get top K actions
            top_actions = torch.topk(q_values, k=num_recommendations)
            top_indices = top_actions.indices.tolist()
            top_values = top_actions.values.tolist()

            recommendations = []
            for rank, (idx, q_val) in enumerate(zip(top_indices, top_values), 1):
                event = self.events_df.iloc[idx]
                recommendations.append({
                    'Rank': rank,
                    'Event ID': event['Event ID'],
                    'Event Type': event['Event Type'],
                    'Date/Time': event['Date/Time'],
                    'Price ($)': event['Price ($)'],
                    'Distance (km)': event['Distance (km)'],
                    'Popularity': event['Popularity'],
                    'Q-Value': f"{q_val:.3f}"
                })

            return recommendations

        except Exception as e:
            logging.error(f"Error getting recommendations: {str(e)}")
            raise

def main():
    # Load data
    events_df = pd.read_csv("Testing/data/1000_generated_events.csv")
    users = pd.read_csv('Testing/data/diverse_users.csv')
    user = users.iloc[2]

    # Initialize tester
    tester = EventTester(
        model_path='Training/models/Model_11/recommender/final_model_20241114_195704.pth',
        events_df=events_df,
        user=user
    )

    # Get and display recommendations
    recommendations = tester.get_top_recommendations(num_recommendations=10)
    tester.display_recommendations(recommendations)

if __name__ == "__main__":
    main()
