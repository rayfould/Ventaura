import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os


class MockEventDataGenerator:
    def __init__(self):
        # Simplified event types with price ranges
        self.event_types_and_prices = {
            "Music": (20, 150),
            "Festivals": (50, 200),
            "Sports": (30, 250),
            "Outdoors": (0, 100),
            "Workshops": (10, 50),
            "Conferences": (100, 500),
            "Exhibitions": (0, 100),
            "Community": (0, 20),
            "Theater": (30, 150),
            "Family": (0, 80),
            "Nightlife": (10, 100),
            "Wellness": (10, 80),
            "Holiday": (0, 100),
            "Networking": (10, 150),
            "Gaming": (10, 60),
            "Film": (5, 40),
            "Pets": (0, 50),
            "Virtual": (0, 50),
            "Charity": (0, 50),
            "Science": (20, 100)
        }

        # Time slots with adjusted probabilities
        self.time_slots = {
            "Morning": {"start": 8, "end": 12, "weight": 0.1},
            "Afternoon": {"start": 12, "end": 17, "weight": 0.35},
            "Evening": {"start": 17, "end": 22, "weight": 0.4},
            "Night": {"start": 22, "end": 23, "weight": 0.15}
        }

        # Weighted days ahead for realistic scheduling
        self.days_ahead_weights = [
            (1, 3, 0.5),   # 50% of events occur within 1–3 days
            (4, 14, 0.3),  # 30% occur within 4–14 days
            (15, 30, 0.15),  # 15% occur within 15–30 days
            (31, 60, 0.05)  # 5% occur within 31–60 days
        ]

    def _generate_days_ahead(self):
        """Generate days ahead based on weighted probabilities."""
        days_range, weight = zip(
            *[(range(low, high + 1), w) for low, high, w in self.days_ahead_weights]
        )
        days_choice = np.random.choice(
            [random.choice(rng) for rng in days_range],
            p=weight
        )
        return int(days_choice)  # Convert numpy.int64 to native Python int

    def _generate_datetime(self):
        """Generate realistic datetime with weighted time slots."""
        days_ahead = self._generate_days_ahead()
        base_date = datetime.now() + timedelta(days=days_ahead)

        # Choose a time slot based on weight
        time_slot = random.choices(
            list(self.time_slots.keys()),
            weights=[slot["weight"] for slot in self.time_slots.values()]
        )[0]

        slot = self.time_slots[time_slot]
        hour = random.randint(slot["start"], slot["end"])
        minute = random.choice([0, 15, 30, 45])

        return base_date.replace(hour=hour, minute=minute)

    def _generate_event(self, event_id):
        """Generate a single event with fields matching the API structure."""
        # Select event type
        event_type, price_range = random.choice(list(self.event_types_and_prices.items()))

        # Generate datetime
        event_datetime = self._generate_datetime()

        # Generate mock event data
        return {
            "contentId": event_id,
            "title": event_type,  # Using event type as title
            "description": "",  # Empty since description is not used
            "location": f"{round(random.uniform(-90, 90), 6)}, {round(random.uniform(-180, 180), 6)}",
            "start": event_datetime.isoformat() + "Z",
            "source": "MockSource",  # Placeholder
            "type": event_type,  # Event type
            "currencyCode": "USD",
            "amount": round(random.uniform(*price_range), 2),
            "url": "https://placeholder.url",  # Placeholder
            "distance": round(random.uniform(0, 100), 2)  # Generating realistic distances
        }

    def generate_mock_events(self, num_events=1000):
        """Generate specified number of mock events."""
        events = [self._generate_event(event_id) for event_id in range(1, num_events + 1)]
        return pd.DataFrame(events)

    def save_mock_events(self, df, filename="mock_events.csv"):
        """Save generated mock events to CSV file."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_file_path = os.path.join(current_dir, filename)
        df.to_csv(csv_file_path, index=False)
        print(f"Mock data saved to: {csv_file_path}")
        return csv_file_path


def main(num_files=1):  # Default to 5 files, but can be changed
    # Create the content directory if it doesn't exist

    generator = MockEventDataGenerator()
    used_ids = set()

    for i in range(num_files):
        # Generate unique user ID
        while True:
            user_id = random.randint(0, 100)
            if user_id not in used_ids:
                used_ids.add(user_id)
                break

        # Generate mock events
        mock_events_df = generator.generate_mock_events(1000)

        # Save with the new naming convention
        filename = f"{user_id}.csv"
        generator.save_mock_events(mock_events_df, filename)

        print(f"[{i + 1}/{num_files}] Generated mock events for user {user_id}")

    print(f"\nGenerated {num_files} files with user IDs: {sorted(list(used_ids))}")


if __name__ == "__main__":
    main(1)  # This will generate 10 files
