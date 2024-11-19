import pandas as pd
import random
from datetime import datetime, timedelta
import os

# Define event types with realistic price ranges per type
event_types_and_prices = {
    "Music": (20, 250),
    "Festivals": (50, 300),
    "Sports": (30, 350),
    "Outdoors": (0, 200),
    "Workshops": (10, 150),
    "Conferences": (100, 700),
    "Exhibitions": (0, 200),
    "Community": (0, 40),
    "Theater": (30, 250),
    "Family": (0, 180),
    "Nightlife": (10, 200),
    "Wellness": (10, 180),
    "Holiday": (0, 200),
    "Networking": (10, 350),
    "Gaming": (10, 160),
    "Film": (5, 80),
    "Pets": (0, 150),
    "Virtual": (0, 150),
    "Charity": (0, 150),
    "Science": (20, 200)
}

# Generate random data for 100 events
event_data = {
    "Event ID": list(range(1, 10001)),


    "Event Type": [random.choice(list(event_types_and_prices.keys())) for _ in range(10000)],
# Most events within 0-20km, some up to 100 km
    "Distance (km)": [round(random.uniform(0, 20), 2) if random.random() > 0.1
                      else round(random.uniform(20, 300), 2) for _ in range(10000)],


    # Majority in 1-15 days, some far-out events
    "Date/Time": [(datetime.now() + timedelta(days=random.randint(1, 15), hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S')
                  if random.random() > 0.2
                  else (datetime.now() + timedelta(days=random.randint(16, 60), hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S')
                  if random.random() > 0.05
                  else (datetime.now() - timedelta(days=random.randint(1, 5), hours=random.randint(0, 23))).strftime('%Y-%m-%d %H:%M:%S')
                  for _ in range(10000)],


    # More common events around 300, fewer highly popular events
    "Popularity": [round(random.gauss(500, 300)) if random.random() > 0.2
                   else round(random.uniform(500, 4000)) for _ in range(10000)],


    "Price ($)": [],


    # Majority shorter events, few long ones
    "Duration (hrs)": [round(random.uniform(0.5, 6), 2) if random.random() > 0.2
                       else round(random.uniform(6, 32), 2) for _ in range(10000)]
}

# Adjust Price per Event Type
for i in range(10000):
    event_type = event_data["Event Type"][i]
    price_range = event_types_and_prices[event_type]
    event_data["Price ($)"].append(round(random.uniform(*price_range)))  # Generate price within the event type's realistic range

# Convert duration to the nearest quarter hour
event_data["Duration (hrs)"] = [round(duration * 4) / 4 for duration in event_data["Duration (hrs)"]]

# Create DataFrame
events_df = pd.DataFrame(event_data)

# Save to CSV in the current directory
current_directory = os.getcwd()  # Get current directory
csv_file_path = os.path.join(current_directory, "10000_generated_events.csv")  # Set full path with filename

# Save the dataframe to the file
events_df.to_csv(csv_file_path, index=False)

# Output the file path for confirmation
print(f"CSV file saved at: {csv_file_path}")
