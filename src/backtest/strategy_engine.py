import yaml
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from pathlib import Path

class StrategyEngine:
    def __init__(self, config_path: str):
        """初始化策略引擎
        
        Args:
            config_path: 策略配置文件路径
        """
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> Dict:
        """加载策略配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            Dict: 配置信息
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
            
    def _execute_code(self, code: str, local_vars: Dict) -> Any:
        """执行代码片段
        
        Args:
            code: 要执行的代码
            local_vars: 局部变量字典
            
        Returns:
            Any: 执行结果
        """
        try:
            exec(code, globals(), local_vars)
            return local_vars.get('result', None)
        except Exception as e:
            print(f"执行代码时出错: {e}")
            return None
            
    def _run_strategy(self, data: pd.DataFrame, strategy_config: Dict) -> Dict:
        """运行单个策略
        
        Args:
            data: 历史数据
            strategy_config: 策略配置
            
        Returns:
            Dict: 策略运行结果
        """
        # 复制数据，避免修改原始数据
        data = data.copy()
        
        # 计算指标
        for indicator in strategy_config['indicators']:
            local_vars = {
                'data': data,
                'params': indicator['params'],
                'result': None
            }
            self._execute_code(indicator['code'], local_vars)
            data = local_vars['data']
            
        # 生成信号
        signals = pd.DataFrame(index=data.index)
        signals['signal'] = 0
        
        # 生成买入信号
        local_vars = {
            'data': data,
            'params': strategy_config['parameters'],
            'result': None
        }
        buy_condition = self._execute_code(
            f"result = {strategy_config['signals']['buy']['code']}",
            local_vars
        )
        if buy_condition is not None:
            signals.loc[buy_condition, 'signal'] = 1
            
        # 生成卖出信号
        local_vars = {
            'data': data,
            'params': strategy_config['parameters'],
            'result': None
        }
        sell_condition = self._execute_code(
            f"result = {strategy_config['signals']['sell']['code']}",
            local_vars
        )
        if sell_condition is not None:
            signals.loc[sell_condition, 'signal'] = -1
            
        # 计算仓位
        positions = pd.DataFrame(index=signals.index)
        if strategy_config['position_sizing']['type'] == 'fixed':
            position_size = strategy_config['position_sizing']['value']
            positions['position'] = signals['signal'] * position_size
            
        # 计算收益
        returns = pd.Series(index=data.index)
        returns.iloc[0] = 0
        for i in range(1, len(data)):
            daily_return = (data['close'].iloc[i] / data['close'].iloc[i-1] - 1)
            returns.iloc[i] = daily_return * positions['position'].iloc[i-1]
            
        return {
            'returns': returns,
            'positions': positions,
            'signals': signals
        }
        
    def backtest(self, data: pd.DataFrame, start_date: str, end_date: str) -> Dict:
        """执行回测
        
        Args:
            data: 历史数据
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            Dict: 回测结果
        """
        # 筛选时间范围
        mask = (data.index >= start_date) & (data.index <= end_date)
        data = data[mask].copy()
        
        results = {}
        
        # 执行单个策略回测
        for strategy_name, strategy_config in self.config['strategies'].items():
            results[strategy_name] = self._run_strategy(data, strategy_config)
            
        # 执行组合策略回测
        if 'strategy_portfolio' in self.config:
            portfolio_config = self.config['strategy_portfolio']
            portfolio_results = {
                'returns': pd.Series(),
                'positions': pd.DataFrame(),
                'trades': []
            }
            
            # 计算每个策略的权重
            weights = {s['name']: s['weight'] for s in portfolio_config['strategies']}
            
            # 合并各个策略的结果
            for strategy_name, weight in weights.items():
                if strategy_name in results:
                    portfolio_results['returns'] = portfolio_results['returns'].add(
                        results[strategy_name]['returns'] * weight,
                        fill_value=0
                    )
                    
            results['portfolio'] = portfolio_results
            
        return results 