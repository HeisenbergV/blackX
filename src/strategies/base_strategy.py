from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any

class BaseStrategy(ABC):
    def __init__(self, config: Dict[str, Any], strategy_name: str = None):
        """初始化策略
        
        Args:
            config: 策略配置
            strategy_name: 要使用的策略名称，如果为 None 则使用第一个策略
        """
        print("初始化策略，配置内容：")
        print(config)
        
        if not isinstance(config, dict):
            raise ValueError("配置必须是字典格式")
            
        self.config = config
        
        # 如果配置中有strategies字段，则使用指定的策略
        if 'strategies' in config and strategy_name is not None:
            if strategy_name not in config['strategies']:
                raise ValueError(f"策略 '{strategy_name}' 不存在")
            strategy_config = config['strategies'][strategy_name]
        else:
            strategy_config = config
        
        self.name = strategy_config.get('name', '未命名策略')
        self.type = strategy_config.get('type', 'unknown')
        self.parameters = strategy_config.get('parameters', {})
        self.indicators = strategy_config.get('indicators', [])
        self.signals = strategy_config.get('signals', {})
        self.position_sizing = strategy_config.get('position_sizing', {'type': 'fixed', 'value': 0.1})
        
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标
        
        Args:
            data: 历史数据
            
        Returns:
            pd.DataFrame: 包含技术指标的数据
        """
        # 动态执行指标计算代码
        for indicator in self.indicators:
            # 准备参数
            params = indicator['params']
            # 执行指标计算代码
            exec(indicator['code'], {'data': data, 'params': params})
        return data
        
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号
        
        Args:
            data: 历史数据
            
        Returns:
            pd.DataFrame: 包含交易信号的数据
        """
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        # 动态执行买入信号代码
        buy_condition = eval(self.signals['buy'], {'data': data, 'params': self.parameters})
        signals.loc[buy_condition, 'signal'] = 1
        
        # 动态执行卖出信号代码
        sell_condition = eval(self.signals['sell'], {'data': data, 'params': self.parameters})
        signals.loc[sell_condition, 'signal'] = -1
        
        return signals
        
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