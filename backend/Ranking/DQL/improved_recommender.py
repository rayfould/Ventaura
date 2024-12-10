"""
improved_recommender.py
Implements an improved DQN-based event recommender with hybrid rewards.
"""

from config import *
from DQL import QNetwork
from Event_Ranking_Environment import EventRecommendationEnv
from user_simulator import HybridRewardSystem
from DQL import ReplayBuffer
from training_analytics import TrainingAnalytics


class ImprovedEventRecommenderDQN:
    def __init__(self, state_size, action_size, user, events_df, analytics=None):
        """Initialize the DQN recommender."""
        self.state_size = state_size
        self.action_size = action_size
        self.events_df = events_df
        self.batch_size = 64
        self.analytics = analytics  # Store analytics reference

        # Initialize networks
        self.dqn = QNetwork(state_size, action_size, analytics)
        self.target_network = self.dqn.target_network

        # Initialize optimizer
        self.optimizer = optim.Adam(self.dqn.parameters(), lr=LEARNING_RATE)
        # Initialize replay buffer
        self.memory = ReplayBuffer(10000, self.batch_size)

        # Initialize environment and reward system
        self.env = EventRecommendationEnv(events_df, user)
        self.reward_system = HybridRewardSystem(user, events_df)
        # Training parameters
        self.epsilon = INITIAL_EPSILON
        self.epsilon_decay = EPSILON_DECAY
        self.initial_epsilon = INITIAL_EPSILON
        self.final_epsilon = FINAL_EPSILON
        self.gamma = GAMMA
        self.target_update_frequency = TARGET_UPDATE_FREQUENCY

        # Analytics
        self.reward_history = []
        self.episode_analytics = []  # Add this
        self.action_history = []  # Add this

        debug_print(
            f"Initialized ImprovedEventRecommenderDQN with state_size: {state_size}, action_size: {action_size}")

    def select_action(self, state):
        """Select action using epsilon-greedy with temperature scaling."""
        if random.random() < self.epsilon:
            action = random.randint(0, self.action_size - 1)
            debug_print(f"Random action selected: {action}")
            return action

        with torch.no_grad():
            q_values = self.dqn(torch.FloatTensor(state).unsqueeze(0))

            # Handle NaN/Inf values
            if torch.isnan(q_values).any() or torch.isinf(q_values).any():
                debug_print("Warning: NaN or Inf in Q-values, defaulting to random action")
                return random.randint(0, self.action_size - 1)

            # Normalize Q-values to prevent extreme values
            q_values = torch.nan_to_num(q_values, nan=0.0, posinf=1.0, neginf=-1.0)

            # Apply temperature scaling with safety checks
            q_values = q_values / max(TEMPERATURE, 1e-8)  # Prevent division by zero

            # Ensure valid probability distribution
            max_q = q_values.max()
            q_values = q_values - max_q  # Subtract maximum for numerical stability

            # Apply softmax with safety checks
            exp_q = torch.exp(q_values)
            if torch.isnan(exp_q).any() or torch.isinf(exp_q).any():
                debug_print("Warning: NaN or Inf after exp, defaulting to random action")
                return random.randint(0, self.action_size - 1)

            probs = exp_q / exp_q.sum()

            # Final safety check
            if torch.isnan(probs).any() or torch.isinf(probs).any() or (probs < 0).any():
                debug_print("Warning: Invalid probabilities, defaulting to random action")
                return random.randint(0, self.action_size - 1)

            try:
                action = torch.multinomial(probs, 1).item()
                debug_print(f"Q-value based action selected: {action}")
                return action
            except RuntimeError:
                debug_print("Error in multinomial sampling, defaulting to random action")
                return random.randint(0, self.action_size - 1)

    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer."""
        if next_state is not None:  # Only remember valid transitions
            self.memory.add(state, action, reward, next_state, done)
            debug_print(f"Stored experience: State shape: {state.shape}, Action: {action}, Reward: {reward:.2f}")

    def replay(self):
        if self.memory.size() < self.batch_size:
            return 0.0

        states, actions, rewards, next_states, dones = self.memory.sample()

        # Convert to tensors
        state_batch = torch.FloatTensor(states)
        action_batch = torch.LongTensor(actions)
        reward_batch = torch.FloatTensor(rewards)
        next_state_batch = torch.FloatTensor(next_states)
        done_batch = torch.FloatTensor(dones)

        # DDQN: Use online network to SELECT actions
        with torch.no_grad():
            # Select actions using online network
            next_actions = self.dqn(next_state_batch).argmax(dim=1, keepdim=True)

            # Evaluate actions using target network
            next_q = self.target_network(next_state_batch).gather(1, next_actions)

            # Calculate target Q-values
            target_q = reward_batch.unsqueeze(1) + (1 - done_batch.unsqueeze(1)) * self.gamma * next_q

        # Get current Q-values from online network
        current_q = self.dqn(state_batch).gather(1, action_batch.unsqueeze(1))

        # Compute loss and update
        loss = F.smooth_l1_loss(current_q, target_q)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def update_target_network(self):
        """Update target network weights"""
        self.dqn.copy_weights_to_target()

    def get_reward(self, event, state):
        """Get reward for the current action"""
        reward, reward_components = self.reward_system.calculate_reward(event)

        # Store reward components for analysis if needed
        self.last_reward_components = reward_components

        return reward

    def train(self, num_episodes):
        """Train the model."""
        initial_memory = monitor_memory()

        pbar = tqdm(range(num_episodes), desc="Training Episodes")
        for episode in pbar:
            state = self.env.reset()
            done = False
            episode_reward = 0
            episode_loss = 0
            episode_actions = []
            episode_q_values = []
            steps = 0

            while not done:
                action = self.select_action(state)
                self.update_action_history(action)
                episode_actions.append(action)

                # Get Q-values for analytics
                with torch.no_grad():
                    q_values = self.dqn(torch.FloatTensor(state).unsqueeze(0))
                    episode_q_values = episode_q_values[-1000:] + q_values.numpy().flatten().tolist()
                next_state, reward, done = self.env.step(action)

                if hasattr(self.env, 'last_reward_components'):
                    components = self.env.last_reward_components
                    debug_print(f"Raw components received: {components}")
                    if self.analytics:
                        for component in ['event_type', 'distance', 'price', 'time', 'popularity']:
                            value = components.get(component, 0)
                            if isinstance(value, np.ndarray):
                                value = float(value)  # Convert numpy values to float
                            self.analytics.history['reward_components'][component].append(value)
                            debug_print(
                                f"Current {component} deque length: {len(self.analytics.history['reward_components'][component])}")

                if next_state is not None:
                    self.remember(state, action, reward, next_state, done)
                    loss = self.replay()
                    episode_loss += loss if loss is not None else 0

                    # Track DDQN metrics
                    self.track_ddqn_metrics()

                    # Track DQL metrics after replay (where loss is defined)
                    if self.analytics:
                        # Get Q-values from both networks
                        with torch.no_grad():
                            online_q = q_values.mean().item()
                            target_q = self.dqn.target_network(torch.FloatTensor(state).unsqueeze(0)).mean().item()

                        self.analytics.track_dql_training(
                            q_values=q_values,
                            online_q=online_q,
                            target_q=target_q,
                            loss=loss if loss is not None else 0,
                            action_taken=action
                        )

                # Track environment state
                if self.analytics:
                    self.analytics.track_environment_state(
                        state_data=state,
                        action=action,
                        reward=reward,
                        done=done
                    )

                state = next_state
                episode_reward += reward
                steps += 1

            # Decay epsilon after each episode
            self.decay_epsilon(episode)

            # Add episode data to analytics
            if self.analytics:  # Add check for analytics existence
                self.analytics.add_episode_data(
                    reward=episode_reward,
                    loss=episode_loss / steps if steps > 0 else 0,
                    epsilon=self.epsilon,
                    q_values=episode_q_values,
                    actions=episode_actions,
                    episode_length=steps,
                    reward_components=self.last_reward_components if hasattr(self, 'last_reward_components') else None
                )
            # Update progress bar
            recent_rewards = list(self.analytics.history['rewards'])  # Convert deque to list
            avg_reward = np.mean(recent_rewards[-100:]) if recent_rewards else 0  # Handle empty case

            pbar.set_postfix({
                'Reward': f'{episode_reward:.2f}',
                'Steps': steps,
                'Epsilon': f'{self.epsilon:.2f}',
                'Avg Reward': f'{avg_reward:.2f}'  # Use the calculated average
            })

            # Generate interim analytics every N episodes
            if (episode + 1) % 1000 == 0:
                self.analytics.plot_training_metrics()

                # Add these new analysis calls
                if self.analytics:
                    debug_print("Generating periodic analyses...")

                    # Environment analysis
                    self.analytics.analyze_environment_metrics()

                    # DQL performance analysis
                    self.analytics.analyze_dql_performance()

                    # User behavior analysis (if applicable)
                    if hasattr(self.env, 'user_simulator'):
                        self.analytics.analyze_user_behavior()

                # Save checkpoint model
                checkpoint_path = self.analytics.checkpoints_dir / f'checkpoint_episode_{episode + 1}.pth'
                self.save_model(checkpoint_path)
                debug_print(f"Checkpoint saved at episode {episode + 1}")

            # Update target network periodically
            if episode % self.target_update_frequency == 0:
                self.update_target_network()
                debug_print("Target network updated")

        # Generate final analytics
        debug_print("About to generate final analytics")
        self.analytics.plot_training_metrics()
        debug_print("About to analyze reward components")
        self.analytics.analyze_recommendation(self.events_df)
        self.analytics.analyze_problematic_rewards()
        self.analytics.generate_report()

        # Add final comprehensive analysis
        debug_print("Generating final comprehensive analysis...")
        self.analytics.analyze_environment_metrics()
        self.analytics.analyze_dql_performance()
        if hasattr(self.env, 'user_simulator'):
            self.analytics.analyze_user_behavior()

        # Generate reward patterns analysis
        self.analytics.analyze_reward_patterns()
        # Save final model using analytics directories
        final_path = self.analytics.recommender_dir / f"final_model_{time.strftime('%Y%m%d_%H%M%S')}.pth"
        self.save_model(final_path)
        info_print(f"Final model saved to {final_path}")

        if self.analytics:
            info_print("\nTraining Summary:")
            recent_rewards = list(self.analytics.history['rewards'])
            avg_reward = np.mean(recent_rewards[-100:]) if recent_rewards else 0
            info_print(f"Final Average Reward (last 100 episodes): {avg_reward:.2f}")
            info_print(f"Best Episode Reward: {max(recent_rewards) if recent_rewards else 0:.2f}")
            info_print(f"Final Epsilon: {self.epsilon:.4f}")
            info_print(f"Total Steps: {sum(self.analytics.history['episode_lengths'])}")

        final_memory = monitor_memory()
        info_print(f"Final memory usage: {final_memory:.2f} MB")
        info_print(f"Total memory change: {final_memory - initial_memory:.2f} MB")

        return self.analytics  # Return the class-level analytics instance

    def track_ddqn_metrics(self):
        """Track metrics specific to Double DQN performance"""
        if self.analytics:
            with torch.no_grad():
                # Sample some states
                if self.memory.size() >= self.batch_size:
                    states, _, _, _, _ = self.memory.sample()
                    state_batch = torch.FloatTensor(states)

                    # Get Q-values from both networks
                    online_q = self.dqn(state_batch)
                    target_q = self.target_network(state_batch)

                    # Calculate average Q-value difference
                    q_diff = (online_q - target_q).abs().mean().item()

                    # Initialize ddqn_metrics in history if it doesn't exist
                    if 'ddqn_metrics' not in self.analytics.history:
                        self.analytics.history['ddqn_metrics'] = {
                            'q_value_diff': [],
                            'target_q_values': [],
                            'online_q_values': []
                        }

                    # Track metrics
                    self.analytics.history['ddqn_metrics']['q_value_diff'].append(q_diff)
                    self.analytics.history['ddqn_metrics']['target_q_values'].append(target_q.mean().item())
                    self.analytics.history['ddqn_metrics']['online_q_values'].append(online_q.mean().item())

                    debug_print(f"DDQN Metrics - Q-diff: {q_diff:.3f}, "
                                f"Online Q: {online_q.mean().item():.3f}, "
                                f"Target Q: {target_q.mean().item():.3f}")

    def decay_epsilon(self, episode):
        """Decay epsilon based on episode progress."""
        progress = episode / NUM_EPISODES

        if progress >= TRAINING_PROGRESS:
            self.epsilon = FINAL_EPSILON
        else:
            # Linear decay instead of exponential
            decay_amount = (INITIAL_EPSILON - FINAL_EPSILON) * (progress / TRAINING_PROGRESS)
            self.epsilon = INITIAL_EPSILON - decay_amount


        if episode % 100 == 0:  # Log every 100 episodes instead of steps
            debug_print(f"Episode: {episode}, Progress: {progress:.2f}, Epsilon: {self.epsilon:.8f}")

    def _analyze_episode(self, episode_data):
        """
        Analyze the performance of an episode.

        Args:
            episode_data: Dictionary containing episode information
        """
        try:
            episode = episode_data['episode']
            total_reward = episode_data['total_reward']

            # Simple analysis of episode performance
            debug_print(f"\nEpisode Analysis:")
            debug_print(f"Average Reward: {total_reward / self.action_size:.2f}")

            # Store analysis results if needed
            self.episode_analytics.append({
                'episode': episode,
                'total_reward': total_reward,
                'average_reward': total_reward / self.action_size
            })

        except Exception as e:
            logging.error(f"Error analyzing episode: {str(e)}")

    def get_recent_actions(self, n_recent=5):
        """Get the most recent actions taken."""
        if not hasattr(self, 'action_history'):
            self.action_history = []
        return self.action_history[-n_recent:]

    def get_event_features(self, action):
        """Extract relev    ant features for diversity calculation."""
        event = self.events_df.iloc[action]
        features = []

        # Add event type (one-hot encoded)
        if 'Event Type' in event:
            features.extend(self._one_hot_encode(event['Event Type']))

        # Add normalized price
        if 'Price ($)' in event:
            max_price = self.events_df['Price ($)'].max()
            normalized_price = event['Price ($)'] / max_price if max_price > 0 else 0
            features.append(normalized_price)

        # Add normalized distance
        if 'Distance (km)' in event:
            max_distance = self.events_df['Distance (km)'].max()
            normalized_distance = event['Distance (km)'] / max_distance if max_distance > 0 else 0
            features.append(normalized_distance)

        return np.array(features)

    def calculate_diversity_bonus(self, action, recent_actions):
        """Calculate bonus for diverse recommendations."""
        if not recent_actions:
            return 1.0

        # Check how different this action is from recent ones
        action_features = self.get_event_features(action)
        similarity_scores = []

        for past_action in recent_actions:
            past_features = self.get_event_features(past_action)
            similarity = self.calculate_similarity(action_features, past_features)
            similarity_scores.append(similarity)

        # More different = higher bonus
        avg_similarity = np.mean(similarity_scores)
        diversity_bonus = 1 - avg_similarity
        debug_print(f"Diversity bonus for action {action}: {diversity_bonus:.2f}")
        return diversity_bonus

    def calculate_similarity(self, features1, features2):
        """Calculate cosine similarity between two feature vectors."""
        if len(features1) == 0 or len(features2) == 0:
            return 0

        dot_product = np.dot(features1, features2)
        norm1 = np.linalg.norm(features1)
        norm2 = np.linalg.norm(features2)

        if norm1 == 0 or norm2 == 0:
            return 0

        return dot_product / (norm1 * norm2)

    def _one_hot_encode(self, event_type):
        """One-hot encode event type."""
        if not hasattr(self, 'event_types'):
            self.event_types = list(self.events_df['Event Type'].unique())

        encoding = [0] * len(self.event_types)
        if event_type in self.event_types:
            encoding[self.event_types.index(event_type)] = 1
        return encoding

    def update_action_history(self, action):
        """Update the history of actions taken."""
        if not hasattr(self, 'action_history'):
            self.action_history = []
        self.action_history.append(action)
        # Keep only recent history
        self.action_history = self.action_history[-10:]


    def save_model(self, path):
        """
        Save the DQN model.

        Args:
            path (str): Path to save the model
        """
        torch.save(self.dqn.state_dict(), path)
        debug_print(f"Model saved to {path}")

    def load_model(self, path):
        """
        Load a saved DQN model.

        Args:
            path (str): Path to load the model from
        """
        self.dqn.load_state_dict(torch.load(path))
        self.dqn.eval()
        debug_print(f"Model loaded from {path}")

    def cleanup(self):
        """Clear all histories and free memory"""
        self.action_history.clear()
        self.reward_history.clear()
        self.episode_analytics.clear()
        if hasattr(self, 'memory'):
            self.memory.clear()
        self.dqn.zero_grad(set_to_none=True)
        self.target_network.zero_grad(set_to_none=True)
