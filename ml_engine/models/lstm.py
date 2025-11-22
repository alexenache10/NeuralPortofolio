import torch
import torch.nn as nn
from typing import Tuple

class NeuralPriceLSTM(nn.Module):
    """
    LSTM Architecture for time series forecasting.

    Architecture scheme:
    Input -> [LSTM Layer 1] -> [Dropout] -> [LSTM Layer 2] -> ... -> [Last Hidden State] -> [Fully Connected Head] -> Output
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int = 1,
        num_layers: int = 2,
        dropout_prob: float = 0.2     
    ):
        """
        Arguments:
        input_dim: number of features (open, close, vol, etc.)
        hidden_dim: num. of neurons in the hidden layers
        output_dim: num. of values predicted (1 for the tommorow value)
        num_layers: num. of lstm stacked layers
        dropout_prob: the probability of turning down neurons for avoiding overfitting 
        """

        super(NeuralPriceLSTM, self).__init__()

        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout_prob if num_layers > 1 else 0
        )
        self.fc_layers = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),                 
            nn.Dropout(dropout_prob),  
            nn.Linear(32, output_dim)  
        )
       

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x (torch.Tensor): (Batch_size, sequence_length, input_dim)

        Returns:
            torch.Tensor: (Batch_size, output_dim)
        """

        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(x.device)

        out, (hn, cn) = self.lstm(x, (h0, c0))

        last_time_step_feature = out[:, -1, :]

        prediction = self.fc_layers(last_time_step_feature)

        return prediction