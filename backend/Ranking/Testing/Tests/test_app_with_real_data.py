from fastapi.testclient import TestClient
from app import app
import pandas as pd
from config import *


def test_rank_events_with_real_data():
    """Test the rank-events endpoint with real CSV data"""
    client = TestClient(app)

    print("\n=== Event Ranking Test with Real Data ===")

    try:
        # Load events from CSV with explicit data types
        events_df = pd.read_csv('../data/1000_generated_events.csv', dtype={
            'Event ID': np.int32,
            'Event Type': str,
            'Distance (km)': np.float32,
            'Date/Time': str,
            'Popularity': np.int32,
            'Price ($)': np.float32
        })

        # Create test user
        test_user = {
            "user_id": 1,
            "preferred_events": "Concerts, Sports",
            "undesirable_events": "Festivals",
            "location": {
                "city": "Boston",
                "coordinates": {
                    "latitude": 42.3601,
                    "longitude": -71.0589
                }
            },
            "max_distance": 10.0,
            "price_range": "$",
            "preferred_crowd_size": "Medium",
            "age": 25
        }

        # Convert DataFrame rows to list of event dictionaries safely
        test_events = []
        for _, row in events_df.iterrows():
            try:
                event = {
                    "event_id": int(row['Event ID']),
                    "event_type": str(row['Event Type']),
                    "distance": float(row['Distance (km)']),
                    "date_time": str(row['Date/Time']),
                    "popularity": int(row['Popularity']),
                    "price": float(row['Price ($)']),
                }
                test_events.append(event)
            except Exception as e:
                print(f"Error processing event: {row}")
                print(f"Error: {str(e)}")
                continue

        print(f"\nTotal Events Loaded: {len(test_events)}")

        # Make the API request
        response = client.post(
            "/rank-events/",
            json={
                "user": test_user,
                "events": test_events
            }
        )

        print(f"\nResponse Status Code: {response.status_code}")

        if response.status_code == 200:
            ranked_events = response.json()
            print(f"\nRanked Events (Total: {len(ranked_events)}):")

            # Save rankings to CSV first
            rankings_df = pd.DataFrame(ranked_events)
            rankings_df.to_csv('ranked_events_output.csv', index=False)
            print("\nFull rankings saved to 'ranked_events_output.csv'")

            # Then display them
            for event in ranked_events:
                print(f"\nRank {event['rank']}:")
                print(f"    Event ID: {event['event_id']}")
                print(f"    Type: {event['event_type']}")
                print(f"    Distance: {event['distance']} km")
                print(f"    Date/Time: {event['date_time']}")
                print(f"    Popularity: {event['popularity']}")
                print(f"    Price: ${event['price']}")
                print(f"    Q-Value: {event['q_value']}")
        else:
            print("Error Response:", response.json())

        assert response.status_code == 200
        print("\nTest completed successfully!")

    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        raise


if __name__ == "__main__":
    test_rank_events_with_real_data()
