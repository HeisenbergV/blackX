import pandas as pd
import numpy as np
from .base import TechnicalIndicator

class MACD(TechnicalIndicator):
    """移动平均收敛散度指标(MACD)"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        """
        Args:
            fast_period: 快线周期
            slow_period: 慢线周期
            signal_period: 信号线周期
        """
        super().__init__('MACD', {
            'fast_period': fast_period,
            'slow_period': slow_period,
            'signal_period': signal_period
        })
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        # 计算快线和慢线
        fast_ema = data['close'].ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = data['close'].ewm(span=self.slow_period, adjust=False).mean()
        
        # 计算MACD线
        macd_line = fast_ema - slow_ema
        
        # 计算信号线
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()
        
        # 计算柱状图
        histogram = macd_line - signal_line
        
        # 返回所有指标
        return pd.DataFrame({
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram
        }) 