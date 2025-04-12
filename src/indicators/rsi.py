import pandas as pd
import numpy as np
from .base import TechnicalIndicator

class RSI(TechnicalIndicator):
    """相对强弱指标(RSI)"""
    
    def __init__(self, period: int = 14):
        """
        Args:
            period: RSI计算周期
        """
        super().__init__('RSI', {'period': period})
        self.period = period
        
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        # 计算价格变化
        delta = data['close'].diff()
        
        # 分离上涨和下跌
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # 计算平均上涨和下跌
        avg_gain = gain.rolling(window=self.period).mean()
        avg_loss = loss.rolling(window=self.period).mean()
        
        # 计算RS
        rs = avg_gain / avg_loss
        
        # 计算RSI
        rsi = 100 - (100 / (1 + rs))
        
        return rsi 