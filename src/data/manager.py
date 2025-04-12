from typing import Optional
from .fetcher import StockDataFetcher
import pandas as pd

class StockDataManager:
    def __init__(self):
        """初始化数据管理器"""
        self.fetcher = StockDataFetcher()

    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        return self.fetcher.get_stock_list()

    def get_stock_daily(self, 
                       symbol: str, 
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> pd.DataFrame:
        """获取股票日线数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
        """
        return self.fetcher.get_stock_daily(symbol, start_date, end_date)

    def get_stock_realtime(self, symbol: str) -> pd.DataFrame:
        """获取股票实时行情"""
        return self.fetcher.get_stock_realtime(symbol)

    def get_stock_financial(self, symbol: str) -> pd.DataFrame:
        """获取股票财务数据"""
        return self.fetcher.get_stock_financial(symbol) 