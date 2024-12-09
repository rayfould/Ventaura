from config import *
import seaborn as sns
import viridis
class TrainingAnalytics:
    def __init__(self):
        self.model_num = get_next_model_number()
        self.directories = create_model_directories(self.model_num)

        # Create convenient shortcuts for commonly used paths
        self.analytics_base = self.directories['base']['analytics']
        self.models_base = self.directories['base']['models']
        self.component_dir = self.directories['analytics']['component_analysis']
        self.metrics_dir = self.directories['analytics']['training_metrics']
        self.additional_dir = self.directories['analytics']['additional_analysis']
        self.checkpoints_dir = self.directories['models']['checkpoints']
        self.recommender_dir = self.directories['models']['recommender']



        # Initialize data structures
        self.history = {
            'rewards': deque(maxlen=10000),
            'losses': deque(maxlen=10000),
            'epsilons': deque(maxlen=10000),
            'episode_lengths': deque(maxlen=10000),
            'q_values': deque(maxlen=10000),
            'actions': deque(maxlen=10000),
            'actions_taken': deque(maxlen=10000),
            'reward_components': {
                'event_type': deque(maxlen=10000),
                'distance': deque(maxlen=10000),
                'price': deque(maxlen=10000),
                'time': deque(maxlen=10000),
                'popularity': deque(maxlen=10000)
            },
            'ddqn_metrics': {  # Add this
                'q_value_diff': deque(maxlen=10000),
                'target_q_values': deque(maxlen=10000),
                'online_q_values': deque(maxlen=10000)
            }
        }

        self.interaction_metrics = {
            'views': deque(maxlen=10000),
            'clicks': deque(maxlen=10000),
            'bookmarks': deque(maxlen=10000),
            'purchases': deque(maxlen=10000),
            'time_spent': deque(maxlen=10000)
        }

        self.max_stored_actions = 10000
        self.max_stored_episodes = 10000
        self.max_stored_rewards = 10000

        # Set up plotting style
        self.setup_plotting_style()
        # Add memory management
        self.max_stored_actions = 10000  # Limit stored actions
        self.q_value_summary = {
            'mean': [],
            'std': [],
            'min': [],
            'max': []
        }

        self.user_simulation_metrics = {
            'interactions': {
                'views': deque(maxlen=10000),
                'clicks': deque(maxlen=10000),
                'bookmarks': deque(maxlen=10000),
                'purchases': deque(maxlen=10000),
                'time_spent': deque(maxlen=10000)
            },
            'preference_changes': deque(maxlen=10000),
            'interaction_patterns': defaultdict(lambda: defaultdict(int))
        }

        self.dql_metrics = {
            'q_values': {
                'mean': deque(maxlen=10000),
                'max': deque(maxlen=10000),
                'min': deque(maxlen=10000),
                'std': deque(maxlen=10000)
            },
            'loss': deque(maxlen=10000),
            'gradients': defaultdict(lambda: deque(maxlen=1000)),
            'action_distributions': defaultdict(int)
        }

        # Initialize DDQN metrics
        self.ddqn_metrics = {
            'online_q_values': deque(maxlen=10000),
            'target_q_values': deque(maxlen=10000),
            'q_value_diff': deque(maxlen=10000)
        }
        self.model_folder = self.directories['base']['models']
        self.metrics_folder = self.directories['analytics']['training_metrics']
        self.reward_folder = self.directories['analytics']['component_analysis']

        self.env = None

    def set_environment(self, env):
        """Set the environment reference for accessing scoring methods."""
        self.env = env

    def save_analysis(self, analysis_text, analysis_type):
        """
        Save analysis text to appropriate directory.

        Args:
            analysis_text (str): The analysis text to save
            analysis_type (str): Type of analysis ('component', 'training', 'additional')
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Select appropriate directory based on analysis type
        if analysis_type == 'component':
            save_dir = self.component_dir
        elif analysis_type == 'training':
            save_dir = self.metrics_dir
        else:
            save_dir = self.additional_dir

        # Create filename and save
        filepath = save_dir / f"{analysis_type}_analysis_{timestamp}.txt"
        with open(filepath, 'w') as f:
            f.write(analysis_text)

        debug_print(f"Saved {analysis_type} analysis to {filepath}")

    def save_plot(self, figure, plot_type):
        """
        Save plot to appropriate directory.

        Args:
            figure (matplotlib.figure.Figure): The figure to save
            plot_type (str): Type of plot ('component', 'training', 'additional')
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Select appropriate directory based on plot type
        if plot_type == 'component':
            save_dir = self.component_dir
        elif plot_type == 'training':
            save_dir = self.metrics_dir
        else:
            save_dir = self.additional_dir

        # Create filename and save
        filepath = save_dir / f"{plot_type}_plot_{timestamp}.png"
        figure.savefig(filepath)

        debug_print(f"Saved {plot_type} plot to {filepath}")

    def save_checkpoint(self, model_state, episode):
        """
        Save model checkpoint.

        Args:
            model_state (dict): Model state dictionary
            episode (int): Current episode number
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.checkpoints_dir / f"checkpoint_episode_{episode}_{timestamp}.pth"
        torch.save(model_state, filepath)
        debug_print(f"Saved model checkpoint to {filepath}")

    def save_recommender(self, recommender_state, is_final=False):
        """
        Save recommender model.

        Args:
            recommender_state (dict): Recommender state dictionary
            is_final (bool): Whether this is the final model
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"final_recommender_{timestamp}.pth" if is_final else f"recommender_{timestamp}.pth"
        filepath = self.recommender_dir / filename
        torch.save(recommender_state, filepath)
        debug_print(f"Saved recommender model to {filepath}")

    def analyze_recommendation(self, event):
        """Analyze and print the component breakdown for a recommendation."""
        try:
            # Calculate reward and get components
            if isinstance(event, dict):
                event = pd.Series(event)

            # Add missing fields with default values
            if 'Date/Time' in event:
                event_time = pd.to_datetime(event['Date/Time'])
                if event_time.tz is None:
                    event_time = event_time.tz_localize('UTC')
                current_time = get_current_time()
                time_until_event = (event_time - current_time).total_seconds() / 3600.0
                event['Time Until Event (hrs)'] = time_until_event

            # Use environment's global stats for defaults
            required_fields = {
                'Time Until Event (hrs)': 0,
                'Price ($)': self.env.global_stats['price_stats']['mean'],
                'Distance (km)': self.env.global_stats['distance_stats']['mean'],
                'Popularity': self.env.global_stats['popularity_stats']['mean']
            }

            for field, default_value in required_fields.items():
                if field not in event:
                    event[field] = default_value

            # Calculate reward using environment's method
            self.env.calculate_reward(event)
            components = self.env.last_reward_components

            # Prepare analysis output
            analysis = []
            analysis.append("\nRecommendation Component Analysis:")
            analysis.append("==================================")

            # Raw scores
            analysis.append("\nRaw Scores (before weights):")
            for component, score in components['raw_scores'].items():
                analysis.append(f"{component:12}: {score:8.2f}")

            # Weighted contributions
            analysis.append("\nWeighted Contributions:")
            for component, score in components['weighted_scores'].items():
                weight = components['weights'][component]
                analysis.append(f"{component:12}: {score:8.2f} (weight: {weight:.2f})")

            # Calculate percentage contributions
            total_absolute = sum(abs(score) for score in components['weighted_scores'].values())
            if total_absolute > 0:
                analysis.append("\nRelative Impact:")
                for component, score in components['weighted_scores'].items():
                    impact = abs(score) / total_absolute * 100
                    analysis.append(f"{component:12}: {impact:8.2f}%")

            # Print to console
            for line in analysis:
                print(line)

            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analysis_path = (self.directories['analytics']['component_analysis'] /
                             f"analysis_{timestamp}.txt")
            with open(analysis_path, 'w') as f:
                f.write('\n'.join(analysis))

        except Exception as e:
            logging.error(f"Error in analyze_recommendation: {str(e)}")

    def setup_plotting_style(self):
        """Set up consistent plotting style."""
        sns.set_theme()
        sns.set_style("whitegrid")


    def add_recommendation(self, recommendation):
        self.history['recommendation_history'].append(recommendation)

    def plot_training_metrics(self):
        """Generate comprehensive training metrics plots."""
        if not self.history['rewards']:
            debug_print("No training data to plot")
            return

        # Convert all deques to lists at the start
        history_lists = {
            'rewards': list(self.history['rewards']),
            'losses': list(self.history['losses']),
            'epsilons': list(self.history['epsilons']),
            'actions_taken': list(self.history['actions_taken']),
            'episode_lengths': list(self.history['episode_lengths']),
            'q_values': list(self.history['q_values'])
        }

        timestamp = time.strftime('%Y%m%d_%H%M%S')

        with plot_context(figsize=(20, 15), subplots=True, nrows=3, ncols=2) as (fig, axes):
            fig.suptitle('Training Metrics Overview', fontsize=16)

            # Rewards plot
            ax = axes[0, 0]
            ax.plot(history_lists['rewards'], alpha=0.6, label='Episode Reward')
            ax.plot(pd.Series(history_lists['rewards']).rolling(10).mean(), label='10-Episode Average')
            ax.set_title('Training Rewards')
            ax.set_xlabel('Episode')
            ax.set_ylabel('Reward')
            ax.legend()

            # Loss plot
            ax = axes[0, 1]
            valid_losses = [l for l in history_lists['losses'] if l is not None]
            ax.plot(valid_losses, alpha=0.6)
            ax.plot(pd.Series(valid_losses).rolling(10).mean())
            ax.set_title('Training Loss')
            ax.set_xlabel('Episode')
            ax.set_ylabel('Loss')

            # Epsilon plot
            ax = axes[1, 0]
            ax.plot(history_lists['epsilons'])
            ax.set_title('Exploration Rate (Epsilon)')
            ax.set_xlabel('Episode')
            ax.set_ylabel('Epsilon')

            # Q-values distribution
            ax = axes[1, 1]
            ax.plot(self.q_value_summary['mean'], label='Mean')
            ax.fill_between(range(len(self.q_value_summary['mean'])),
                            np.array(self.q_value_summary['min']),
                            np.array(self.q_value_summary['max']),
                            alpha=0.2, label='Range')
            ax.plot(self.q_value_summary['std'], label='Std Dev')
            ax.set_title('Q-Values Evolution')
            ax.legend()

            # Action distribution
            ax = axes[2, 0]
            recent_actions = history_lists['actions_taken'][-1000:] if len(history_lists['actions_taken']) >= 1000 else \
            history_lists['actions_taken']
            sns.histplot(recent_actions, bins=50, ax=ax)
            ax.set_title('Action Distribution')

            # Episode lengths
            ax = axes[2, 1]
            ax.plot(history_lists['episode_lengths'])
            ax.set_title('Episode Lengths')
            ax.set_xlabel('Episode')
            ax.set_ylabel('Length')

            plt.tight_layout()
            plt.savefig(self.metrics_dir / f'training_metrics_{timestamp}.png')

    def generate_report(self):
        """Generate a text report with key metrics."""
        timestamp = time.strftime('%Y%m%d_%H%M%S')

        # Convert deques to lists and check for data
        rewards = list(self.history['rewards'])
        epsilons = list(self.history['epsilons'])
        episode_lengths = list(self.history['episode_lengths'])
        actions_taken = list(self.history['actions_taken'])

        # Calculate event statistics
        total_events_analyzed = sum(episode_lengths) if episode_lengths else 0
        unique_events = len(set(actions_taken)) if actions_taken else 0
        events_per_episode = total_events_analyzed / len(rewards) if rewards else 0

        report = [
            "=== DQL Event Recommender Training Report ===",
            f"Generated at: {timestamp}\n",
            "Training Metrics:"
        ]

        # Only add metrics if we have data
        if rewards:
            report.extend([
                f"Total Episodes: {len(rewards)}",
                f"Average Reward: {np.mean(rewards):.2f}",
                f"Best Reward: {max(rewards):.2f}"
            ])

        if epsilons:
            report.append(f"Final Epsilon: {epsilons[-1]:.4f}")

        if episode_lengths:
            report.append(f"Average Episode Length: {np.mean(episode_lengths):.1f}")

        # Add event analysis statistics
        report.extend([
            f"Total Events Analyzed: {total_events_analyzed}",
            f"Unique Events Recommended: {unique_events}",
            f"Events Per Episode: {events_per_episode:.1f}\n"
        ])

        if hasattr(self, 'q_value_summary') and all(self.q_value_summary.values()):
            report.extend([
                "\nQ-Value Statistics:",
                f"Mean Q-Value: {np.mean(self.q_value_summary['mean']):.2f}",
                f"Max Q-Value: {max(self.q_value_summary['max']):.2f}",
                f"Min Q-Value: {min(self.q_value_summary['min']):.2f}"
            ])

        if actions_taken:
            report.extend([
                "\nAction Statistics:",
                f"Unique Actions Taken: {len(set(actions_taken))}"
            ])

        # Add component summary if available and non-empty
        if self.history['reward_components'] and any(
                len(values) > 0 for values in self.history['reward_components'].values()):
            report.append("\nReward Component Summary:")
            for key, values in self.history['reward_components'].items():
                if values:  # Check if deque is not empty
                    values_list = list(values)
                    if values_list:  # Double check after conversion
                        report.append(f"{key}: avg={np.mean(values_list):.2f}")

        # Add DQL Performance section
        if self.dql_metrics['loss'] and self.dql_metrics['q_values']['mean']:
            report.extend([
                "\nDQL Performance Metrics:",
                f"Average Loss: {np.mean(list(self.dql_metrics['loss'])):.4f}",
                f"Q-Value Evolution:",
                f"  - Mean: {np.mean(list(self.dql_metrics['q_values']['mean'])):.4f}",
                f"  - Max: {np.mean(list(self.dql_metrics['q_values']['max'])):.4f}",
                f"  - Min: {np.mean(list(self.dql_metrics['q_values']['min'])):.4f}",
                f"  - Stability (StdDev): {np.mean(list(self.dql_metrics['q_values']['std'])):.4f}",
                f"Action Distribution Entropy: {self.calculate_action_entropy():.4f}\n"
            ])
        # Save to additional_analysis directory
        report_path = self.additional_dir / f'training_report_{timestamp}.txt'
        with open(report_path, 'w') as f:
            f.write('\n'.join(report))

        debug_print(f"Training report saved to {report_path}")

    def calculate_action_entropy(self):
        """Calculate entropy of action distribution."""
        if not self.dql_metrics['action_distributions']:
            return 0.0
        counts = np.array(list(self.dql_metrics['action_distributions'].values()))
        probs = counts / counts.sum()
        return -np.sum(probs * np.log(probs + 1e-10))

    def analyze_problematic_rewards(self):
        """Analyze and visualize the most problematic reward components."""
        if not any(self.history['reward_components'].values()):
            debug_print("No reward components to analyze")
            return
        timestamp = time.strftime('%Y%m%d_%H%M%S')

        # Calculate statistics for each component
        component_stats = {}
        for key in self.history['reward_components']:
            if self.history['reward_components'][key]:
                values = np.array(self.history['reward_components'][key])
                component_stats[key] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'negative_ratio': np.sum(values < 0) / len(values),
                    'variance': np.var(values)
                }

        if not component_stats:
            debug_print("No component statistics available")
            return

        # Plot problematic components
        fig, axes = plt.subplots(2, 2, figsize=(20, 15))
        fig.suptitle('Problematic Reward Components Analysis', fontsize=16)

        # 1. Negative rewards distribution
        ax = axes[0, 0]
        negative_ratios = [stats['negative_ratio'] for stats in component_stats.values()]
        ax.bar(np.arange(len(component_stats)), negative_ratios)
        ax.set_title('Proportion of Negative Rewards')
        ax.set_xticks(np.arange(len(component_stats)), list(component_stats.keys()), rotation=45, ha='right')

        # 2. Reward volatility
        ax = axes[0, 1]
        volatility = [stats['std'] for stats in component_stats.values()]
        ax.bar(np.arange(len(component_stats)), volatility)
        ax.set_title('Reward Volatility (Standard Deviation)')
        ax.set_xticks(np.arange(len(component_stats)), list(component_stats.keys()), rotation=45, ha='right')

        # 3. Reward ranges
        ax = axes[1, 0]
        for key in component_stats:
            ax.boxplot(self.history['reward_components'][key], positions=[list(component_stats.keys()).index(key)])
        ax.set_title('Reward Ranges by Component')
        ax.set_xticks(np.arange(len(component_stats)), list(component_stats.keys()), rotation=45, ha='right')

        # 4. Worst offenders summary
        ax = axes[1, 1]
        ax.axis('off')
        summary_text = "Worst Performing Components:\n\n"

        # Sort components by various metrics
        by_negativity = sorted(component_stats.items(), key=lambda x: x[1]['negative_ratio'], reverse=True)
        by_volatility = sorted(component_stats.items(), key=lambda x: x[1]['std'], reverse=True)

        summary_text += "Most Negative Components:\n"
        for key, stats in by_negativity[:3]:
            summary_text += f"{key}: {stats['negative_ratio'] * 100:.1f}% negative\n"

        summary_text += "\nMost Volatile Components:\n"
        for key, stats in by_volatility[:3]:
            summary_text += f"{key}: std={stats['std']:.2f}\n"

        ax.text(0.1, 0.1, summary_text, fontsize=12, verticalalignment='top')

        plt.tight_layout()
        plt.savefig(self.reward_folder / f'problematic_rewards_{timestamp}.png')
        plt.close()

    def analyze_reward_components(self):
        """Analyze the contribution of different components to the final reward."""
        if not any(self.history['reward_components'].values()):
            debug_print("No reward component data to analyze")
            return

        timestamp = time.strftime('%Y%m%d_%H%M%S')

        # Get the component names from the dictionary keys
        component_names = list(self.history['reward_components'].keys())

        with plot_context(figsize=(20, 15), subplots=True, nrows=2, ncols=2) as (fig, axes):
            # Component Contributions Over Time
            ax = axes[0, 0]
            for component in component_names:
                values = list(self.history['reward_components'][component])
                ax.plot(values, label=component, alpha=0.7)
            ax.set_title('Reward Components Over Time')
            ax.set_xlabel('Recommendation')
            ax.set_ylabel('Component Value')
            ax.legend()

            # Average Component Contribution
            ax = axes[0, 1]
            avg_contributions = {
                component: np.mean(list(self.history['reward_components'][component]))
                for component in component_names
            }
            bars = ax.bar(np.arange(len(avg_contributions)), list(avg_contributions.values()))
            ax.set_title('Average Component Contributions')
            ax.set_xlabel('Component')
            ax.set_ylabel('Average Value')
            ax.set_xticks(np.arange(len(component_names)), component_names, rotation=45, ha='right')

            # Component Distribution
            ax = axes[1, 0]
            component_data = []
            for component in component_names:
                values = list(self.history['reward_components'][component])
                component_data.extend([(component, value) for value in values])
            df = pd.DataFrame(component_data, columns=['Component', 'Value'])
            sns.boxplot(x='Component', y='Value', data=df, ax=ax)
            ax.set_title('Distribution of Component Values')
            ax.set_xticks(np.arange(len(component_names)), component_names, rotation=45, ha='right')

            # Correlation Matrix - Replace seaborn heatmap with matplotlib
            ax = axes[1, 1]
            correlation_data = pd.DataFrame({
                component: list(self.history['reward_components'][component])
                for component in component_names
            })
            corr_matrix = correlation_data.corr().values

            # Create the heatmap manually
            im = ax.imshow(corr_matrix, cmap='coolwarm', vmin=-1, vmax=1)

            # Add colorbar
            plt.colorbar(im, ax=ax)

            # Add annotations
            for i in range(len(component_names)):
                for j in range(len(component_names)):
                    text = f'{corr_matrix[i, j]:.2f}'
                    ax.text(j, i, text, ha='center', va='center')

            # Set ticks and labels
            ax.set_xticks(np.arange(len(component_names)))
            ax.set_yticks(np.arange(len(component_names)))
            ax.set_xticklabels(component_names)
            ax.set_yticklabels(component_names)

            # Rotate x labels
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            ax.set_title('Component Correlation Matrix')

            plt.tight_layout()
            plt.savefig(self.component_dir / f'reward_analysis_{timestamp}.png')
        # Generate and display the pie chart for component impact
        self.plot_component_impact_pie_chart()

    def add_episode_data(self, reward, loss, epsilon, q_values, actions, episode_length, reward_components=None):
        """Add episode data to history."""
        try:
            # Ensure all required keys exist
            required_keys = ['rewards', 'losses', 'epsilons', 'episode_lengths',
                             'q_values', 'actions', 'actions_taken']

            for key in required_keys:
                if key not in self.history:
                    self.history[key] = deque(maxlen=10000)

            # Add the data
            self.history['rewards'].append(reward)
            self.history['losses'].append(loss)
            self.history['epsilons'].append(epsilon)
            self.history['episode_lengths'].append(episode_length)

            # Handle q_values (take mean if it's a list/array)
            if isinstance(q_values, (list, np.ndarray)):
                self.history['q_values'].append(np.mean(q_values))
            else:
                self.history['q_values'].append(q_values)

            # Handle actions
            if isinstance(actions, (list, np.ndarray)):
                self.history['actions'].extend(actions)
                self.history['actions_taken'].extend(actions)
            else:
                self.history['actions'].append(actions)
                self.history['actions_taken'].append(actions)

            # Handle reward components
            if reward_components:
                for component, value in reward_components.items():
                    if component not in self.history['reward_components']:
                        self.history['reward_components'][component] = deque(maxlen=10000)
                    self.history['reward_components'][component].append(value)

        except Exception as e:
            debug_print(f"Error in add_episode_data: {str(e)}")
            raise

    def track_user_interaction(self, event_id, interaction_data):
        """
        Track user interaction metrics.
        From: user_simulator.py
        """
        # Basic interactions
        if interaction_data.get('viewed', False):
            self.interaction_metrics['views'].append(event_id)
        if interaction_data.get('clicked', False):
            self.interaction_metrics['clicks'].append(event_id)
        if interaction_data.get('bookmarked', False):
            self.interaction_metrics['bookmarks'].append(event_id)
        if interaction_data.get('purchased', False):
            self.interaction_metrics['purchases'].append(event_id)

        # Time spent
        if 'time_spent' in interaction_data:
            self.interaction_metrics['time_spent'].append(interaction_data['time_spent'])


    def generate_recommendation_analysis(self, recommendation_data):
        """Helper method to generate recommendation analysis text."""
        analysis = [
            "\nRecommendation Analysis:",
            "=" * 50,
            f"Timestamp: {recommendation_data['timestamp']}",
            f"Event ID: {recommendation_data['event_id']}",
            f"Event Type: {recommendation_data['event_type']}",
            f"Price: ${recommendation_data['price']:.2f}",
            f"Distance: {recommendation_data['distance']:.2f} km",
            f"Popularity: {recommendation_data['popularity']}"
        ]

        if 'reward_components' in recommendation_data:
            analysis.extend([
                "\nReward Components:",
                "-" * 30
            ])
            for component, value in recommendation_data['reward_components'].items():
                analysis.append(f"{component}: {value:.3f}")

        return "\n".join(analysis)

    def visualize_results(self, recommendations, total_reward):
        """
        Moved from main.py - Visualize recommendation results.
        Now uses proper directory structure for saving plots.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Plot rewards distribution
            with plot_context(figsize=(10, 6)) as (fig, ax):
                rewards = [r['Reward'] for r in recommendations]
                plt.hist(rewards, bins=20)
                plt.title('Distribution of Rewards')
                plt.xlabel('Reward')
                plt.ylabel('Count')
                self.save_plot(plt.gcf(), 'rewards_distribution')

            # Plot event type distribution
            with plot_context(figsize=(12, 6)) as (fig, ax):
                event_types = [r['Event Type'] for r in recommendations]
                pd.Series(event_types).value_counts().plot(kind='bar')
                plt.title('Distribution of Recommended Event Types')
                plt.xlabel('Event Type')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.tight_layout()
                self.save_plot(plt.gcf(), 'event_distribution')

        except Exception as e:
            logging.error(f"Error during visualization: {str(e)}")
            raise

    def track_environment_state(self, state_data, action, reward, done):
        """
        Track environment state transitions and metrics.

        Args:
            state_data (dict): Current state information
            action (int): Action taken
            reward (float): Reward received
            done (bool): Whether episode is done
        """
        try:
            # Track state transitions
            self.history['state_transitions'].append({
                'state': state_data,
                'action': action,
                'reward': reward,
                'done': done,
                'timestamp': time.time()
            })

            # Track state features
            if 'features' in state_data:
                for feature, value in state_data['features'].items():
                    if feature not in self.history['feature_distributions']:
                        self.history['feature_distributions'][feature] = deque(maxlen=10000)
                    self.history['feature_distributions'][feature].append(value)

            # Track reward distribution
            self.history['reward_distribution'].append(reward)

            # Save periodic state analysis
            if len(self.history['state_transitions']) % 1000 == 0:
                self.analyze_environment_metrics()

        except Exception as e:
            logging.error(f"Error tracking environment state: {str(e)}")

    def analyze_environment_metrics(self):
        """Analyze and visualize environment metrics."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create visualization
            with plot_context(figsize=(20, 15)) as (fig, axes):
                fig.suptitle('Environment Analysis', fontsize=16)

                # Plot feature distributions
                for i, (feature, values) in enumerate(self.history['feature_distributions'].items()):
                    ax = plt.subplot(3, 2, i + 1)
                    sns.histplot(data=list(values), ax=ax)
                    ax.set_title(f'{feature} Distribution')

                # Plot reward distribution
                ax = plt.subplot(3, 2, 5)
                sns.histplot(data=self.history['reward_distribution'])
                ax.set_title('Reward Distribution')

                # Plot state transition patterns
                ax = plt.subplot(3, 2, 6)
                transitions = pd.DataFrame(self.history['state_transitions'])
                if not transitions.empty:
                    sns.scatterplot(data=transitions, x='timestamp', y='reward')
                ax.set_title('Reward Over Time')

                plt.tight_layout()
                self.save_plot(plt.gcf(), 'environment_analysis')

            # Generate text analysis
            analysis_text = self._generate_environment_analysis()
            self.save_analysis(analysis_text, 'environment')

        except Exception as e:
            logging.error(f"Error analyzing environment metrics: {str(e)}")

    def _generate_environment_analysis(self):
        """Generate text analysis of environment metrics."""
        analysis = ["Environment Metrics Analysis", "=" * 30, ""]

        # Analyze reward distribution
        rewards = self.history['reward_distribution']
        analysis.extend([
            "Reward Statistics:",
            f"Mean Reward: {np.mean(rewards):.3f}",
            f"Std Dev: {np.std(rewards):.3f}",
            f"Min: {min(rewards):.3f}",
            f"Max: {max(rewards):.3f}",
            ""
        ])

        # Analyze feature distributions
        analysis.append("Feature Statistics:")
        for feature, values in self.history['feature_distributions'].items():
            values_list = list(values)
            analysis.extend([
                f"\n{feature}:",
                f"Mean: {np.mean(values_list):.3f}",
                f"Std Dev: {np.std(values_list):.3f}",
                f"Range: [{min(values_list):.3f}, {max(values_list):.3f}]"
            ])

        return "\n".join(analysis)

    def track_reward_calculation(self, event, reward_info):
        """
        Track detailed reward calculations and components.

        Args:
            event (pd.Series): Event that was recommended
            reward_info (dict): Dictionary containing:
                - total (float): Total reward
                - components (dict): Individual reward components
                - weights (dict): Component weights used
        """
        try:
            debug_print(f"Tracking reward calculation:")
            debug_print(f"Event: {event['Event ID']}")
            debug_print(f"Reward info: {reward_info}")

            # Track component distributions
            components = reward_info.get('components', {})
            debug_print(f"Components to track: {components}")

            for component_name, value in components.items():
                if component_name not in self.history['reward_components']:
                    debug_print(f"Creating new component tracker for: {component_name}")
                    self.history['reward_components'][component_name] = deque(maxlen=10000)
                self.history['reward_components'][component_name].append(float(value))
                debug_print(f"Stored {component_name}: {value}")

            # Verify storage
            debug_print("Current component history:")
            for comp, values in self.history['reward_components'].items():
                debug_print(f"{comp}: {len(values)} values stored")

        except Exception as e:
            logging.error(f"Error tracking reward calculation: {str(e)}")
            logging.error(f"Event: {event}")
            logging.error(f"Reward info: {reward_info}")

    def analyze_reward_patterns(self):
        """Analyze patterns in reward calculations."""
        try:
            # Convert reward components to DataFrame for analysis
            component_data = {
                component: list(values)
                for component, values in self.history['reward_components'].items()
            }
            df = pd.DataFrame(component_data)

            # Generate visualizations
            with plot_context(figsize=(20, 15)) as (fig, axes):
                fig.suptitle('Reward Analysis', fontsize=16)

                # Component contribution over time
                ax = plt.subplot(3, 2, 1)
                for component in self.history['reward_components']:
                    values = list(self.history['reward_components'][component])
                    plt.plot(values[-1000:], label=component)  # Last 1000 values for clarity
                ax.set_title('Component Contributions Over Time')
                ax.legend()

                # Component distributions
                ax = plt.subplot(3, 2, 2)
                component_means = {
                    comp: np.mean(list(values))
                    for comp, values in self.history['reward_components'].items()
                }
                plt.bar(component_means.keys(), component_means.values())
                ax.set_title('Average Component Contributions')
                plt.xticks(rotation=45)

                # Save plot
                self.save_plot(plt.gcf(), 'reward_analysis')

            # Generate text analysis
            analysis_text = self._generate_reward_analysis(df)
            self.save_analysis(analysis_text, 'reward')

        except Exception as e:
            logging.error(f"Error analyzing reward patterns: {str(e)}")

    def _generate_reward_analysis(self, df):
        """Generate text analysis of reward patterns."""
        analysis = ["Reward System Analysis", "=" * 30, ""]

        # Overall statistics
        analysis.extend([
            "Overall Reward Statistics:",
            f"Mean Total Reward: {df['total_reward'].mean():.3f}",
            f"Std Dev: {df['total_reward'].std():.3f}",
            f"Min: {df['total_reward'].min():.3f}",
            f"Max: {df['total_reward'].max():.3f}",
            ""
        ])

        # Component analysis
        analysis.append("Component Statistics:")
        for component in self.history['reward_components']:
            values = list(self.history['reward_components'][component])
            analysis.extend([
                f"\n{component}:",
                f"Mean: {np.mean(values):.3f}",
                f"Std Dev: {np.std(values):.3f}",
                f"Range: [{min(values):.3f}, {max(values):.3f}]"
            ])

        return "\n".join(analysis)

    def track_user_simulation(self, event, interaction_data, preference_data=None):
        """
        Track user simulation metrics and interactions.

        Args:
            event (pd.Series): The event being interacted with
            interaction_data (dict): User interaction results
            preference_data (dict, optional): Changes in user preferences
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Track basic interactions
            for interaction_type in ['viewed', 'clicked', 'bookmarked', 'purchased']:
                if interaction_data.get(interaction_type, False):
                    self.user_simulation_metrics['interactions'][interaction_type].append({
                        'timestamp': timestamp,
                        'event_id': event['Event ID'],
                        'event_type': event['Event Type']
                    })

            # Track time spent
            if 'time_spent' in interaction_data:
                self.user_simulation_metrics['interactions']['time_spent'].append({
                    'timestamp': timestamp,
                    'event_id': event['Event ID'],
                })

            # Track preference changes if provided
            if preference_data:
                self.user_simulation_metrics['preference_changes'].append({
                    'timestamp': timestamp,
                    'changes': preference_data
                })

            # Track interaction patterns by event type
            event_type = event['Event Type']
            for interaction_type, occurred in interaction_data.items():
                if occurred and interaction_type != 'time_spent':
                    self.user_simulation_metrics['interaction_patterns'][event_type][interaction_type] += 1

            # Periodic analysis
            if len(self.user_simulation_metrics['interactions']['views']) % 1000 == 0:
                self.analyze_user_behavior()

        except Exception as e:
            logging.error(f"Error tracking user simulation: {str(e)}")

    def generate_user_behavior_analysis(self):
        """Generate text analysis of user behavior patterns."""
        analysis = ["User Behavior Analysis", "=" * 30, ""]

        # Interaction statistics
        for interaction_type in ['views', 'clicks', 'bookmarks', 'purchases']:
            count = len(self.user_simulation_metrics['interactions'][interaction_type])
            analysis.append(f"{interaction_type.capitalize()}: {count}")

        # Time spent statistics
        #NEEDS TO BE IMPLEMENTED

        return "\n".join(analysis)

    def analyze_user_behavior(self):
        """Analyze and visualize user behavior patterns."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            with plot_context(figsize=(20, 15)) as (fig, axes):
                fig.suptitle('User Behavior Analysis', fontsize=16)

                # Interaction rates over time
                ax = plt.subplot(3, 2, 1)
                for interaction_type in ['clicks', 'bookmarks', 'purchases']:
                    rates = [len(self.user_simulation_metrics['interactions'][interaction_type]) /
                             max(1, len(self.user_simulation_metrics['interactions']['views']))]
                    plt.plot(rates, label=f'{interaction_type} rate')
                ax.set_title('Interaction Rates')
                ax.legend()

                # Event type preferences
                ax = plt.subplot(3, 2, 3)
                pattern_df = pd.DataFrame(self.user_simulation_metrics['interaction_patterns'])
                sns.heatmap(pattern_df, ax=ax)
                ax.set_title('Event Type Interaction Patterns')

                self.save_plot(plt.gcf(), 'user_behavior')

            # Generate text analysis
            analysis_text = self.generate_user_behavior_analysis()
            self.save_analysis(analysis_text, 'user_behavior')

        except Exception as e:
            logging.error(f"Error analyzing user behavior: {str(e)}")

    def track_dql_training(self, q_values, online_q, target_q, loss=None, gradients=None, network_state=None,
                           action_taken=None):
        """Track DQL network training metrics including both online and target Q-values."""
        try:
            # Initialize DDQN metrics if they don't exist
            if not hasattr(self, 'ddqn_metrics'):
                debug_print("Initializing DDQN metrics tracking")
                self.ddqn_metrics = {
                    'online_q_values': deque(maxlen=10000),
                    'target_q_values': deque(maxlen=10000),
                    'q_value_diff': deque(maxlen=10000)
                }

            # Convert q_values to numpy if it's a tensor
            if torch.is_tensor(q_values):
                q_values_np = q_values.detach().cpu().numpy()
            else:
                q_values_np = q_values

            # Track Q-value statistics
            current_stats = {
                'mean': np.mean(q_values_np),
                'max': np.max(q_values_np),
                'min': np.min(q_values_np),
                'std': np.std(q_values_np)
            }

            debug_print(f"Current Q-value stats: Mean={current_stats['mean']:.4f}, "
                        f"Max={current_stats['max']:.4f}, Min={current_stats['min']:.4f}")

            # Store Q-values and track differences
            self.ddqn_metrics['online_q_values'].append(online_q)
            self.ddqn_metrics['target_q_values'].append(target_q)
            q_diff = abs(online_q - target_q)
            self.ddqn_metrics['q_value_diff'].append(q_diff)

            debug_print(f"Q-value difference: {q_diff:.4f}")

            # Track loss if provided
            if loss is not None:
                if not hasattr(self.dql_metrics, 'loss'):
                    self.dql_metrics['loss'] = deque(maxlen=10000)
                self.dql_metrics['loss'].append(loss)
                debug_print(f"Current loss: {loss:.4f}")

            # Track action distribution
            if action_taken is not None:
                if not hasattr(self.dql_metrics, 'action_distributions'):
                    self.dql_metrics['action_distributions'] = defaultdict(int)
                self.dql_metrics['action_distributions'][action_taken] += 1

            # Periodic statistics logging
            if len(self.ddqn_metrics['online_q_values']) % 1000 == 0:
                info_print("\nDDQN Training Statistics:")
                info_print(f"Average Online Q-Value: {np.mean(list(self.ddqn_metrics['online_q_values'])):.4f}")
                info_print(f"Average Target Q-Value: {np.mean(list(self.ddqn_metrics['target_q_values'])):.4f}")
                info_print(f"Average Q-Value Difference: {np.mean(list(self.ddqn_metrics['q_value_diff'])):.4f}")
                if loss is not None:
                    info_print(f"Recent Average Loss: {np.mean(list(self.dql_metrics['loss'])[-1000:]):.4f}")

        except Exception as e:
            logging.error(f"Error in track_dql_training: {str(e)}")
            logging.error(f"Q-values shape: {q_values.shape if hasattr(q_values, 'shape') else 'no shape'}")
            logging.error(f"Online Q type: {type(online_q)}")
            logging.error(f"Target Q type: {type(target_q)}")

    def analyze_dql_performance(self):
        """Analyze and visualize DQL network performance."""
        try:
            debug_print("Starting DQL performance analysis")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            debug_print(f"Creating plots with timestamp: {timestamp}")
            debug_print(f"Q-values mean length: {len(self.dql_metrics['q_values']['mean'])}")
            debug_print(f"Loss length: {len(self.dql_metrics['loss'])}")
            if hasattr(self, 'ddqn_metrics'):
                debug_print(f"DDQN metrics lengths - Online: {len(self.ddqn_metrics['online_q_values'])}, "
                            f"Target: {len(self.ddqn_metrics['target_q_values'])}")

            # Create plots with proper subplot configuration
            with plot_context(figsize=(20, 15), subplots=True, nrows=3, ncols=2) as (fig, axes):
                fig.suptitle('DQL Network Analysis', fontsize=16)

                # Q-value evolution plot
                ax = axes[0, 0]
                ax.plot(list(self.dql_metrics['q_values']['mean']), label='Mean Q')
                ax.fill_between(
                    range(len(self.dql_metrics['q_values']['mean'])),
                    list(self.dql_metrics['q_values']['min']),
                    list(self.dql_metrics['q_values']['max']),
                    alpha=0.2
                )
                ax.set_title('Q-Value Evolution')
                ax.legend()

                # Loss curve
                ax = axes[0, 1]
                ax.plot(list(self.dql_metrics['loss']))
                ax.set_title('Training Loss')

                # DDQN specific plots
                if hasattr(self, 'ddqn_metrics'):
                    ax = axes[1, 0]
                    ax.plot(list(self.ddqn_metrics['online_q_values']), label='Online Q-Values')
                    ax.plot(list(self.ddqn_metrics['target_q_values']), label='Target Q-Values')
                    ax.set_title('DDQN Q-Values Comparison')
                    ax.legend()

                    ax = axes[1, 1]
                    ax.plot(list(self.ddqn_metrics['q_value_diff']), label='Q-Value Difference')
                    ax.set_title('Q-Value Network Difference')
                    ax.legend()

                # Save the plot
                plot_path = self.metrics_dir / f'dql_analysis_{timestamp}.png'
                debug_print(f"Attempting to save DQL analysis plot to: {plot_path}")
                plt.savefig(plot_path)
                debug_print(f"Successfully saved DQL analysis plot")

                # Print analysis to console
                info_print("\n=== DQL Performance Analysis ===")
                info_print(f"Analysis timestamp: {timestamp}")

                # Q-value statistics
                mean_q = np.mean(list(self.dql_metrics['q_values']['mean']))
                max_q = np.max(list(self.dql_metrics['q_values']['max']))
                min_q = np.min(list(self.dql_metrics['q_values']['min']))

                info_print(f"\nQ-Value Statistics:")
                info_print(f"Mean Q-Value: {mean_q:.4f}")
                info_print(f"Max Q-Value: {max_q:.4f}")
                info_print(f"Min Q-Value: {min_q:.4f}")

                # DDQN specific statistics
                if hasattr(self, 'ddqn_metrics'):
                    online_mean = np.mean(list(self.ddqn_metrics['online_q_values']))
                    target_mean = np.mean(list(self.ddqn_metrics['target_q_values']))
                    diff_mean = np.mean(list(self.ddqn_metrics['q_value_diff']))

                    info_print("\nDDQN Statistics:")
                    info_print(f"Online Network Mean: {online_mean:.4f}")
                    info_print(f"Target Network Mean: {target_mean:.4f}")
                    info_print(f"Mean Q-Value Difference: {diff_mean:.4f}")

                info_print(f"\nPlot saved to: {plot_path}")

        except Exception as e:
            logging.error(f"Error analyzing DQL performance: {str(e)}")
            debug_print(f"Full error: {traceback.format_exc()}")

    def _generate_dql_analysis(self):
        """Generate text analysis of DQL network performance metrics."""
        analysis = ["DQL Network Performance Analysis", "=" * 30, ""]

        # Q-value analysis
        q_values = self.dql_metrics['q_values']
        analysis.extend([
            "Q-Value Statistics:",
            f"Mean Q-Value: {np.mean(list(q_values['mean'])):.3f}",
            f"Max Q-Value: {np.max(list(q_values['max'])):.3f}",
            f"Min Q-Value: {np.min(list(q_values['min'])):.3f}",
            f"Average Std Dev: {np.mean(list(q_values['std'])):.3f}",
            ""
        ])

        # Loss analysis
        if self.dql_metrics['loss']:
            losses = list(self.dql_metrics['loss'])
            analysis.extend([
                "Training Loss:",
                f"Current Loss: {losses[-1]:.3f}",
                f"Average Loss: {np.mean(losses):.3f}",
                f"Loss Trend: {'Decreasing' if losses[-1] < np.mean(losses[:10]) else 'Increasing or Stable'}",
                ""
            ])

        # Gradient analysis
        if self.dql_metrics['gradients']:
            analysis.append("Gradient Statistics:")
            for layer_name, grads in self.dql_metrics['gradients'].items():
                grad_values = list(grads)
                analysis.extend([
                    f"\n{layer_name}:",
                    f"Mean Gradient: {np.mean(grad_values):.3f}",
                    f"Max Gradient: {np.max(grad_values):.3f}"
                ])
            analysis.append("")

        # Action distribution analysis
        total_actions = sum(self.dql_metrics['action_distributions'].values())
        if total_actions > 0:
            analysis.append("Action Distribution:")
            for action, count in self.dql_metrics['action_distributions'].items():
                percentage = (count / total_actions) * 100
                analysis.append(f"Action {action}: {percentage:.1f}%")

        return "\n".join(analysis)

    def plot_component_impact_pie_chart(self):
        """Plot and save a pie chart of component impact."""

        # Calculate total reward
        total_reward = sum(self.history['rewards'])

        # Calculate weights based on summed rewards for each component
        weights = {
            component: sum(rewards) / total_reward
            for component, rewards in self.history['reward_components'].items()
        }

        # Calculate percentage contributions using weights
        percentage_contributions = {
            component: weight * 100 for component, weight in weights.items()
        }

        # Filter out components with zero contribution
        percentage_contributions = {k: v for k, v in percentage_contributions.items() if v > 0}

        if not percentage_contributions:
            debug_print("No positive contributions to plot in pie chart.")
            return

        # Plot pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(
            percentage_contributions.values(),
            labels=list(percentage_contributions.keys()),  # Convert keys to list
            autopct='%1.1f%%'
        )
        plt.title('Component Impact on Rewards')

        # Save the plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = self.component_dir / f'component_impact_{timestamp}.png'
        plt.savefig(save_path)
        plt.close()  # Close the plot to free up memory

        debug_print(f"Saved component impact pie chart to {save_path}")




