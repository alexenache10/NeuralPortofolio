# ml_engine/data/loader.py
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader

class FinancialDataset(Dataset):
    def __init__(self, features: np.ndarray, target: np.ndarray, seq_len: int):
        """
        features: Scaled Matrix (N_samples, N_features)
        target: Scaled Target array  (N_samples, 1)
        seq_len: Window Len (ex: 60 zile)
        """
        self.features = features
        self.target = target
        self.seq_len = seq_len

    def __len__(self):
        return len(self.features) - self.seq_len

    def __getitem__(self, idx):
        x = self.features[idx : idx + self.seq_len]
        
        y = self.target[idx + self.seq_len]

        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

def create_dataloaders(df, processor, target_col, seq_len, batch_size, test_size=0.2):
    # 1. Scale
    scaled_features, scaled_target = processor.fit_transform(df, target_col)

    # 2. Split 
    train_size = int(len(scaled_features) * (1 - test_size))
    
    train_features = scaled_features[:train_size]
    train_target = scaled_target[:train_size]
    
    test_features = scaled_features[train_size:]
    test_target = scaled_target[train_size:]

    # 3. Dataset creation
    train_dataset = FinancialDataset(train_features, train_target, seq_len)
    test_dataset = FinancialDataset(test_features, test_target, seq_len)

    # 4. Loader creation
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, test_loader