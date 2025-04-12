import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
from src.indicators import MovingAverage, RSI, MACD

def test_moving_average():
    # 创建测试数据
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    })
    
    # 测试简单移动平均
    ma = MovingAverage(window=3, ma_type='SMA')
    result = ma.calculate(data)
    assert len(result) == len(data)
    assert pd.isna(result[0])  # 第一个值应该是NaN
    assert pd.isna(result[1])  # 第二个值应该是NaN
    assert result[2] == 11  # (10+11+12)/3
    
    # 测试指数移动平均
    ma = MovingAverage(window=3, ma_type='EMA')
    result = ma.calculate(data)
    assert len(result) == len(data)
    # EMA的第一个值应该等于第一个收盘价
    assert result[0] == data['close'][0]
    # 检查EMA值是否在合理范围内
    assert result[1] > data['close'][0] and result[1] < data['close'][1]

def test_rsi():
    # 创建测试数据
    data = pd.DataFrame({
        'close': [10, 12, 11, 13, 12, 14, 13, 15, 14, 16]
    })
    
    rsi = RSI(period=3)
    result = rsi.calculate(data)
    
    assert len(result) == len(data)
    assert not result[:2].notna().any()  # 前两个值应该是NaN
    assert 0 <= result.iloc[-1] <= 100  # RSI值应该在0-100之间

def test_macd():
    # 创建测试数据
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    })
    
    macd = MACD(fast_period=3, slow_period=5, signal_period=2)
    result = macd.calculate(data)
    
    assert isinstance(result, pd.DataFrame)
    assert 'macd_line' in result.columns
    assert 'signal_line' in result.columns
    assert 'histogram' in result.columns
    assert len(result) == len(data)

def test_custom_indicator():
    # 测试自定义指标
    class CustomIndicator(MovingAverage):
        def calculate(self, data):
            return super().calculate(data) * 2
    
    data = pd.DataFrame({
        'close': [10, 11, 12, 13, 14]
    })
    
    indicator = CustomIndicator(window=2)
    result = indicator.calculate(data)
    
    assert len(result) == len(data)
    assert result[1] == 21  # (10+11)*2 