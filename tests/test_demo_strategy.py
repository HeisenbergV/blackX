import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.backtest.strategy_engine import StrategyEngine
import yaml

@pytest.fixture
def sample_data():
    """生成测试用的股票数据"""
    # 生成日期范围
    dates = pd.date_range(start='2020-01-01', end='2020-12-31', freq='D')
    
    # 生成随机价格数据
    np.random.seed(42)
    base_price = 100
    returns = np.random.normal(0.001, 0.02, len(dates))
    prices = base_price * (1 + returns).cumprod()
    
    # 创建DataFrame
    data = pd.DataFrame({
        'open': prices,
        'high': prices * 1.02,
        'low': prices * 0.98,
        'close': prices,
        'volume': np.random.randint(1000000, 2000000, len(dates))
    }, index=dates)
    
    return data

@pytest.fixture
def strategy_engine():
    """初始化策略引擎"""
    return StrategyEngine('src/strategies/demo.yml')

def test_strategy_loading(strategy_engine):
    """测试策略加载"""
    # 检查策略是否成功加载
    assert 'demo_strategy' in strategy_engine.config['strategies']
    
    # 检查策略配置
    strategy_config = strategy_engine.config['strategies']['demo_strategy']
    assert strategy_config['name'] == "示例策略"
    assert 'indicators' in strategy_config
    assert 'signals' in strategy_config
    assert 'position_sizing' in strategy_config

def test_indicator_calculation(sample_data, strategy_engine):
    """测试指标计算"""
    # 获取策略配置
    strategy_config = strategy_engine.config['strategies']['demo_strategy']
    
    # 计算指标
    data = sample_data.copy()
    for indicator in strategy_config['indicators']:
        local_vars = {
            'data': data,
            'params': indicator['params'],
            'result': None
        }
        strategy_engine._execute_code(indicator['code'], local_vars)
        data = local_vars['data']
    
    # 检查指标是否正确计算
    assert 'ma_fast' in data.columns
    assert 'ma_slow' in data.columns
    assert 'rsi' in data.columns
    
    # 检查指标值是否合理
    assert not data['ma_fast'].isna().all()
    assert not data['ma_slow'].isna().all()
    assert not data['rsi'].isna().all()
    assert (data['rsi'] >= 0).all() and (data['rsi'] <= 100).all()

def test_signal_generation(sample_data, strategy_engine):
    """测试信号生成"""
    # 获取策略配置
    strategy_config = strategy_engine.config['strategies']['demo_strategy']
    
    # 计算指标
    data = sample_data.copy()
    for indicator in strategy_config['indicators']:
        local_vars = {
            'data': data,
            'params': indicator['params'],
            'result': None
        }
        strategy_engine._execute_code(indicator['code'], local_vars)
        data = local_vars['data']
    
    # 生成买入信号
    local_vars = {
        'data': data,
        'params': strategy_config['parameters'],
        'result': None
    }
    buy_condition = strategy_engine._execute_code(
        f"result = {strategy_config['signals']['buy']['code']}",
        local_vars
    )
    
    # 生成卖出信号
    local_vars = {
        'data': data,
        'params': strategy_config['parameters'],
        'result': None
    }
    sell_condition = strategy_engine._execute_code(
        f"result = {strategy_config['signals']['sell']['code']}",
        local_vars
    )
    
    # 检查信号
    assert isinstance(buy_condition, pd.Series)
    assert isinstance(sell_condition, pd.Series)
    assert buy_condition.dtype == bool
    assert sell_condition.dtype == bool

def test_position_sizing(sample_data, strategy_engine):
    """测试仓位管理"""
    # 获取策略配置
    strategy_config = strategy_engine.config['strategies']['demo_strategy']
    
    # 计算指标和信号
    data = sample_data.copy()
    for indicator in strategy_config['indicators']:
        local_vars = {
            'data': data,
            'params': indicator['params'],
            'result': None
        }
        strategy_engine._execute_code(indicator['code'], local_vars)
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
    buy_condition = strategy_engine._execute_code(
        f"result = {strategy_config['signals']['buy']['code']}",
        local_vars
    )
    signals.loc[buy_condition, 'signal'] = 1
    
    # 生成卖出信号
    local_vars = {
        'data': data,
        'params': strategy_config['parameters'],
        'result': None
    }
    sell_condition = strategy_engine._execute_code(
        f"result = {strategy_config['signals']['sell']['code']}",
        local_vars
    )
    signals.loc[sell_condition, 'signal'] = -1
    
    # 计算仓位
    positions = pd.DataFrame(index=signals.index)
    if strategy_config['position_sizing']['type'] == 'fixed':
        position_size = strategy_config['position_sizing']['value']
        positions['position'] = signals['signal'] * position_size
    
    # 检查仓位
    assert isinstance(positions, pd.DataFrame)
    assert 'position' in positions.columns
    assert (positions['position'].abs() <= position_size).all()

def test_full_backtest(sample_data, strategy_engine):
    """测试完整回测"""
    # 执行回测
    results = strategy_engine.backtest(
        sample_data,
        start_date='2020-01-01',
        end_date='2020-12-31'
    )
    
    # 检查回测结果
    assert 'demo_strategy' in results
    strategy_results = results['demo_strategy']
    
    # 检查返回的数据结构
    assert 'returns' in strategy_results
    assert 'positions' in strategy_results
    assert 'signals' in strategy_results
    
    # 检查数据类型
    assert isinstance(strategy_results['returns'], pd.Series)
    assert isinstance(strategy_results['positions'], pd.DataFrame)
    assert isinstance(strategy_results['signals'], pd.DataFrame)
    
    # 检查信号值
    assert strategy_results['signals']['signal'].isin([-1, 0, 1]).all()
    
    # 检查收益计算
    assert not strategy_results['returns'].isna().any()
    assert strategy_results['returns'].index.equals(sample_data.index) 