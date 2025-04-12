import pandas as pd
import numpy as np
from .base_strategy import BaseStrategy

class MACrossoverStrategy(BaseStrategy):
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算双均线指标
        
        Args:
            data: 历史数据
            
        Returns:
            pd.DataFrame: 包含均线指标的数据
        """
        # 计算快慢均线
        data['fast_ma'] = data['close'].rolling(
            window=self.parameters['fast_period']
        ).mean()
        
        data['slow_ma'] = data['close'].rolling(
            window=self.parameters['slow_period']
        ).mean()
        
        return data
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号
        
        Args:
            data: 历史数据
            
        Returns:
            pd.DataFrame: 包含交易信号的数据
        """
        signals = pd.DataFrame(index=data.index)
        
        # 初始化信号列
        signals['signal'] = 0
        
        # 生成买入信号（快线上穿慢线）
        signals.loc[data['fast_ma'] > data['slow_ma'], 'signal'] = 1
        
        # 生成卖出信号（快线下穿慢线）
        signals.loc[data['fast_ma'] < data['slow_ma'], 'signal'] = -1
        
        return signals 