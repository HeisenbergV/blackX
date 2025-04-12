from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any

class BaseStrategy(ABC):
    def __init__(self, config: Dict[str, Any]):
        """初始化策略
        
        Args:
            config: 策略配置
        """
        self.config = config
        self.name = config['name']
        self.parameters = config['parameters']
        self.indicators = config['indicators']
        self.signals = config['signals']
        self.position_sizing = config['position_sizing']
        
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标
        
        Args:
            data: 历史数据
            
        Returns:
            pd.DataFrame: 包含技术指标的数据
        """
        pass
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号
        
        Args:
            data: 历史数据
            
        Returns:
            pd.DataFrame: 包含交易信号的数据
        """
        pass
        
    def run(self, data: pd.DataFrame, start_date: str, end_date: str) -> Dict:
        """运行策略
        
        Args:
            data: 历史数据
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict: 策略运行结果
        """
        # 筛选时间范围
        mask = (data.index >= start_date) & (data.index <= end_date)
        data = data[mask].copy()
        
        # 计算指标
        data = self.calculate_indicators(data)
        
        # 生成信号
        signals = self.generate_signals(data)
        
        # 计算仓位
        positions = self._calculate_positions(signals)
        
        # 计算收益
        returns = self._calculate_returns(data, positions)
        
        return {
            'returns': returns,
            'positions': positions,
            'signals': signals
        }
        
    def _calculate_positions(self, signals: pd.DataFrame) -> pd.DataFrame:
        """计算仓位
        
        Args:
            signals: 交易信号
            
        Returns:
            pd.DataFrame: 仓位数据
        """
        positions = pd.DataFrame(index=signals.index)
        
        if self.position_sizing['type'] == 'fixed':
            position_size = self.position_sizing['value']
            positions['position'] = signals['signal'] * position_size
            
        return positions
        
    def _calculate_returns(self, data: pd.DataFrame, positions: pd.DataFrame) -> pd.Series:
        """计算收益
        
        Args:
            data: 历史数据
            positions: 仓位数据
            
        Returns:
            pd.Series: 收益序列
        """
        returns = pd.Series(index=data.index)
        returns.iloc[0] = 0
        
        for i in range(1, len(data)):
            # 计算每日收益
            daily_return = (data['close'].iloc[i] / data['close'].iloc[i-1] - 1)
            # 考虑仓位后的收益
            returns.iloc[i] = daily_return * positions['position'].iloc[i-1]
            
        return returns 