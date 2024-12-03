from scipy.cluster.hierarchy import weighted

from config import *

class EventRecommendationEnv:
    """
    Environment for event recommendation reinforcement learning.

    Attributes:
        events (pd.DataFrame): Event data
        user (pd.Series): User preferences
        current_event_index (int): Current position in event list
        done (bool): Episode completion status
        max_events (int): Total number of available events
    """
    def __init__(self, events_df, user, analytics=None):
        debug_print(f"Initializing EventRecommendationEnv with {len(events_df)} events")
        self.events = events_df.reset_index(drop=True)  # DataFrame containing the event data
        self.user = user  # User preferences (from users.csv)
        self.current_event_index = 0  # Track which event we are recommending
        self.done = False  # Whether the episode is over
        self.max_events = len(events_df)  # Total number of events available
        self.analytics = analytics
        debug_print(f"Analytics object initialized: {self.analytics is not None}")

        # Convert 'Date/Time' to timestamp for filtering
        current_time = get_timestamp()
        if 'timestamp' not in events_df.columns:
            self.events['timestamp'] = pd.to_datetime(events_df['Date/Time'])


        # Filter out past events at initialization
        current_time = get_timestamp()
        self.valid_events = events_df[events_df['timestamp'] > current_time].copy()
        self.max_events = len(self.valid_events)

        # Assign max distance from the user preferences
        self.max_distance = self.user['Max Distance (km)']  # Ensure user has this field

        self.action_space = self.max_events
        self.observation_space = 5

        # Precompute statistics and process user preferences
        self.precompute_statistics()
        self.process_user_preferences()


        debug_print("\nUser Data Debug:")
        debug_print(f"Raw preferred events: {user['Preferred Events']}")
        debug_print(f"Raw undesirable events: {user['Undesirable Events']}")

        # Since the data is already a list, we just need to clean it
        if isinstance(user['Preferred Events'], list):
            self.user_preferred_events = [e.strip() for e in user['Preferred Events']]
        else:
            self.user_preferred_events = [e.strip() for e in user['Preferred Events'].split(',')]

        if isinstance(user['Undesirable Events'], list):
            self.user_undesirable_events = [e.strip() for e in user['Undesirable Events']]
        else:
            self.user_undesirable_events = [e.strip() for e in user['Undesirable Events'].split(',')]

        debug_print("\nProcessed User Preferences:")
        debug_print(f"Preferred events list: {self.user_preferred_events}")
        debug_print(f"Undesirable events list: {self.user_undesirable_events}")

        # Convert to sets for efficient lookup
        self.preferred_set = {e.lower() for e in self.user_preferred_events}
        self.undesirable_set = {e.lower() for e in self.user_undesirable_events}

        debug_print("Processed preferences:")
        debug_print(f"Preferred events: {self.preferred_set}")
        debug_print(f"Undesirable events: {self.undesirable_set}")


    def filter_invalid_events(self, events):
        """Remove past events from consideration."""
        current_time = get_current_time()
        valid_events = events[events['timestamp'] > current_time].copy()
        debug_print(f"Filtered {len(events) - len(valid_events)} past events")
        return valid_events

    def precompute_statistics(self):
        """Precompute statistics for normalization and scoring."""
        # Ensure 'Date/Time' is in datetime format and handle errors (coerce invalid dates)
        self.events['Date/Time'] = pd.to_datetime(self.events['Date/Time'], errors='coerce')

        # Handle any NaT values by setting a fallback (e.g., maximum date in the future)
        fallback_time = pd.Timestamp.max
        self.events['Date/Time'] = self.events['Date/Time'].fillna(fallback_time)

        # Make event times timezone-aware if they aren't already
        if self.events['Date/Time'].dt.tz is None:
            self.events['Date/Time'] = self.events['Date/Time'].dt.tz_localize('UTC')

        self.current_time = get_current_time()

        # Compute 'Time Until Event' in hours
        self.events['Time Until Event (hrs)'] = (self.events['Date/Time'] - self.current_time).dt.total_seconds() / 3600.0

        # Calculate the maximum time difference for scoring purposes
        self.max_time_difference = self.events['Time Until Event (hrs)'].max()

        # Calculate max popularity for use in scoring popularity
        self.max_popularity = self.events['Popularity'].max()

        # Precompute cached statistics for each event type
        self.event_type_stats_cache = {}
        for event_type in self.events['Event Type'].unique():
            if pd.notna(event_type):
                event_data = self.events[self.events['Event Type'] == event_type]

                # Cache stats for price, distance, popularity, and time until event
                self.event_type_stats_cache[event_type] = {
                    'price_stats': {
                        'mean': event_data['Price ($)'].mean(),
                        'min': event_data['Price ($)'].min(),
                        'max': event_data['Price ($)'].max(),
                        'std': event_data['Price ($)'].std() or 1e-5
                    },
                    'distance_stats': {
                        'mean': event_data['Distance (km)'].mean(),
                        'min': event_data['Distance (km)'].min(),
                        'max': event_data['Distance (km)'].max(),
                        'std': event_data['Distance (km)'].std() or 1e-5
                    },
                    'popularity_stats': {
                        'mean': event_data['Popularity'].mean(),
                        'min': event_data['Popularity'].min(),
                        'max': event_data['Popularity'].max(),
                        'std': event_data['Popularity'].std() or 1e-5
                    },
                    'time_stats': {
                        'mean': event_data['Time Until Event (hrs)'].mean(),
                        'min': event_data['Time Until Event (hrs)'].min(),
                        'max': event_data['Time Until Event (hrs)'].max(),
                        'std': event_data['Time Until Event (hrs)'].std() or 1e-5
                    }
                }

        # Global fallback stats
        self.global_stats = {
            'price_stats': {
                'mean': self.events['Price ($)'].mean(),
                'min': self.events['Price ($)'].min(),
                'max': self.events['Price ($)'].max(),
                'std': self.events['Price ($)'].std() or 1e-5
            },
            'distance_stats': {
                'mean': self.events['Distance (km)'].mean(),
                'min': self.events['Distance (km)'].min(),
                'max': self.events['Distance (km)'].max(),
                'std': self.events['Distance (km)'].std() or 1e-5
            },
            'popularity_stats': {
                'mean': self.events['Popularity'].mean(),
                'min': self.events['Popularity'].min(),
                'max': self.events['Popularity'].max(),
                'std': self.events['Popularity'].std() or 1e-5
            },
            'time_stats': {
                'mean': self.events['Time Until Event (hrs)'].mean(),
                'min': self.events['Time Until Event (hrs)'].min(),
                'max': self.events['Time Until Event (hrs)'].max(),
                'std': self.events['Time Until Event (hrs)'].std() or 1e-5
            }
        }

    def process_user_preferences(self):
        """Process and store user preferences for efficient access."""
        # Clean and process preferred events
        preferred_raw = str(self.user['Preferred Events'])
        preferred_events = [
            event.strip().lower().strip("'[]")  # Remove brackets and quotes but NOT plural/singular
            for event in preferred_raw.split(',')
        ]
        self.user_preferred_events = set(preferred_events)

        # Clean and process undesirable events
        undesirable_raw = str(self.user['Undesirable Events'])
        undesirable_events = [
            event.strip().lower().strip("'[]")  # Remove brackets and quotes but NOT plural/singular
            for event in undesirable_raw.split(',')
        ]
        self.user_undesirable_events = set(undesirable_events)

        self.preferred_crowd_size = self.user['Preferred Crowd Size']

        # Debug print
        debug_print(f"Processed preferences:")
        debug_print(f"Preferred events: {self.user_preferred_events}")
        debug_print(f"Undesirable events: {self.user_undesirable_events}")

    def reset(self):
        """Reset the environment and return the first event's features."""
        self.current_event_index = 0
        self.done = False
        return self.get_event_features(self.current_event_index)

    def step(self, action):
        """Take an action (recommend an event) and return the next state, reward, and done flag."""
        if action >= len(self.events):
            self.done = True
            return np.zeros(self.observation_space), -1, True

        event = self.events.iloc[action]
        reward, reward_info = self.calculate_reward(event)  # Now getting both reward and info

        # Store the components
        self.last_reward_components = reward_info['components']  # This contains the detailed components

        # Track analytics if available
        if hasattr(self, 'analytics') and self.analytics is not None:
            # Create state data dictionary
            state_data = {
                'current_event_index': self.current_event_index,
                'action_taken': action,
                'event_id': event['Event ID'],
                'event_type': event['Event Type'],
                'reward_components': self.last_reward_components,
                'features': self.get_event_features(self.current_event_index)
            }

            # Track the state transition in analytics
            self.analytics.track_environment_state(state_data, action, reward, self.done)

        # Early termination for very bad recommendations
        if reward < -0.8:  # Normalized threshold
            self.done = True
            return np.zeros(self.observation_space), reward, True

        # Only log steps occasionally to reduce output
        if random.random() < 0.01:  # 1% chance to log
            debug_print(f"Step taken - Action: {action}, Reward: {reward:.2f}")

        self.current_event_index += 1

        if self.current_event_index >= self.max_events:
            self.done = True
            return np.zeros(self.observation_space), reward, True
        else:
            next_state = self.get_event_features(self.current_event_index)

        return next_state, reward, self.done

    def get_event_features(self, event_index):
        """Extract field scores for the event at the given index."""
        try:
            event = self.events.iloc[event_index]
            features = []

            # Get cached stats for the event type, fallback to global stats if necessary
            event_type = event['Event Type']
            cached_stats = self.event_type_stats_cache.get(event_type, self.global_stats) if pd.notna(
                event_type) else self.global_stats

            # Apply strict filtering for price and popularity first
            price = event['Price ($)']
            popularity = event['Popularity']

            # Strong penalties for out-of-range values
            if not pd.isna(price) and self.user['Price Range'] != 'irrelevant':
                price_range = self.get_price_range(self.user['Price Range'])
                if price > price_range['max']:
                    features = [-1] * 5  # Strong penalty
                    return np.array(features, dtype=np.float32)

            if not pd.isna(popularity) and self.user['Preferred Crowd Size'] != 'irrelevant':
                pop_range = self.get_popularity_range(self.user['Preferred Crowd Size'])
                if popularity < pop_range['min'] or popularity > pop_range['max']:
                    features = [-.50] * 5  # Moderate penalty
                    return np.array(features, dtype=np.float32)

            # 1. Event Type Score (using fallback)
            event_type_score = self.score_event_type(event)
            features.append(event_type_score)

            # 2. Distance Score (use cached mean if missing)
            distance = event['Distance (km)']
            distance = distance if not pd.isna(distance) else cached_stats['distance_stats']['mean']
            distance_score = self.score_minimize(distance, 0, self.max_distance * 2)
            features.append(distance_score)

            # 3. Time Score (fallback to mean time if missing or event in the past)
            time_until_event = event['Time Until Event (hrs)']
            time_until_event = time_until_event if not pd.isna(time_until_event) and time_until_event >= 0 else \
            cached_stats['time_stats']['mean']
            time_score = self.score_minimize(time_until_event, 0, self.max_time_difference)
            features.append(time_score)

            # 4. Popularity Score (use cached popularity mean if missing)
            popularity = event['Popularity']
            popularity = popularity if not pd.isna(popularity) else cached_stats['popularity_stats']['mean']
            popularity_score = self.score_popularity(popularity)
            features.append(popularity_score)

            # 5. Price Score (use cached mean price if missing)
            price = event['Price ($)']
            price = price if not pd.isna(price) else cached_stats['price_stats']['mean']
            price_score = self.score_price_relative(price, event_type)
            features.append(price_score)

            feature_vector = np.array(features, dtype=np.float32)
            debug_print(f"Extracted features for event {event_index}: {feature_vector}")
            debug_print(f"get_event_features output - index: {event_index}, shape: {feature_vector}")
            return feature_vector

        except Exception as e:
            logging.error(f"Error extracting features for event {event_index}: {str(e)}")
            return np.zeros(6, dtype=np.float32)  # Return zero vector on error

    # Scoring Functions
    def score_event_type(self, event):
        """Score the event type."""
        event_type = event['Event Type']
        if pd.isna(event_type):
            return -50  # Penalize missing event type

        # Clean the event type
        event_type_lower = event_type.lower()

        # Debug prints
        debug_print(f"\nEvent Type Scoring Debug:")
        debug_print(f"Raw event type: {event_type}")
        debug_print(f"Processed event type: {event_type_lower}")
        debug_print(f"User's preferred events: {self.user_preferred_events}")
        debug_print(f"User's undesirable events: {self.user_undesirable_events}")

        # Check for exact or partial matches in preferred events
        for preferred in self.user_preferred_events:
            if (event_type_lower == preferred.lower() or
                    event_type_lower in preferred.lower() or
                    preferred.lower() in event_type_lower):
                debug_print(f"Match found in preferred events: {preferred}")
                return 1

        # Check for exact or partial matches in undesirable events
        for undesirable in self.user_undesirable_events:
            if (event_type_lower == undesirable.lower() or
                    event_type_lower in undesirable.lower() or
                    undesirable.lower() in event_type_lower):
                debug_print(f"Match found in undesirable events: {undesirable}")
                return -1

        debug_print("No match found in either list")
        return 0

    def score_distance(self, distance):
        """
        Score distance with emphasis on closer events.
        Provides maximum score for closest events, decreasing as distance increases.
        """
        if pd.isna(distance):
            return 0

        max_distance = self.user['Max Distance (km)']

        if distance <= max_distance:
            # Linear decrease from 100 to 0 as distance increases
            return 1 * (1 - (distance / max_distance))
        else:
            # Penalty for being over max distance
            overage = (distance - max_distance) / max_distance
            return max(-1, -1 * overage)

    def score_time(self, time_until_event):
        """
        Score time with emphasis on immediate events.
        Provides maximum score for events happening soon, decreasing as time increases.
        """
        if pd.isna(time_until_event) or time_until_event < 0:
            return -1  # Penalize past events

        # Consider events up to 2 weeks (336 hours) ahead
        max_preferred_time = 336  # 14 days * 24 hours

        if time_until_event <= max_preferred_time:
            # Linear decrease from 100 to 0 as time increases
            return 1 * (1 - (time_until_event / max_preferred_time))
        else:
            # Moderate penalty for events too far in the future
            overage = (time_until_event - max_preferred_time) / max_preferred_time
            return max(-.50, -.25 * overage)  # Less severe penalty than distance

    def score_popularity(self, popularity):
        """
        Score popularity with proper penalties:
        - Within range: 1.0
        - Near range (±30%): 0.5
        - Outside range: negative scores
        - Exception: Large preference never penalizes for being too popular
        """
        if pd.isna(popularity):
            return 0

        crowd_pref = self.user['Preferred Crowd Size']
        if crowd_pref == 'irrelevant':
            return 0

        pop_range = self.get_popularity_range(crowd_pref)
        min_pop = pop_range['min']
        max_pop = pop_range['max']

        # Within range
        if min_pop <= popularity <= max_pop:
            return 1.0

        # Below range
        if popularity < min_pop:
            percent_below = (min_pop - popularity) / min_pop
            if percent_below <= 0.3:
                return 0.5
            return -1.0

        # Above range (except for Large preference)
        if crowd_pref != 'Large':
            percent_above = (popularity - max_pop) / max_pop
            if percent_above <= 0.3:
                return 0.5
            return -1.0

        return 1.0  # Large preference with above-range popularity

    def score_price_relative(self, event_price, event_type):
        """
        Score price based on user's preferred range:
        - Within range: 1.0
        - Below range but within 30%: 0.5
        - Below range more than 30%: 0.0
        - Above range but within 30%: 0.0
        - Above range more than 30%: -1.0
        """
        if pd.isna(event_price):
            return 0

        # Handle free events
        if event_price == 0:
            return 1.0  # Free events are good for everyone

        # Handle irrelevant preference
        user_price_pref = self.user['Price Range']
        if user_price_pref == 'irrelevant':
            return 0

        # Get price range
        price_range = self.get_price_range(user_price_pref)
        min_price = price_range['min']
        max_price = price_range['max']

        # Within range - perfect score
        if min_price <= event_price <= max_price:
            return 1.0

        # Below range
        if event_price < min_price:
            # Calculate how far below
            percent_below = (min_price - event_price) / min_price
            if percent_below <= 0.3:  # Within 30% below
                return 0.5
            return 0.0  # More than 30% below

        # Above range
        if event_price > max_price:
            # Handle infinite max price case
            if max_price == float('inf'):
                return 0

            # Calculate how far above
            percent_above = (event_price - max_price) / max_price
            if percent_above <= 0.3:  # Within 30% above
                return 0.0
            return -1.0  # More than 30% above

    def score_minimize(self, value, best_value, worst_value):
        """Score a value where lower is better."""
        if value <= best_value:
            return 1
        elif value >= worst_value:
            return -1
        else:
            normalized_value = (value - best_value) / (worst_value - best_value)
            penalty = 1 * (1 - np.exp(-5 * normalized_value))
            return 1 - penalty

    def score_maximize(self, value, best_value, worst_value):
        """Score a value where higher is better."""
        if value >= best_value:
            return 1
        elif value <= worst_value:
            return -1
        else:
            normalized_value = (best_value - value) / (best_value - worst_value)
            reward = 1 * (1 - np.exp(-5 * normalized_value))
            return 1 - reward

    def score_target(self, value, target_value, acceptable_range):
        """Score a value based on proximity to a target."""
        deviation = abs(value - target_value)
        if deviation >= acceptable_range:
            return -1
        else:
            normalized_deviation = deviation / acceptable_range
            penalty = 100 * (1 - np.exp(-5 * (1 - normalized_deviation)))
            return 1 - penalty

    def calculate_reward(self, event):
        """Compute the total reward as the weighted average of individual field scores."""
        # Extract feature scores with weights
        weights = {
            'event_type': 0.40,  # Most important
            'distance': 0.25,  # Second most important
            'price': 0.15,  # Third most important
            'time': 0.20,  # Equal to price
        }

        scores = {
            'event_type': self.score_event_type(event),
            'distance': self.score_distance(event['Distance (km)']),
            'time': self.score_time(event['Time Until Event (hrs)']),
            'popularity': self.score_popularity(event['Popularity']),
            'price': self.score_price_relative(event['Price ($)'], event['Event Type']),
        }

        # Calculate weighted components
        weighted_components = {k: scores[k] * weights[k] for k in weights}

        # Calculate weighted average
        weighted_reward = sum(weighted_components.values())

        # Store the components for analysis
        reward_info = {
            'total': weighted_reward,
            'components': weighted_components,
            'weights': weights
        }

        # Debug print to verify data
        debug_print(f"Sending reward info to analytics: {reward_info}")

        # Call analytics
        if hasattr(self, 'analytics') and self.analytics is not None:
            self.analytics.track_reward_calculation(event, reward_info)


        if DEBUG_MODE:
            debug_print(f"\nReward breakdown for event {event['Event ID']}:")
            debug_print("\nRaw Scores:")
            for k in scores:
                debug_print(f"{k}: {scores[k]:.2f}")
            debug_print("\nWeighted Scores:")
            for k in weighted_components:
                debug_print(f"{k}: {weighted_components[k]:.2f}")
            debug_print(f"\nFinal normalized reward: {weighted_reward:.2f}")

        return weighted_reward, reward_info

    def analyze_recommendation(self, event):
        """Delegate to analytics class if available."""
        if self.analytics:
            self.analytics.analyze_recommendation(event)
        else:
            logging.warning("No analytics instance available for recommendation analysis")

    def visualize_component_impact(self, event):
        """Delegate to analytics class if available."""
        if self.analytics:
            self.analytics.visualize_component_impact(event)
        else:
            logging.warning("No analytics instance available for component visualization")

    def get_state(self):
        """Get normalized state representation."""
        try:
            # Get current event using current_event_index
            if self.current_event_index >= len(self.events):
                logging.warning("Current event index out of bounds")
                return np.zeros(5, dtype=np.float32)

            current_event = self.events.iloc[self.current_event_index]

            state = np.array([
                self.score_popularity(current_event['Popularity']) / 100,  # Normalize to [-1, 1]
                self.score_price_relative(current_event['Price ($)'],
                                          current_event['Event Type']) / 100,
                self.score_distance(current_event['Distance (km)']) / 100,
                self.score_time(pd.to_datetime(current_event['Date/Time'])) / 100,
                self.score_event_type(current_event) / 100,
            ], dtype=np.float32)

            # Replace any NaN values with 0
            state = np.nan_to_num(state, nan=0.0, posinf=1.0, neginf=-1.0)
            debug_print(f"Environment state shape: {state.shape}")  # Debug print

            return state

        except Exception as e:
            logging.error(f"Error in get_state: {str(e)}")
            return np.zeros(5, dtype=np.float32)  # Return zero state on error

    def get_popularity_range(self, crowd_size):
        """Get popularity range with case-insensitive lookup."""
        if pd.isna(crowd_size):
            return POPULARITY_RANGES['irrelevant']
        return POPULARITY_RANGES[crowd_size.title()]  # Convert to Title Case

    def get_price_range(self, price_pref):
        """Get price range with exact match."""
        if pd.isna(price_pref):
            return PRICE_RANGES['irrelevant']
        return PRICE_RANGES[price_pref] # $ signs need exact match


    def get_next_model_folder(self):
        """Create and get the next available model folder number."""
        base_dir = "Training/analytics"
        os.makedirs(base_dir, exist_ok=True)

        # Get existing model folders
        existing_folders = [d for d in os.listdir(base_dir)
                            if os.path.isdir(os.path.join(base_dir, d))
                            and d.startswith("model_")]

        # Find next available number
        if not existing_folders:
            next_num = 1
        else:
            max_num = max([int(f.split('_')[1]) for f in existing_folders])
            next_num = max_num + 1

        # Create new folder
        model_folder = os.path.join(base_dir, f"model_{next_num}")
        os.makedirs(model_folder, exist_ok=True)
        os.makedirs(os.path.join(model_folder, "component_analysis"), exist_ok=True)

        return model_folder


