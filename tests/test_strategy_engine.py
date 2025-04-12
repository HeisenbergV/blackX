import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.backtest.strategy_engine import StrategyEngine

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
    return StrategyEngine('src/strategies/strategy_config.yaml')

def test_ma_crossover_strategy(sample_data, strategy_engine):
    """测试双均线策略"""
    results = strategy_engine.backtest(
        sample_data,
        start_date='2020-01-01',
        end_date='2020-12-31'
    )
    
    # 检查结果
    assert 'ma_crossover' in results
    strategy_results = results['ma_crossover']
    
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

def test_rsi_strategy(sample_data, strategy_engine):
    """测试RSI策略"""
    results = strategy_engine.backtest(
        sample_data,
        start_date='2020-01-01',
        end_date='2020-12-31'
    )
    
    # 检查结果
    assert 'rsi_strategy' in results
    strategy_results = results['rsi_strategy']
    
    # 检查信号值
    assert strategy_results['signals']['signal'].isin([-1, 0, 1]).all()
    
    # 检查仓位大小
    assert (strategy_results['positions']['position'].abs() <= 0.1).all()

def test_bollinger_bands_strategy(sample_data, strategy_engine):
    """测试布林带策略"""
    results = strategy_engine.backtest(
        sample_data,
        start_date='2020-01-01',
        end_date='2020-12-31'
    )
    
    # 检查结果
    assert 'bollinger_bands' in results
    strategy_results = results['bollinger_bands']
    
    # 检查信号值
    assert strategy_results['signals']['signal'].isin([-1, 0, 1]).all()

def test_portfolio_strategy(sample_data, strategy_engine):
    """测试组合策略"""
    results = strategy_engine.backtest(
        sample_data,
        start_date='2020-01-01',
        end_date='2020-12-31'
    )
    
    # 检查结果
    assert 'portfolio' in results
    portfolio_results = results['portfolio']
    
    # 检查收益计算
    assert not portfolio_results['returns'].isna().any()
    assert portfolio_results['returns'].index.equals(sample_data.index)
    
    # 检查组合权重
    total_weight = sum(s['weight'] for s in 
                      strategy_engine.config['strategy_portfolio']['strategies'])
    assert abs(total_weight - 1.0) < 1e-6  # 权重之和应该等于1

def test_strategy_parameters(sample_data, strategy_engine):
    """测试策略参数"""
    # 获取双均线策略配置
    ma_config = strategy_engine.config['strategies']['ma_crossover']
    
    # 检查参数
    assert ma_config['parameters']['fast_period'] == 5
    assert ma_config['parameters']['slow_period'] == 20
    
    # 检查仓位管理
    assert ma_config['position_sizing']['type'] == 'fixed'
    assert ma_config['position_sizing']['value'] == 0.1

def test_invalid_dates(sample_data, strategy_engine):
    """测试无效日期范围"""
    with pytest.raises(Exception):
        strategy_engine.backtest(
            sample_data,
            start_date='2021-01-01',  # 超出数据范围
            end_date='2021-12-31'
        )

def test_empty_data(sample_data, strategy_engine):
    """测试空数据"""
    empty_data = pd.DataFrame()
    with pytest.raises(Exception):
        strategy_engine.backtest(
            empty_data,
            start_date='2020-01-01',
            end_date='2020-12-31'
        ) 