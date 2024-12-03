import pandas as pd
import random
from datetime import datetime, timedelta
import os


class MockUserDataGenerator:
    def __init__(self):
        # Define all event types
        self.event_types = [
            "Music", "Festivals", "Sports", "Outdoors", "Workshops",
            "Conferences", "Exhibitions", "Community", "Theater",
            "Family", "Nightlife", "Wellness", "Holiday", "Networking",
            "Gaming", "Film", "Pets", "Virtual", "Charity", "Science"
        ]
        # Define price ranges
        self.price_ranges = ["$", "$$", "$$$"]
        # Add distance preferences
        self.distance_ranges = {
            "Very Local": (0, 5),  # Walking distance
            "Local": (2, 10),  # Short drive
            "Nearby": (5, 20),  # Medium drive
            "City-wide": (10, 30),  # Longer drive
            "Regional": (20, 100),  # Day trip
            "Any Distance": (0, 200)  # More realistic max distance
        }

    def _generate_random_email(self, first_name, last_name):
        """Generate a random email based on first and last name."""
        domains = ["example.com", "mock.com", "test.com"]
        return f"{first_name.lower()}.{last_name.lower()}@{random.choice(domains)}"

    def _generate_random_coordinates(self):
        """Generate random latitude and longitude within realistic bounds."""
        latitude = round(random.uniform(-90, 90), 6)
        longitude = round(random.uniform(-180, 180), 6)
        return latitude, longitude

    def _generate_created_at(self):
        """Generate a random account creation date within the past year."""
        days_ago = random.randint(0, 365)
        created_at = datetime.now() - timedelta(days=days_ago)
        return created_at.isoformat() + "Z"

    def _generate_user(self, user_id):
        """Generate a single user with required fields."""
        first_name = random.choice(["Jane", "John", "Alice", "Bob", "Eve", "Charlie", "Grace", "Mallory"])
        last_name = random.choice(["Doe", "Smith", "Brown", "Taylor", "Wilson", "Johnson", "Davis", "Moore"])
        email = self._generate_random_email(first_name, last_name)
        latitude, longitude = self._generate_random_coordinates()

        # Generate preferences and disliked event types
        preferences = random.sample(self.event_types, random.randint(1, 5))
        disliked = random.sample([et for et in self.event_types if et not in preferences], random.randint(1, 3))

        price_range = random.choice(self.price_ranges)
        distance = random.choice(list(self.distance_ranges.keys()))
        created_at = self._generate_created_at()

        return {
            "userId": user_id,
            "email": email,
            "firstName": first_name,
            "lastName": last_name,
            "latitude": latitude,
            "longitude": longitude,
            "preferences": ", ".join(preferences),
            "disliked": ", ".join(disliked),
            "priceRange": price_range,
            "distance": distance,
            "createdAt": created_at
        }

    def generate_mock_users(self, num_users=100):
        """Generate specified number of mock users."""
        users = [self._generate_user(user_id) for user_id in range(1, num_users + 1)]
        return pd.DataFrame(users)

    def save_mock_users(self, df, filename="mock_users.csv"):
        """Save generated mock users to a CSV file."""
        current_directory = os.getcwd()
        csv_file_path = os.path.join(current_directory, filename)
        df.to_csv(csv_file_path, index=False)
        print(f"Mock user data saved to: {csv_file_path}")
        return csv_file_path


def main():
    generator = MockUserDataGenerator()
    mock_users_df = generator.generate_mock_users(100)
    generator.save_mock_users(mock_users_df, "diverse_users.csv")


if __name__ == "__main__":
    main()
