import sys
from pathlib import Path

# 添加项目根目录到系统路径
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from src.data.manager import StockDataManager
import pandas as pd
from datetime import datetime, timedelta

def test_stock_data():
    """测试股票数据获取功能"""
    print("开始测试股票数据功能...")
    
    # 创建数据管理器实例
    manager = StockDataManager()
    
    # 1. 测试获取股票列表
    print("\n1. 测试获取股票列表...")
    stock_list = manager.get_stock_list()
    print(f"获取到 {len(stock_list)} 只股票")
    if not stock_list.empty:
        print("\n股票列表示例：")
        print(stock_list.head())
    
    # 2. 测试获取日线数据
    print("\n2. 测试获取日线数据...")
    # 获取平安银行（000001）最近一年的数据
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    df = manager.get_stock_daily("000001", start_date, end_date)
    print(f"获取到 {len(df)} 条日线数据")
    if not df.empty:
        print("\n数据示例：")
        print(df.head())
        print("\n数据统计：")
        print(df.describe())
    
    # 3. 测试获取实时行情
    print("\n3. 测试获取实时行情...")
    realtime = manager.get_stock_realtime("000001")
    if not realtime.empty:
        print("\n实时行情数据：")
        print(realtime)
    
    # 4. 测试获取财务数据
    print("\n4. 测试获取财务数据...")
    financial = manager.get_stock_financial("000001")
    if not financial.empty:
        print("\n财务数据示例：")
        print(financial.head())
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_stock_data() 