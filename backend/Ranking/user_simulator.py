"""
user_simulator.py
This module implements user simulation and hybrid reward calculation for event recommendations.
"""

from config import *
from Event_Ranking_Environment import EventRecommendationEnv


class SimulatedUserFeedback:
    def __init__(self, user, events_df, preference_drift=0.1, analytics=None):
        # Make a deep copy of the user data to prevent warnings and potential issues
        self.user = user.copy() if isinstance(user, pd.Series) else user
        self.preference_drift = preference_drift
        self.events_df = events_df
        self.interaction_history = []
        self.analytics = analytics
        self.env = EventRecommendationEnv(events_df, user)

        # Handle Preferred Events
        if isinstance(self.user['Preferred Events'], str):
            self.user['Preferred Events'] = [x.strip() for x in self.user['Preferred Events'].split(',')]
        elif isinstance(self.user['Preferred Events'], (list, np.ndarray)):
            self.user['Preferred Events'] = list(self.user['Preferred Events'])
        else:
            self.user['Preferred Events'] = []

        # Handle Undesirable Events
        if isinstance(self.user['Undesirable Events'], str):
            self.user['Undesirable Events'] = [x.strip() for x in self.user['Undesirable Events'].split(',')]
        elif isinstance(self.user['Undesirable Events'], (list, np.ndarray)):
            self.user['Undesirable Events'] = list(self.user['Undesirable Events'])
        else:
            self.user['Undesirable Events'] = []

        debug_print(f"Initialized SimulatedUserFeedback with preference drift: {preference_drift}")

    def _get_preference_changes(self):
        """
        Track changes in user preferences over time.

        Returns:
            dict: Changes in user preferences
        """
        try:
            # Initialize preference changes dictionary
            preference_changes = {
                'preferred_events': [],
                'undesirable_events': [],
                'preference_drift': self.preference_drift
            }

            # Simulate preference drift
            if random.random() < self.preference_drift:
                # Randomly modify preferences
                if self.user['Preferred Events'] and random.random() < 0.5:
                    # Randomly remove a preferred event
                    removed_event = random.choice(self.user['Preferred Events'])
                    self.user['Preferred Events'].remove(removed_event)
                    preference_changes['preferred_events'].append({
                        'action': 'removed',
                        'event_type': removed_event
                    })

                if self.user['Undesirable Events'] and random.random() < 0.5:
                    # Randomly remove an undesirable event
                    removed_event = random.choice(self.user['Undesirable Events'])
                    self.user['Undesirable Events'].remove(removed_event)
                    preference_changes['undesirable_events'].append({
                        'action': 'removed',
                        'event_type': removed_event
                    })

                # Potentially swap between preferred and undesirable
                if self.user['Preferred Events'] and random.random() < 0.3:
                    event_to_swap = random.choice(self.user['Preferred Events'])
                    self.user['Preferred Events'].remove(event_to_swap)
                    self.user['Undesirable Events'].append(event_to_swap)
                    preference_changes['preferred_events'].append({
                        'action': 'moved_to_undesirable',
                        'event_type': event_to_swap
                    })

            return preference_changes

        except Exception as e:
            logging.error(f"Error in _get_preference_changes: {str(e)}")
            return {
                'preferred_events': [],
                'undesirable_events': [],
                'preference_drift': self.preference_drift,
                'error': str(e)
            }

    def simulate_interaction(self, event):
        """Simulate user interaction with an event."""
        try:
            # Ensure event type is string
            event_type = str(event['Event Type']) if pd.notna(event['Event Type']) else 'Unknown'

            interaction_prob = self._calculate_interaction_probability(event)

            # Base interactions
            interactions = {
                'viewed': True,  # Always viewed when recommended
                'clicked': random.random() < interaction_prob,
                'bookmarked': random.random() < interaction_prob * 0.7,
                'purchased': random.random() < interaction_prob * 0.4
            }

            # Add deeper interactions if basic interaction occurred
            if interactions['clicked']:
                interactions.update(self._simulate_deeper_interactions(event, interaction_prob))

            # Track in analytics if available
            if self.analytics:
                self.analytics.track_user_simulation(
                    event=event,
                    interaction_data=interactions,  # Pass the interactions dictionary, not interaction_prob
                    preference_data=self._get_preference_changes()
                )

            return interactions

        except Exception as e:
            logging.error(f"Error in simulate_interaction: {str(e)}")
            return {'viewed': True}  # Return minimal interaction on error

    def _calculate_interaction_probability(self, event):
        """Calculate probability of user interacting with event"""
        try:
            base_prob = 0.3

            # Handle Event Type safely
            event_type = str(event['Event Type']) if pd.notna(event['Event Type']) else 'Unknown'

            # Check preferred/undesirable events
            if event_type in self.user['Preferred Events']:
                base_prob += 0.4
            elif event_type in self.user['Undesirable Events']:
                base_prob -= 0.4

            # Price range check
            if self.user['Price Range'] != 'irrelevant':
                price = event['Price ($)']
                if not pd.isna(price):
                    price_range = PRICE_RANGES[self.user['Price Range']]
                    if price > price_range['max']:
                        base_prob *= 0.2

            # Crowd size check
            if self.user['Preferred Crowd Size'] != 'irrelevant':
                popularity = event['Popularity']
                if not pd.isna(popularity):
                    pop_range = POPULARITY_RANGES[self.user['Preferred Crowd Size'].upper()]
                    if not (pop_range['min'] <= popularity <= pop_range['max']):
                        base_prob *= 0.5

            # Add some randomness
            noise = np.random.normal(0, self.preference_drift)

            return np.clip(base_prob + noise, 0, 1)

        except Exception as e:
            logging.error(f"Error in _calculate_interaction_probability: {str(e)}")
            return 0.3  # Return base probability on error

    def _simulate_deeper_interactions(self, event, interaction_prob):
        """Simulate deeper engagement metrics."""
        try:
            event_type = str(event['Event Type']) if pd.notna(event['Event Type']) else 'Unknown'

            # Base time spent viewing (in minutes)
            mean_time = 30 if event_type in self.user['Preferred Events'] else 15
            # Convert numpy random value to float and then take max
            time_spent = float(max(0.0, float(np.random.normal(mean_time, mean_time / 4))))

            return {
                'time_spent': time_spent,
                'shared': random.random() < interaction_prob * 0.3,
                'commented': random.random() < interaction_prob * 0.2
            }

        except Exception as e:
            logging.error(f"Error in _simulate_deeper_interactions: {str(e)}")
            return {'time_spent': 15, 'shared': False, 'commented': False}


class HybridRewardSystem:
    def __init__(self, user, events_df):
        self.env = EventRecommendationEnv(events_df, user)
        self.simulated_user = SimulatedUserFeedback(user, events_df)
        self.user_id = user['User ID']

        # Base weights for personalized vs interaction rewards
        self.reward_weights = {
            'personalized': 0.7,
            'interaction': 0.3
        }

        # Component weights that will be adjusted per user
        self.component_weights = {
            'event_type': 0.40,
            'distance': 0.20,
            'price': 0.15,
            'time': 0.15,
            'popularity': 0.10
        }

        # Store user-specific adjustments
        self.user_weight_adjustments = {}
        self.adjustment_rate = 0.1

        debug_print(f"Initialized HybridRewardSystem with weights: {self.reward_weights}")

    def get_adjusted_weights(self):
        """Get current weights with any user-specific adjustments"""
        if self.user_id not in self.user_weight_adjustments:
            return self.component_weights.copy()

        base_weights = self.component_weights.copy()
        adjustments = self.user_weight_adjustments[self.user_id]

        # Apply adjustments
        for component in base_weights:
            if component in adjustments:
                base_weights[component] *= (1 + adjustments[component])

        # Normalize
        total = sum(base_weights.values())
        return {k: v / total for k, v in base_weights.items()}

    def update_weights(self, interactions, scores):
        """Update weights based on user interactions"""
        if self.user_id not in self.user_weight_adjustments:
            self.user_weight_adjustments[self.user_id] = {
                'event_type': 0,
                'distance': 0,
                'price': 0,
                'time': 0,
                'popularity': 0
            }

        adjustments = self.user_weight_adjustments[self.user_id]

        # Adjust weights based on interaction strength
        if interactions['clicked']:
            for component, score in scores.items():
                if score > 0:
                    adjustments[component] += self.adjustment_rate

        if interactions['bookmarked']:
            for component, score in scores.items():
                if score > 0:
                    adjustments[component] += self.adjustment_rate * 1.5

        if interactions['purchased']:
            for component, score in scores.items():
                if score > 0:
                    adjustments[component] += self.adjustment_rate * 2

    def calculate_reward(self, event, previous_events=None):
        # Get current adjusted weights
        current_weights = self.get_adjusted_weights()

        # Get personalized reward using environment with adjusted weights
        personalized_reward, reward_info = self.env.calculate_reward(event)

        # Get interaction reward and update weights
        interactions = self.simulated_user.simulate_interaction(event)
        interaction_reward = self._calculate_interaction_reward(event)

        # Update weights based on interactions
        self.update_weights(interactions, reward_info['scores'])

        # Combine rewards using weights
        total_reward = (self.reward_weights['personalized'] * personalized_reward +
                        self.reward_weights['interaction'] * interaction_reward)

        # Add small random noise
        noise = np.random.normal(0, 0.05)
        total_reward += noise

        debug_print(f"\nReward Components:")
        debug_print(f"Personalized Reward: {personalized_reward:7.2f}")
        debug_print(f"Interaction Reward: {interaction_reward:7.2f}")
        debug_print(f"Current Weights: {current_weights}")

        return total_reward, {
            'personalized_reward': personalized_reward,
            'interaction_reward': interaction_reward,
            'total': total_reward,
            'noise': noise,
            'components': reward_info['components'],
            'weights': current_weights,
            'interactions': interactions
        }

    def _calculate_interaction_reward(self, event):
        """
        Calculate reward based on simulated user interactions.

        Args:
            event (pd.Series): Event data

        Returns:
            float: Calculated interaction reward
        """
        interactions = self.simulated_user.simulate_interaction(event)

        reward = 0

        # Basic interaction rewards
        if interactions['clicked']:
            reward += .2

        if interactions['bookmarked']:
            reward += .3

        if interactions['purchased']:
            reward += .4

        # Time spent reward
        time_reward = min(interactions.get('time_spent', 0) / 60, .1)  # Normalize to 0-1
        reward += time_reward

        return reward

