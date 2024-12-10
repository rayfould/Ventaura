from fastapi.testclient import TestClient
from app import app
import pytest

client = TestClient(app)


def test_rank_events():
    """Test the rank-events endpoint with valid data"""
    print("\nStarting test_rank_events...")

    test_user = {
        "user_id": 1,
        "preferred_events": "Concerts, Sports",  # Comma-separated string
        "undesirable_events": "Festivals",  # Comma-separated string
        "location": {
            "city": "Boston",
            "coordinates": {
                "latitude": 42.3601,  # Boston's coordinates
                "longitude": -71.0589
            }
        },
        "max_distance": 10.0,
        "price_range": "$",
        "preferred_crowd_size": "Medium",
        "age": 25
    }

    test_events = [
        {
            "event_id": 1,
            "event_type": "Wellness",
            "distance": 12.54,
            "date_time": "2024-11-15 14:16:13",
            "popularity": 344,
            "price": 32.0,
        },
        {
            "event_id": 2,
            "event_type": "Wellness",
            "distance": 9.79,
            "date_time": "2024-11-24 17:16:13",
            "popularity": 654,
            "price": 75.0,
        }
    ]

    print(f"\nSending request with data:")
    print(f"User: {test_user}")
    print(f"Events: {test_events}")

    response = client.post(
        "/rank-events/",
        json={
            "user": test_user,
            "events": test_events
        }
    )

    print(f"\nResponse status code: {response.status_code}")
    # Print ranked events
    if response.status_code == 200:
        ranked_events = response.json()
        print("\nRanked Events:")
        for event in ranked_events:
            print(f"\nRank {event['rank']}:")
            print(f"  Event ID: {event['event_id']}")
            print(f"  Event Type: {event['event_type']}")
            print(f"  Distance: {event['distance']} km")
            print(f"  Date/Time: {event['date_time']}")
            print(f"  Popularity: {event['popularity']}")
            print(f"  Price: ${event['price']}")
            print(f"  Q-Value: {event['q_value']}")
    else:
        print(f"Response content: {response.json()}")

    assert response.status_code == 200
    print("\nTest passed!")


if __name__ == "__main__":
    pytest.main(["-v", __file__])  # This runs pytest with verbose output