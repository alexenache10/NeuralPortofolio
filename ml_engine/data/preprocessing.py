import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, List

class DataProcessor:
    def __init__(self, feature_cols: List[str]):
        self.feature_cols = feature_cols

        self.scaler_features = MinMaxScaler(feature_range=(0, 1))
        self.scaler_target = MinMaxScaler(feature_range=(0, 1))

    def fit_transform(self, df: pd.DataFrame, target_col: str) -> Tuple[np.ndarray, np.ndarray]:
     
        features = df[self.feature_cols].values
        target = df[[target_col]].values

        scaled_features = self.scaler_features.fit_transform(features)
        scaled_target = self.scaler_target.fit_transform(target)

        return scaled_features, scaled_target

    def inverse_transform_target(self, scaled_data: np.ndarray) -> np.ndarray:

        return self.scaler_target.inverse_transform(scaled_data)