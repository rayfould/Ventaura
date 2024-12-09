"""
epsilon_greedy.py
Implements epsilon-greedy exploration policy for DQN-based event recommendations.
"""

from config import *


class EpsilonGreedyPolicy:
    """
    Implements epsilon-greedy policy for exploration vs exploitation.

    Attributes:
        epsilon (float): Current exploration rate
        decay_episodes (int): Number of episodes over which to decay epsilon
        epsilon_decay (float): Rate at which epsilon decays
    """

    def __init__(self):
        """
        Initialize epsilon-greedy policy using config values.
        """
        self.epsilon = INITIAL_EPSILON
        self.decay_episodes = int(NUM_EPISODES * TRAINING_PROGRESS)
        self.epsilon_decay = EPSILON_DECAY
        debug_print(f"Initialized EpsilonGreedyPolicy with config values: "
                   f"initial_epsilon={INITIAL_EPSILON}, "
                   f"decay_episodes={self.decay_episodes}, "
                   f"epsilon_decay={EPSILON_DECAY}")

    def get_action(self, q_values):
        """
        Select action using epsilon-greedy policy.

        Args:
            q_values (torch.Tensor): Q-values for all possible actions

        Returns:
            int: Selected action index
        """
        if random.random() < self.epsilon:
            # Exploration: choose a random action (event)
            action = random.randint(0, len(q_values) - 1)
            debug_print(f"Exploring: Selected random action {action}")
            return action
        else:
            # Exploitation: choose the action with the highest Q-value
            action = torch.argmax(q_values.cpu() if q_values.is_cuda else q_values).item()
            debug_print(f"Exploiting: Selected best action {action}")
            return action

    def update_epsilon(self):
        """Update epsilon value using precalculated decay rate from config."""
        old_epsilon = self.epsilon
        self.epsilon = max(FINAL_EPSILON, self.epsilon * self.epsilon_decay)
        debug_print(f"Updated epsilon from {old_epsilon:.4f} to {self.epsilon:.4f}")

    def reset_epsilon(self):
        """Reset epsilon to its initial value."""
        self.epsilon = INITIAL_EPSILON
        debug_print(f"Reset epsilon to {self.epsilon}")

    def get_current_epsilon(self):
        """
        Get current epsilon value.

        Returns:
            float: Current epsilon value
        """
        return self.epsilon
