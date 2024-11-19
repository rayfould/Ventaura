import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Define event types with realistic price ranges per type
event_types_and_prices = {
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

# Generate random data for 100 events
event_data = {
    "Event ID": list(range(1, 101)),


    "Event Type": [random.choice(list(event_types_and_prices.keys())) for _ in range(100)],
# Most events within 0-20km, some up to 100 km
    "Distance (km)": [round(random.uniform(0, 20), 2) if random.random() > 0.1
                      else round(random.uniform(20, 100), 2) for _ in range(100)],


    # Majority in 1-15 days, some far-out events
    "Date/Time": [(datetime.now() + timedelta(days=random.randint(1, 15), hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S')
                  if random.random() > 0.2
                  else (datetime.now() + timedelta(days=random.randint(16, 60), hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S')
                  if random.random() > 0.05
                  else (datetime.now() - timedelta(days=random.randint(1, 5), hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S')
                  for _ in range(100)],


    # More common events around 300, fewer highly popular events
    "Popularity": [max(0, round(random.gauss(500, 300))) if random.random() > 0.2
                   else round(random.uniform(500, 1000)) for _ in range(100)],

    "Price ($)": [],


    # Majority shorter events, few long ones
    "Duration (hrs)": [round(random.uniform(0.5, 6), 2) if random.random() > 0.2 else round(random.uniform(6, 12), 2) for _ in range(100)]
}

# Adjust Price per Event Type
for i in range(100):
    event_type = event_data["Event Type"][i]
    price_range = event_types_and_prices[event_type]
    event_data["Price ($)"].append(round(random.uniform(*price_range)))  # Generate price within the event type's realistic range

# Convert duration to the nearest quarter hour
event_data["Duration (hrs)"] = [round(duration * 4) / 4 for duration in event_data["Duration (hrs)"]]

# Create DataFrame
events_df = pd.DataFrame(event_data)

# Save to CSV in the current directory
current_directory = os.getcwd()  # Get current directory
csv_file_path = os.path.join(current_directory, "100_generated_events.csv")  # Set full path with filename

# Save the dataframe to the file
events_df.to_csv(csv_file_path, index=False)

# Output the file path for confirmation
print(f"CSV file saved at: {csv_file_path}")
