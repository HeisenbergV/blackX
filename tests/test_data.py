import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from datetime import datetime, timedelta
from src.data.manager import StockDataManager

def test_stock_list():
    """测试获取股票列表功能"""
    manager = StockDataManager()
    stock_list = manager.get_stock_list()
    
    # 验证返回的是DataFrame
    assert isinstance(stock_list, pd.DataFrame)
    # 验证DataFrame不为空
    assert not stock_list.empty
    # 验证包含必要的列
    required_columns = ['code', 'name']
    assert all(col in stock_list.columns for col in required_columns)

def test_stock_daily():
    """测试获取日线数据功能"""
    manager = StockDataManager()
    
    # 设置测试时间范围
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    # 获取平安银行（000001.SZ）的数据
    df = manager.get_stock_daily("000001.SZ", start_date, end_date)
    
    # 验证返回的是DataFrame
    assert isinstance(df, pd.DataFrame)
    # 验证DataFrame不为空
    assert not df.empty
    # 验证包含必要的列
    required_columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    assert all(col in df.columns for col in required_columns)
    # 验证数据类型
    assert pd.api.types.is_datetime64_any_dtype(df['date'])
    assert pd.api.types.is_numeric_dtype(df['close'])

def test_stock_realtime():
    """测试获取实时行情功能"""
    manager = StockDataManager()
    realtime = manager.get_stock_realtime("000001.SZ")
    
    # 验证返回的是DataFrame
    assert isinstance(realtime, pd.DataFrame)
    # 验证DataFrame不为空
    assert not realtime.empty
    # 验证包含必要的列
    required_columns = ['code', 'name', 'price', 'change', 'volume']
    assert all(col in realtime.columns for col in required_columns)

def test_stock_financial():
    """测试获取财务数据功能"""
    manager = StockDataManager()
    financial = manager.get_stock_financial("000001.SZ")
    
    # 验证返回的是DataFrame
    assert isinstance(financial, pd.DataFrame)
    # 验证DataFrame不为空
    assert not financial.empty
    # 验证包含必要的列
    required_columns = ['code', 'name', 'report_date']
    assert all(col in financial.columns for col in required_columns) 