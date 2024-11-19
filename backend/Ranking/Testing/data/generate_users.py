import pandas as pd

# Define our actual event categories from the dataset
EVENT_CATEGORIES = [
    'Film', 'Science', 'Exhibitions', 'Theater', 'Networking', 'Gaming',
    'Pets', 'Music', 'Sports', 'Nightlife', 'Virtual', 'Charity',
    'Festivals', 'Workshops', 'Family', 'Holiday', 'Wellness',
    'Community', 'Outdoors', 'Conferences'
]

# First define all the basic user data
base_data = {
    "Preferred Location": [
        "Boston", "New York", "San Francisco", "Chicago", "Los Angeles",
        "Austin", "Seattle", "Miami", "Denver", "Portland",
        "Nashville", "San Diego", "Houston", "Atlanta", "Philadelphia",
        "Phoenix", "Minneapolis", "New Orleans", "Salt Lake City", "Washington DC"
    ],
    "Max Distance (km)": [
        15, 25, 40, 20, 30,
        50, 35, 25, 45, 30,
        20, 40, 35, 25, 50,
        30, 40, 45, 25, 35
    ],
    "Preferred Time": [
        "Evening", "Mixed", "Night", "Morning", "Afternoon",
        "Evening", "Morning", "Night", "Mixed", "Evening",
        "Morning", "Afternoon", "Evening", "Mixed", "Night",
        "Morning", "Evening", "Night", "Mixed", "Evening"
    ],
    "Price Range": [
        "$$$", "$$", "$", "$$", "$$$",
        "$$", "$$$", "$", "$$", "$",
        "$$$", "$$", "$", "$$$", "$$",
        "$", "$$$", "$$", "$", "$$$"
    ],
    "Preferred Crowd Size": [
        "Large", "Small", "Medium", "Large", "Small",
        "Medium", "Large", "Small", "Medium", "Large",
        "Small", "Medium", "Large", "Small", "Medium",
        "Large", "Small", "Medium", "Large", "Small"
    ],
    "Age": [
        25, 32, 19, 45, 28,
        23, 41, 35, 29, 38,
        52, 33, 26, 47, 21,
        39, 24, 31, 44, 36
    ],
    "Interests": [
        "Music, Technology", "Arts, Culture", "Gaming, Tech", "Fitness, Outdoors",
        "Food, Culture", "Arts, Music", "Business, Tech", "Health, Wellness",
        "Community, Food", "Film, Arts", "Science, Education", "Family, Education",
        "Adventure, Sports", "Music, Arts", "Dance, Social", "Community, Health",
        "Gaming, Pop Culture", "Sports, Social", "Arts, Photography", "Culture, Language"
    ],
    "Activity Level": [
        "High", "Medium", "High", "Very High", "Medium",
        "High", "Medium", "Low", "Medium", "Low",
        "Medium", "High", "Very High", "Low", "High",
        "Medium", "High", "Medium", "Low", "Medium"
    ]
}

# Now create the complete users_data dictionary
users_data = {
    "User ID": range(1, 21),
    "Preferred Events": [
        "Music, Festivals, Theater",  # Music & Entertainment focus
        "Theater, Exhibitions, Community",  # Cultural focus
        "Gaming, Virtual, Workshops",  # Gaming/Tech focus
        "Sports, Outdoors, Wellness",  # Sports/Fitness focus
        "Festivals, Community, Workshops",  # Food/Drink focus
        "Music, Exhibitions, Theater",  # Alternative/Arts focus
        "Networking, Conferences, Workshops",  # Professional focus
        "Wellness, Workshops, Community",  # Wellness focus
        "Community, Festivals, Family",  # Community focus
        "Film, Theater, Exhibitions",  # Film/Arts focus
        "Science, Exhibitions, Workshops",  # Educational focus
        "Family, Theater, Community",  # Family focus
        "Outdoors, Sports, Community",  # Adventure focus
        "Music, Theater, Exhibitions",  # Refined Music focus
        "Nightlife, Music, Festivals",  # Nightlife focus
        "Charity, Community, Wellness",  # Social Impact focus
        "Gaming, Virtual, Festivals",  # Gaming/Pop Culture focus
        "Sports, Community, Festivals",  # Sports Entertainment focus
        "Exhibitions, Workshops, Community",  # Creative focus
        "Festivals, Community, Exhibitions"  # Cultural/International focus
    ],
    "Undesirable Events": [
        "Conferences, Networking, Virtual",  # Opposite of entertainment
        "Sports, Gaming, Nightlife",  # Opposite of cultural
        "Theater, Conferences, Exhibitions",  # Opposite of gaming/tech
        "Gaming, Nightlife, Virtual",  # Opposite of sports/fitness
        "Sports, Gaming, Networking",  # Opposite of food/drink
        "Networking, Conferences, Virtual",  # Opposite of alternative/arts
        "Nightlife, Gaming, Festivals",  # Opposite of professional
        "Sports, Nightlife, Gaming",  # Opposite of wellness
        "Nightlife, Gaming, Conferences",  # Opposite of community
        "Sports, Nightlife, Gaming",  # Opposite of film/arts
        "Nightlife, Gaming, Festivals",  # Opposite of educational
        "Nightlife, Conferences, Gaming",  # Opposite of family
        "Conferences, Virtual, Networking",  # Opposite of adventure
        "Gaming, Sports, Nightlife",  # Opposite of refined music
        "Conferences, Virtual, Science",  # Opposite of nightlife
        "Nightlife, Gaming, Virtual",  # Opposite of social impact
        "Conferences, Networking, Science",  # Opposite of gaming/pop culture
        "Exhibitions, Science, Virtual",  # Opposite of sports entertainment
        "Sports, Gaming, Nightlife",  # Opposite of creative
        "Gaming, Virtual, Networking"  # Opposite of cultural/international
    ]
}

# Add all the base data to users_data
users_data.update(base_data)

# Convert to DataFrame and save
users_df = pd.DataFrame(users_data)
users_df.to_csv("diverse_users.csv", index=False)

print("Users data generated successfully!")