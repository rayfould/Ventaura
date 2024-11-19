"""
main.py
Main script for running the event recommendation system.
"""

from config import *
from datetime import datetime
import json
from DQL import QNetwork
from epsilon_greedy import EpsilonGreedyPolicy
from Event_Ranking_Environment import EventRecommendationEnv
from improved_recommender import ImprovedEventRecommenderDQN
from user_simulator import HybridRewardSystem
from training_analytics import *
from DQL_Test import EventTester


def load_data():
    """Load and prepare event and user data."""
    try:
        events_df = pd.read_csv(EVENTS_CSV_PATH)
        users_df = pd.read_csv(USERS_CSV_PATH)

        # Clean Event Type column
        events_df['Event Type'] = events_df['Event Type'].fillna('Unknown')
        events_df['Event Type'] = events_df['Event Type'].astype(str)

        # Convert preferred and undesirable events to lists
        users_df['Preferred Events'] = users_df['Preferred Events'].apply(
            lambda x: [e.strip() for e in str(x).split(',')] if pd.notna(x) else []
        )
        users_df['Undesirable Events'] = users_df['Undesirable Events'].apply(
            lambda x: [e.strip() for e in str(x).split(',')] if pd.notna(x) else []
        )

        # Convert Date/Time to datetime and create timestamp
        events_df['Date/Time'] = pd.to_datetime(events_df['Date/Time'], errors='coerce')
        events_df['timestamp'] = events_df['Date/Time'].astype(np.int64) // 10**9

        # Handle any NaT values by setting a fallback
        fallback_time = get_current_time() + pd.Timedelta(days=7)
        events_df['Date/Time'] = events_df['Date/Time'].fillna(fallback_time)
        events_df['timestamp'] = events_df['timestamp'].fillna(int(fallback_time.timestamp()))

        # Clean numeric columns
        events_df['Price ($)'] = pd.to_numeric(events_df['Price ($)'], errors='coerce')
        events_df['Distance (km)'] = pd.to_numeric(events_df['Distance (km)'], errors='coerce')
        events_df['Popularity'] = pd.to_numeric(events_df['Popularity'], errors='coerce')

        # Fill NaN values with appropriate defaults
        events_df['Price ($)'] = events_df['Price ($)'].fillna(0)
        events_df['Distance (km)'] = events_df['Distance (km)'].fillna(events_df['Distance (km)'].mean())
        events_df['Popularity'] = events_df['Popularity'].fillna(50)  # Middle value

        # Standardize crowd size values
        users_df['Preferred Crowd Size'] = users_df['Preferred Crowd Size'].str.upper()

        debug_print(f"Loaded {len(events_df)} events and {len(users_df)} users")
        return events_df, users_df
    except Exception as e:
        logging.error(f"Error loading data: {str(e)}")
        raise


def train_recommender(recommender, num_episodes):
    """Train the recommendation system."""
    try:
        info_print("Starting training...")


        # Initialize analytics if not already done
        if not hasattr(recommender, 'analytics') or recommender.analytics is None:
            debug_print("Initializing analytics object...")
            # Use your existing TrainingAnalytics initialization
            recommender.analytics = TrainingAnalytics()

        # Train and get analytics
        analytics = recommender.train(num_episodes)

        # Process reward components after training
        debug_print("\nProcessing final reward components analysis...")
        if hasattr(recommender, 'analytics'):
            debug_print("Component statistics:")
            for component, values in recommender.analytics.history['reward_components'].items():
                if values:
                    values_list = list(values)
                    debug_print(f"\n{component}:")
                    debug_print(f"Count: {len(values_list)}")
                    debug_print(f"Mean: {np.mean(values_list):.4f}")
                    debug_print(f"Min: {min(values_list):.4f}")
                    debug_print(f"Max: {max(values_list):.4f}")

            # Generate final analytics
            info_print("About to generate final analytics")
            recommender.analytics.analyze_reward_components()

        # Convert deque to list for calculations
        rewards = list(analytics.history['rewards'])
        recent_rewards = rewards[-100:] if len(rewards) >= 100 else rewards

        info_print("\nTraining Summary:")
        info_print("=" * 50)
        info_print(f"Total Episodes: {num_episodes}")
        info_print(f"Final Average Reward (last 100 episodes): {np.mean(recent_rewards):.2f}")
        info_print(f"Best Episode Reward: {max(rewards):.2f}")
        info_print(f"Final Epsilon: {analytics.history['epsilons'][-1]:.4f}")
        info_print(f"Total Steps: {sum(analytics.history['episode_lengths'])}")

        # Save final analytics
        if hasattr(recommender, 'analytics'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            analytics_path = recommender.analytics.additional_dir / f"training_summary_{timestamp}.txt"
            debug_print(f"Saving training summary to: {str(analytics_path)}")

            with open(analytics_path, 'w') as f:
                f.write("Reward Component Analysis\n")
                f.write("=" * 50 + "\n\n")

                for component, values in recommender.analytics.history['reward_components'].items():
                    if values:  # Check if there are values
                        values_list = list(values)
                        if len(values_list) > 0:  # Additional check
                            f.write(f"{component} Statistics:\n")
                            f.write(f"Count: {len(values_list)}\n")
                            if np.any(values_list):  # Check if any non-zero values
                                f.write(f"Mean: {np.mean(values_list):.4f}\n")
                                f.write(f"Min: {np.min(values_list):.4f}\n")
                                f.write(f"Max: {np.max(values_list):.4f}\n")
                            else:
                                f.write("All values are zero\n")
                            f.write("\n")

        return analytics

    except Exception as e:
        logging.error(f"Training failed with error: {str(e)}")
        info_print(f"Training failed with error: {str(e)}")
        traceback.print_exc()  # Print full traceback for debugging
        raise


def evaluate_recommender(recommender, events_df, user):
    """Evaluate the trained recommender system."""
    try:
        total_reward = 0
        state = recommender.env.reset()
        done = False
        recommendations = []

        while not done:
            action = recommender.select_action(state)
            event = events_df.iloc[action]
            reward = recommender.get_reward(event, state)

            recommendations.append({
                'Event ID': event['Event ID'],
                'Event Type': event['Event Type'],
                'Reward': reward
            })

            next_state, done = recommender.env.step(action)
            if next_state is None:  # Handle end of episode
                done = True
                break
            total_reward += reward
            state = next_state

        debug_print(f"Evaluation complete. Total reward: {total_reward}")
        return recommendations, total_reward
    except Exception as e:
        logging.error(f"Error during evaluation: {str(e)}")
        raise


def visualize_results(recommendations, analytics):
    """Visualize recommendation results."""
    try:
        # Create timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Plot rewards distribution
        with plot_context(figsize=(10, 6)) as (fig, ax):
            rewards = [r['Reward'] for r in recommendations]
            plt.hist(rewards, bins=20)
            plt.title('Distribution of Rewards')
            plt.xlabel('Reward')
            plt.ylabel('Count')
            analytics.save_plot(plt.gcf(), 'rewards_distribution')

        # Plot event type distribution
        with plot_context(figsize=(12, 6)) as (fig, ax):
            event_types = [r['Event Type'] for r in recommendations]
            pd.Series(event_types).value_counts().plot(kind='bar')
            plt.title('Distribution of Recommended Event Types')
            plt.xlabel('Event Type')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            analytics.save_plot(plt.gcf(), 'event_distribution')

    except Exception as e:
        logging.error(f"Error during visualization: {str(e)}")
        raise


def main():
    """Main execution function."""
    try:
        # Setup logging
        log_file = LOGS_DIR / 'event_recommender.log'
        logging.basicConfig(
            filename=str(log_file),  # Convert Path to string
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        debug_print("Starting event recommendation system")


        # Load data
        events_df, users_df = load_data()
        user = users_df.iloc[0]  # Start with first user for testing

        # Initialize components
        state_size = 5
        action_size = len(events_df)


        # Training phase
        if TRAIN_MODEL:
            # Initialize analytics
            analytics = TrainingAnalytics()

            recommender = ImprovedEventRecommenderDQN(
                state_size=state_size,
                action_size=action_size,
                user=user,
                events_df=events_df,
                analytics=analytics
            )
            analytics = train_recommender(recommender, NUM_EPISODES)

        # Testing phase
        if TEST_MODEL:
            info_print("\nStarting Testing Phase...")

            # Initialize tester
            tester = EventTester(
                model_path=LOAD_MODEL_PATH,
                events_df=events_df,
                user=user
            )

            # Get and display recommendations
            recommendations = tester.get_top_recommendations(num_recommendations=10)
            tester.display_recommendations(recommendations)

            info_print("\nTesting Complete!")

    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        raise

def test_recommender(recommender, events_df, user, num_recommendations=10):
    try:
        info_print("\nStarting Recommendation Testing...")

        # Store original training mode
        was_training = recommender.dqn.training

        # Set model to evaluation mode
        recommender.dqn.eval()
        state = recommender.env.reset()

        # Get Q-values for all actions at once
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = recommender.dqn(state_tensor).squeeze()

        # Get top K actions based on Q-values
        top_k = min(num_recommendations * 2, len(q_values))  # Get more than we need
        top_actions = torch.topk(q_values, k=top_k).indices.tolist()

        info_print(f"Top {top_k} actions selected: {top_actions[:10]}...")  # Show first 10

        recommendations = []
        seen_events = set()

        with tqdm(total=num_recommendations, desc="Generating Recommendations") as pbar:
            for action in top_actions:
                if len(recommendations) >= num_recommendations:
                    break

                if action in seen_events:
                    continue

                if action >= len(events_df):
                    logging.error(f"Action index {action} out of bounds for events_df with length {len(events_df)}")
                    continue


                event = events_df.iloc[action]
                reward = recommender.get_reward(event, state)

                recommendations.append({
                    'Event ID': event['Event ID'],
                    'Event Type': event['Event Type'],
                    'Price ($)': event['Price ($)'],
                    'Distance (km)': event['Distance (km)'],
                    'Popularity': event['Popularity'],
                    'Date/Time': event['Date/Time'],
                    'Reward': reward,
                    'Q-Value': q_values[action].item()
                })

                seen_events.add(action)
                pbar.update(1)

                info_print(f"\nRecommended event {len(recommendations)}:")
                info_print(f"Action: {action}")
                info_print(f"Event Type: {event['Event Type']}")
                info_print(f"Q-Value: {q_values[action]:.2f}")
                info_print(f"Reward: {reward:.2f}")

        # Print recommendations
        info_print("\nTop Recommendations:")
        info_print("=" * 50)

        for i, rec in enumerate(recommendations, 1):
            info_print(f"\nRecommendation {i}:")
            info_print(f"{'Event ID:':<15} {rec['Event ID']}")
            info_print(f"{'Event Type:':<15} {rec['Event Type']}")
            info_print(f"{'Price:':<15} ${rec['Price ($)']:.2f}")
            info_print(f"{'Distance:':<15} {rec['Distance (km)']:.1f} km")
            info_print(f"{'Popularity:':<15} {rec['Popularity']:.0f}")
            info_print(f"{'Date/Time:':<15} {rec['Date/Time']}")
            info_print(f"{'Reward Score:':<15} {rec['Reward']:.2f}")
            info_print(f"{'Q-Value:':<15} {rec['Q-Value']:.2f}")

            event_series = pd.Series(rec)
            recommender.env.analyze_recommendation(event_series)
            recommender.env.visualize_component_impact(event_series)
            info_print("-" * 50)

        if len(recommendations) < num_recommendations:
            info_print(
                f"\nWarning: Only found {len(recommendations)} valid recommendations out of {num_recommendations} requested")
            if len(recommendations) == 0:
                raise ValueError("No valid recommendations found")

        return recommendations


    except Exception as e:
        logging.error(f"Error during testing: {str(e)}")
        info_print(f"Error occurred: {str(e)}")
        raise

    finally:
        # Restore original training mode
        if was_training:
            recommender.dqn.train()


if __name__ == "__main__":
    main()

