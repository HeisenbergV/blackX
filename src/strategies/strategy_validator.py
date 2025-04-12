import pandas as pd
import numpy as np
import plotly.graph_objects as go
import akshare as ak
from typing import Dict, Tuple
from .base_strategy import BaseStrategy

class StrategyValidator:
    """策略验证器，用于验证策略配置和执行回测"""
    
    def __init__(self, strategy: BaseStrategy):
        """初始化策略验证器
        
        Args:
            strategy: 要验证的策略实例
        """
        self.strategy = strategy
        
    def validate_config(self) -> Tuple[bool, str]:
        """验证策略配置
        
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        try:
            print("验证策略配置...")
            print("策略配置内容：")
            print(self.strategy.config)
            
            # 检查配置结构
            if not isinstance(self.strategy.config, dict):
                return False, "配置必须是字典格式"
            
            # 检查必需字段
            required_fields = ['name', 'type', 'description', 'parameters', 'indicators', 'signals', 'position_sizing']
            for field in required_fields:
                if field not in self.strategy.config:
                    return False, f"缺少必需字段: {field}"
            
            # 检查指标配置
            if not isinstance(self.strategy.config['indicators'], list):
                return False, "指标配置必须是列表格式"
                
            for indicator in self.strategy.config['indicators']:
                if not isinstance(indicator, dict):
                    return False, "指标配置项必须是字典格式"
                if not all(key in indicator for key in ['name', 'code', 'params']):
                    return False, "指标配置不完整"
            
            # 检查信号配置
            if not isinstance(self.strategy.config['signals'], dict):
                return False, "信号配置必须是字典格式"
            if not all(key in self.strategy.config['signals'] for key in ['buy', 'sell']):
                return False, "信号配置不完整"
            
            # 检查仓位配置
            if not isinstance(self.strategy.config['position_sizing'], dict):
                return False, "仓位配置必须是字典格式"
            if not all(key in self.strategy.config['position_sizing'] for key in ['type', 'value']):
                return False, "仓位配置不完整"
            
            # 检查参数类型
            if not isinstance(self.strategy.config['parameters'], dict):
                return False, "参数必须是字典格式"
            
            # 检查仓位值
            if self.strategy.config['position_sizing']['type'] == 'fixed':
                value = self.strategy.config['position_sizing']['value']
                if not isinstance(value, (int, float)):
                    return False, "仓位值必须是数字"
                if not 0 < value <= 1:
                    return False, "仓位值必须在 0 到 1 之间"
            
            return True, "策略配置验证通过"
            
        except Exception as e:
            return False, f"验证过程中发生错误: {str(e)}"
    
    def get_test_data(self) -> pd.DataFrame:
        """获取测试数据
        
        Returns:
            pd.DataFrame: 测试数据
        """
        # 获取测试股票数据
        test_stock = "000001"  # 使用平安银行作为测试股票
        test_data = ak.stock_zh_a_hist(symbol=test_stock, period="daily", 
                                     start_date="20230101", end_date="20231231")
        test_data = test_data.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume'
        })
        test_data['date'] = pd.to_datetime(test_data['date'])
        test_data.set_index('date', inplace=True)
        return test_data
    
    def run_backtest(self, data: pd.DataFrame) -> Dict:
        """运行回测
        
        Args:
            data: 历史数据
            
        Returns:
            Dict: 回测结果
        """
        return self.strategy.run(data, '2023-01-01', '2023-12-31')
    
    def get_performance_metrics(self, results: Dict) -> Dict:
        """计算性能指标
        
        Args:
            results: 回测结果
            
        Returns:
            Dict: 性能指标
        """
        returns = results['returns']
        positions = results['positions']
        signals = results['signals']
        
        # 计算累计收益
        cumulative_returns = (1 + returns).cumprod()
        
        # 计算各项指标
        total_return = cumulative_returns.iloc[-1] - 1
        annual_return = (1 + total_return) ** (252/len(cumulative_returns)) - 1
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
        max_drawdown = (cumulative_returns / cumulative_returns.cummax() - 1).min()
        
        # 计算交易统计
        buy_signals = len(signals[signals['signal'] == 1])
        sell_signals = len(signals[signals['signal'] == -1])
        trade_frequency = buy_signals + sell_signals
        
        # 计算持仓统计
        position_stats = {
            'max': positions['position'].max(),
            'min': positions['position'].min(),
            'mean': positions['position'].mean()
        }
        
        return {
            'returns': {
                'total': total_return,
                'annual': annual_return,
                'sharpe': sharpe_ratio,
                'max_drawdown': max_drawdown
            },
            'trades': {
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'frequency': trade_frequency
            },
            'positions': position_stats
        }
    
    def plot_results(self, data: pd.DataFrame, results: Dict, metrics: Dict) -> Dict[str, go.Figure]:
        """绘制回测结果图表
        
        Args:
            data: 原始数据
            results: 回测结果
            metrics: 性能指标
            
        Returns:
            Dict[str, go.Figure]: 图表字典
        """
        # 绘制收益曲线
        returns_fig = go.Figure()
        cumulative_returns = (1 + results['returns']).cumprod()
        benchmark_returns = (data['close'] / data['close'].iloc[0])
        
        returns_fig.add_trace(go.Scatter(
            x=cumulative_returns.index,
            y=cumulative_returns,
            name="策略收益",
            line=dict(color="blue")
        ))
        
        returns_fig.add_trace(go.Scatter(
            x=benchmark_returns.index,
            y=benchmark_returns,
            name="基准收益",
            line=dict(color="gray", dash="dash")
        ))
        
        returns_fig.update_layout(
            title="收益曲线",
            xaxis_title="日期",
            yaxis_title="累计收益",
            height=400
        )
        
        # 绘制交易信号
        signals_fig = go.Figure()
        
        signals_fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close'],
            name="K线"
        ))
        
        buy_signals = results['signals'][results['signals']['signal'] == 1]
        signals_fig.add_trace(go.Scatter(
            x=buy_signals.index,
            y=data.loc[buy_signals.index, 'low'] * 0.98,
            mode='markers',
            marker=dict(symbol='triangle-up', size=10, color='green'),
            name="买入信号"
        ))
        
        sell_signals = results['signals'][results['signals']['signal'] == -1]
        signals_fig.add_trace(go.Scatter(
            x=sell_signals.index,
            y=data.loc[sell_signals.index, 'high'] * 1.02,
            mode='markers',
            marker=dict(symbol='triangle-down', size=10, color='red'),
            name="卖出信号"
        ))
        
        signals_fig.update_layout(
            title="交易信号",
            xaxis_title="日期",
            yaxis_title="价格",
            height=400
        )
        
        # 绘制持仓变化
        positions_fig = go.Figure()
        positions_fig.add_trace(go.Scatter(
            x=results['positions'].index,
            y=results['positions']['position'],
            name="持仓比例",
            line=dict(color="purple")
        ))
        
        positions_fig.update_layout(
            title="持仓变化",
            xaxis_title="日期",
            yaxis_title="持仓比例",
            height=400
        )
        
        return {
            'returns': returns_fig,
            'signals': signals_fig,
            'positions': positions_fig
        } 