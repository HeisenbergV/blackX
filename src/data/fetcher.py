import akshare as ak
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, timedelta

class StockDataFetcher:
    def __init__(self):
        """初始化数据获取器"""
        self._cache: Dict[str, pd.DataFrame] = {}

    def get_stock_list(self) -> pd.DataFrame:
        """获取A股股票列表"""
        try:
            return ak.stock_info_a_code_name()
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return pd.DataFrame()

    def get_stock_daily(self, 
                       symbol: str, 
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> pd.DataFrame:
        """获取股票日线数据
        
        Args:
            symbol: 股票代码（如：000001）
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
        """
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            
            # 转换日期格式
            start_date = start_date.replace('-', '')
            end_date = end_date.replace('-', '')
            
            df = ak.stock_zh_a_hist(symbol=symbol, 
                                  start_date=start_date,
                                  end_date=end_date,
                                  adjust="qfq")  # 前复权
            
            # 重命名列以保持一致性
            df.columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'amplitude', 
                         'pct_change', 'change', 'turnover']
            
            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'])
            
            return df
        except Exception as e:
            print(f"获取股票 {symbol} 日线数据失败: {e}")
            return pd.DataFrame()

    def get_stock_realtime(self, symbol: str) -> pd.DataFrame:
        """获取股票实时行情"""
        try:
            df = ak.stock_zh_a_spot_em()
            return df[df['代码'] == symbol]
        except Exception as e:
            print(f"获取股票 {symbol} 实时行情失败: {e}")
            return pd.DataFrame()

    def get_stock_financial(self, symbol: str) -> pd.DataFrame:
        """获取股票财务数据"""
        try:
            return ak.stock_financial_report_sina(symbol=symbol)
        except Exception as e:
            print(f"获取股票 {symbol} 财务数据失败: {e}")
            return pd.DataFrame() 