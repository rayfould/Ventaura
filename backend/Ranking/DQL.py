"""
DQL.py
Implements Deep Q-Learning Network and Replay Buffer for event recommendation.
"""

from config import *


class QNetwork(nn.Module):
    def __init__(self, state_size, action_size, analytics=None, create_target=False):
        """
        Initialize Q-Network.

        Args:
            state_size (int): Dimension of state space
            action_size (int): Dimension of action space
            analytics (Analytics, optional): Analytics instance
            create_target (bool): Whether to create a target network
        """
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, action_size)

        # Initialize weights to prevent NaN
        nn.init.xavier_uniform_(self.fc1.weight)
        nn.init.xavier_uniform_(self.fc2.weight)
        nn.init.xavier_uniform_(self.fc3.weight)

        # Initialize Q-value tracking
        self.online_q_values = deque(maxlen=10000)
        self.target_q_values = deque(maxlen=10000)
        self.q_value_diff = deque(maxlen=10000)


        # Add necessary attributes
        self.batch_size = BATCH_SIZE
        self.target_update_frequency = TARGET_UPDATE_FREQUENCY

        self.optimizer = optim.Adam(self.parameters(), lr=LEARNING_RATE)
        self.memory = ReplayBuffer(BUFFER_SIZE, BATCH_SIZE)
        self.analytics = analytics

        # Only create target network if this is the main network
        if not create_target:
            self.target_network = QNetwork(state_size, action_size, analytics, create_target=True)
            # Copy weights manually
            self.copy_weights_to_target()

        debug_print(f"Initialized QNetwork with state_size: {state_size}, action_size: {action_size}")


    def forward(self, state):
        """
        Forward pass through the network.

        Args:
            state (torch.Tensor): Input state

        Returns:
            torch.Tensor: Q-values for each action
        """
        x = F.relu(self.fc1(state))
        x = F.relu(self.fc2(x))
        q_values = self.fc3(x)

        # Track Q-values for analytics
        if self.analytics and self.training:
            if hasattr(self, 'target_network'):  # Only track if this is online network
                online_q = q_values.mean().item()
                with torch.no_grad():
                    target_q = self.target_network(state).mean().item()

                self.online_q_values.append(online_q)
                self.target_q_values.append(target_q)

                self.analytics.track_dql_training(
                    q_values=q_values,
                    online_q=online_q,
                    target_q=target_q,
                    loss=self.last_loss if hasattr(self, 'last_loss') else None,
                    gradients={name: param.grad for name, param in self.named_parameters() if param.grad is not None},
                    network_state={name: param.data for name, param in self.named_parameters()},
                    action_taken=torch.argmax(q_values).item()
                )

        return q_values

    def remember(self, state, action, reward, next_state, done):
        """
        Store experience in replay buffer.

        Args:
            state (np.array): Current state
            action (int): Action taken
            reward (float): Reward received
            next_state (np.array): Next state
            done (bool): Whether episode is done
        """
        self.memory.add(state, action, reward, next_state, done)

    def copy_weights_to_target(self):
        """Manually copy weights to target network"""
        if hasattr(self, 'target_network'):
            self.target_network.fc1.weight.data = self.fc1.weight.data.clone()
            self.target_network.fc1.bias.data = self.fc1.bias.data.clone()
            self.target_network.fc2.weight.data = self.fc2.weight.data.clone()
            self.target_network.fc2.bias.data = self.fc2.bias.data.clone()
            self.target_network.fc3.weight.data = self.fc3.weight.data.clone()
            self.target_network.fc3.bias.data = self.fc3.bias.data.clone()
            debug_print("Manually copied weights to target network")

    def replay(self, batch_size):
        """
        Train on a batch of experiences.

        Args:
            batch_size (int): Size of training batch
        """
        if self.memory.size() < batch_size:
            return

        states, actions, rewards, next_states, dones = self.memory.sample()

        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        # Current Q values
        current_q_values = self(states).gather(1, actions.unsqueeze(1)).squeeze()

        # Double DQN modification
        with torch.no_grad():
            # Use online network to SELECT action
            next_actions = self(next_states).argmax(dim=1, keepdim=True)

            # Use target network to EVALUATE action
            next_q_values = self.target_network(next_states).gather(1, next_actions).squeeze()
            target_q_values = rewards + (GAMMA * next_q_values * (1 - dones))

        # Compute loss and update
        loss = F.mse_loss(current_q_values, target_q_values)
        self.last_loss = loss.item()

        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.parameters(), 1.0)
        self.optimizer.step()

        return loss.item()

    def save_model(self, path):
        """
        Save model weights to file.

        Args:
            path (str): Path to save the model
        """
        torch.save(self.state_dict(), path)
        debug_print(f"Model saved to {path}")

    def load_model(self, path):
        """
        Load model weights from file.

        Args:
            path (str): Path to load the model from
        """
        self.load_state_dict(torch.load(path))
        self.eval()
        debug_print(f"Model loaded from {path}")


class ReplayBuffer:
    """
    Replay buffer for experience replay.

    Attributes:
        buffer (deque): Buffer to store experiences
        batch_size (int): Size of training batches
    """

    def __init__(self, buffer_size, batch_size):
        """
        Initialize replay buffer.

        Args:
            buffer_size (int): Maximum size of buffer
            batch_size (int): Size of training batches
        """
        self.buffer = deque(maxlen=BUFFER_SIZE)
        self.batch_size = BATCH_SIZE  # From config
        self.buffer_size = BUFFER_SIZE  # From config
        debug_print(f"Initialized ReplayBuffer with size: {buffer_size}, batch_size: {batch_size}")

    def add(self, state, action, reward, next_state, done):
        """
        Add experience to buffer.

        Args:
            state (np.array): Current state
            action (int): Action taken
            reward (float): Reward received
            next_state (np.array): Next state
            done (bool): Whether episode is done
        """
        if next_state is None and not done:
            next_state = np.zeros_like(state)
            debug_print("Warning: Got None next_state in non-terminal state")
            return
        if next_state is None:
            next_state = state

        experience = (state, action, reward, next_state, done)
        self.buffer.append(experience)

    def sample(self):
        """
        Sample a batch of experiences.

        Returns:
            tuple: Batch of (states, actions, rewards, next_states, dones)
        """
        batch_size = min(self.batch_size, len(self.buffer))
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        return np.array(states), np.array(actions), np.array(rewards), np.array(next_states), np.array(dones)

    def size(self):
        """
        Get current size of buffer.

        Returns:
            int: Current buffer size
        """
        return len(self.buffer)

    def clear(self):
        """Clear the replay buffer"""
        self.buffer.clear()

