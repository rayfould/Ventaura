import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os


class EventDataGenerator:
    def __init__(self):
        # Enhanced event types with categories, subcategories, and realistic price ranges
        self.event_categories = {
            "Music": {
                "Concert": (30, 200),
                "Festival": (50, 300),
                "Live Band": (15, 100),
                "DJ Set": (20, 80),
                "Orchestra": (40, 250)
            },
            "Sports": {
                "Professional Game": (50, 300),
                "Amateur Match": (10, 50),
                "Tournament": (30, 150),
                "Marathon": (25, 100),
                "Training Session": (15, 80)
            },
            "Arts & Culture": {
                "Exhibition": (0, 50),
                "Theater": (30, 150),
                "Museum": (10, 50),
                "Gallery Opening": (0, 30),
                "Performance": (25, 120)
            },
            "Professional": {
                "Conference": (100, 1000),
                "Workshop": (50, 300),
                "Networking": (10, 100),
                "Seminar": (30, 200),
                "Training": (80, 400)
            },
            "Community": {
                "Festival": (0, 50),
                "Market": (0, 20),
                "Fundraiser": (10, 100),
                "Meeting": (0, 30),
                "Local Event": (0, 40)
            }
        }

        # Time slots with weighted probabilities
        self.time_slots = {
            "Morning": {"start": 8, "end": 12, "weight": 0.2},
            "Afternoon": {"start": 12, "end": 17, "weight": 0.3},
            "Evening": {"start": 17, "end": 22, "weight": 0.4},
            "Night": {"start": 22, "end": 23, "weight": 0.1}
        }

        # Popularity factors
        self.popularity_factors = {
            "base_popularity": {
                "Music": (300, 1000),
                "Sports": (200, 800),
                "Arts & Culture": (100, 600),
                "Professional": (50, 400),
                "Community": (50, 300)
            },
            "time_multipliers": {
                "Weekend": 1.5,
                "Evening": 1.3,
                "Holiday": 2.0
            }
        }

    def _generate_datetime(self):
        """Generate realistic datetime with weighted time slots."""
        # Base date within next 60 days
        days_ahead = int(np.random.choice(  # Convert to int
            [random.randint(1, 14),  # Next 2 weeks (higher probability)
             random.randint(15, 30),  # Next month
             random.randint(31, 60)],  # Further ahead
            p=[0.85, 0.1, 0.05]
        ))

        base_date = datetime.now() + timedelta(days=days_ahead)

        # Select time slot based on weights
        time_slot = random.choices(
            list(self.time_slots.keys()),
            weights=[slot["weight"] for slot in self.time_slots.values()]
        )[0]

        slot = self.time_slots[time_slot]
        hour = random.randint(slot["start"], slot["end"])
        minute = random.choice([0, 15, 30, 45])  # Quarter-hour intervals

        return base_date.replace(hour=hour, minute=minute)

    def _calculate_popularity(self, category, event_type, datetime):
        """Calculate realistic popularity based on multiple factors."""
        base_range = self.popularity_factors["base_popularity"][category]
        base_popularity = random.randint(*base_range)

        multiplier = 1.0
        # Weekend bonus
        if datetime.weekday() >= 5:
            multiplier *= self.popularity_factors["time_multipliers"]["Weekend"]

        # Evening bonus
        if 17 <= datetime.hour <= 22:
            multiplier *= self.popularity_factors["time_multipliers"]["Evening"]

        # Holiday bonus (simplified)
        if random.random() < 0.1:  # 10% chance of being a holiday
            multiplier *= self.popularity_factors["time_multipliers"]["Holiday"]

        return int(base_popularity * multiplier)

    def _generate_duration(self, category, event_type):
        """Generate realistic duration based on event type."""
        if category == "Music":
            return round(random.uniform(2, 4), 2)
        elif category == "Sports":
            return round(random.uniform(2, 3), 2)
        elif category == "Professional":
            return round(random.uniform(4, 8), 2)
        elif category == "Arts & Culture":
            return round(random.uniform(1, 3), 2)
        else:
            return round(random.uniform(2, 5), 2)

    def generate_events(self, num_events=1000):
        """Generate specified number of events with realistic attributes."""
        events_data = []

        for event_id in range(1, num_events + 1):
            # Select category and event type
            category = random.choice(list(self.event_categories.keys()))
            event_type = random.choice(list(self.event_categories[category].keys()))
            price_range = self.event_categories[category][event_type]

            # Generate datetime
            event_datetime = self._generate_datetime()

            # Generate other attributes
            event = {
                "Event ID": event_id,
                "Category": category,
                "Event Type": event_type,
                "Date/Time": event_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                "Price ($)": round(random.uniform(*price_range)),
                "Distance (km)": round(random.uniform(0, 20), 2) if random.random() > 0.1
                else round(random.uniform(20, 100), 2),
                "Duration (hrs)": self._generate_duration(category, event_type),
                "Popularity": self._calculate_popularity(category, event_type, event_datetime)
            }

            events_data.append(event)

        return pd.DataFrame(events_data)

    def save_events(self, df, filename="generated_events.csv"):
        """Save generated events to CSV file."""
        current_directory = os.getcwd()
        csv_file_path = os.path.join(current_directory, filename)
        df.to_csv(csv_file_path, index=False)
        print(f"CSV file saved at: {csv_file_path}")
        return csv_file_path


def main():
    generator = EventDataGenerator()
    events_df = generator.generate_events(1000)
    generator.save_events(events_df, "1000_generated_events.csv")


if __name__ == "__main__":
    main()
