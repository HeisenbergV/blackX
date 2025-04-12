import yaml
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from pathlib import Path

class StrategyEngine:
    def __init__(self, config_path: str = None):
        """初始化策略引擎
        
        Args:
            config_path: 策略配置文件路径，如果为None则自动加载所有策略
        """
        self.config = self._load_all_configs(config_path)
        
    def _load_all_configs(self, config_path: str = None) -> Dict:
        """加载所有策略配置
        
        Args:
            config_path: 指定的配置文件路径
            
        Returns:
            Dict: 合并后的配置信息
        """
        config = {'strategies': {}}
        
        # 从 strategies 目录加载所有策略
        strategy_dir = Path("strategies")
        if strategy_dir.exists():
            for strategy_file in strategy_dir.glob("*.y*ml"):  # 支持 .yaml 和 .yml
                with open(strategy_file, 'r', encoding='utf-8') as f:
                    strategy_config = yaml.safe_load(f)
                    if 'strategies' in strategy_config:
                        config['strategies'].update(strategy_config['strategies'])
                    else:
                        # 如果配置中没有strategies字段，则使用整个配置作为一个策略
                        strategy_name = strategy_file.stem
                        config['strategies'][strategy_name] = strategy_config
        
        # 如果指定了配置文件，则加载
        if config_path is not None:
            with open(config_path, 'r', encoding='utf-8') as f:
                specified_config = yaml.safe_load(f)
                if 'strategies' in specified_config:
                    config['strategies'].update(specified_config['strategies'])
                else:
                    # 如果配置中没有strategies字段，则使用整个配置作为一个策略
                    strategy_name = Path(config_path).stem
                    config['strategies'][strategy_name] = specified_config
        
        return config
        
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
        
        # 处理不同的信号格式
        buy_signal = strategy_config['signals']['buy']
        if isinstance(buy_signal, dict) and 'code' in buy_signal:
            buy_condition = self._execute_code(
                f"result = {buy_signal['code']}",
                local_vars
            )
        else:
            buy_condition = self._execute_code(
                f"result = {buy_signal}",
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
        
        # 处理不同的信号格式
        sell_signal = strategy_config['signals']['sell']
        if isinstance(sell_signal, dict) and 'code' in sell_signal:
            sell_condition = self._execute_code(
                f"result = {sell_signal['code']}",
                local_vars
            )
        else:
            sell_condition = self._execute_code(
                f"result = {sell_signal}",
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