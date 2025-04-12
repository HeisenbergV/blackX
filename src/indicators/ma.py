import pandas as pd
import numpy as np
from .base import TechnicalIndicator

class MovingAverage(TechnicalIndicator):
    """移动平均线指标"""
    
    def __init__(self, window: int = 20, ma_type: str = 'SMA'):
        """
        Args:
            window: 计算周期
            ma_type: 移动平均类型，可选 'SMA'(简单移动平均), 'EMA'(指数移动平均)
        """
        super().__init__('MA', {'window': window, 'type': ma_type})
        self.window = window
        self.ma_type = ma_type
        
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        if self.ma_type == 'SMA':
            return data['close'].rolling(window=self.window).mean()
        elif self.ma_type == 'EMA':
            return data['close'].ewm(span=self.window, adjust=False).mean()
        else:
            raise ValueError(f"不支持的移动平均类型: {self.ma_type}") 