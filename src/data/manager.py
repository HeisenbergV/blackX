from typing import Optional
from .fetcher import StockDataFetcher
from .db_manager import DatabaseManager
from .models import init_db
import pandas as pd
from datetime import datetime, timedelta

class StockDataManager:
    def __init__(self):
        """初始化数据管理器"""
        # 初始化数据库
        init_db()
        
        self.fetcher = StockDataFetcher()
        self.db = DatabaseManager()
        self.cache_time = {
            'stock_list': timedelta(days=1),  # 股票列表缓存1天
            'daily': timedelta(days=1),       # 日线数据缓存1天
            'realtime': timedelta(minutes=5), # 实时行情缓存5分钟
            'financial': timedelta(days=7)    # 财务数据缓存7天
        }

    def _is_cache_valid(self, update_time: datetime, cache_type: str) -> bool:
        """检查缓存是否有效"""
        if not update_time:
            return False
        return datetime.now() - update_time < self.cache_time[cache_type]

    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        # 先从数据库获取
        df = self.db.get_stock_list()
        if not df.empty:
            return df
            
        # 如果数据库没有，从API获取
        df = self.fetcher.get_stock_list()
        if not df.empty:
            # 保存到数据库
            self.db.save_stock_list(df)
        return df

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
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            
        # 先从数据库获取
        df = self.db.get_stock_daily(symbol, start_date, end_date)
        if not df.empty:
            return df
            
        # 如果数据库没有，从API获取
        df = self.fetcher.get_stock_daily(symbol, start_date, end_date)
        if not df.empty:
            # 保存到数据库
            self.db.save_stock_daily(symbol, df)
        return df

    def get_stock_realtime(self, symbol: str) -> pd.DataFrame:
        """获取股票实时行情"""
        # 先从数据库获取
        df = self.db.get_stock_realtime(symbol)
        if not df.empty:
            return df
            
        # 如果数据库没有，从API获取
        df = self.fetcher.get_stock_realtime(symbol)
        if not df.empty:
            # 保存到数据库
            self.db.save_stock_realtime(df)
        return df

    def get_stock_financial(self, symbol: str) -> pd.DataFrame:
        """获取股票财务数据"""
        # 先从数据库获取
        df = self.db.get_stock_financial(symbol)
        if not df.empty:
            return df
            
        # 如果数据库没有，从API获取
        df = self.fetcher.get_stock_financial(symbol)
        if not df.empty:
            # 保存到数据库
            self.db.save_stock_financial(df)
        return df 