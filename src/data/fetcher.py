from abc import ABC, abstractmethod
import akshare as ak
import pandas as pd
from typing import Optional, Dict, List
from datetime import datetime, timedelta

class StockDataFetcherBase(ABC):
    """股票数据获取器基类"""
    
    @abstractmethod
    def get_stock_list(self) -> pd.DataFrame:
        """获取A股股票列表"""
        pass
    
    @abstractmethod
    def get_stock_daily(self, 
                       symbol: str, 
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> pd.DataFrame:
        """获取股票日线数据"""
        pass
    
    @abstractmethod
    def get_stock_realtime(self, symbol: str) -> pd.DataFrame:
        """获取股票实时行情"""
        pass
    
    @abstractmethod
    def get_stock_financial(self, symbol: str) -> pd.DataFrame:
        """获取股票财务数据"""
        pass

class AkshareStockDataFetcher(StockDataFetcherBase):
    """基于Akshare的股票数据获取器实现"""
    
    def __init__(self):
        """初始化数据获取器"""
        self._cache: Dict[str, pd.DataFrame] = {}

    def _clean_symbol(self, symbol: str) -> str:
        """清理股票代码，移除后缀"""
        return symbol.split('.')[0]

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
        """获取股票日线数据"""
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y%m%d')
            
            # 转换日期格式
            start_date = start_date.replace('-', '')
            end_date = end_date.replace('-', '')
            
            # 清理股票代码
            clean_symbol = self._clean_symbol(symbol)
            
            df = ak.stock_zh_a_hist(symbol=clean_symbol, 
                                  start_date=start_date,
                                  end_date=end_date,
                                  adjust="qfq")  # 前复权
            
            if df.empty:
                return df
                
            # 重命名列以保持一致性
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change',
                '换手率': 'turnover'
            }
            
            # 只保留需要的列
            df = df.rename(columns=column_mapping)
            required_columns = ['date', 'open', 'close', 'high', 'low', 'volume']
            df = df[required_columns]
            
            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'])
            
            return df
        except Exception as e:
            print(f"获取股票 {symbol} 日线数据失败: {e}")
            return pd.DataFrame()

    def get_stock_realtime(self, symbol: str) -> pd.DataFrame:
        """获取股票实时行情"""
        try:
            # 清理股票代码
            clean_symbol = self._clean_symbol(symbol)
            
            # 使用更稳定的API
            df = ak.stock_zh_a_spot()
            if df.empty:
                return df
                
            # 重命名列
            column_mapping = {
                '代码': 'code',
                '名称': 'name',
                '最新价': 'price',
                '涨跌幅': 'change',
                '成交量': 'volume'
            }
            
            # 筛选并重命名列
            df = df[df['代码'] == clean_symbol]
            if df.empty:
                return df
                
            df = df.rename(columns=column_mapping)
            required_columns = ['code', 'name', 'price', 'change', 'volume']
            df = df[required_columns]
            
            return df
        except Exception as e:
            print(f"获取股票 {symbol} 实时行情失败: {e}")
            # 尝试使用备用API
            try:
                df = ak.stock_zh_a_spot_em()
                if df.empty:
                    return df
                    
                df = df[df['代码'] == clean_symbol]
                if df.empty:
                    return df
                    
                df = df.rename(columns=column_mapping)
                df = df[required_columns]
                return df
            except Exception as e2:
                print(f"获取股票 {symbol} 实时行情失败(备用API): {e2}")
                return pd.DataFrame()

    def get_stock_financial(self, symbol: str) -> pd.DataFrame:
        """获取股票财务数据"""
        try:
            # 清理股票代码
            clean_symbol = self._clean_symbol(symbol)
            
            # 使用更可靠的API
            df = ak.stock_financial_analysis_indicator(symbol=clean_symbol)
            if df.empty:
                return df
                
            # 重命名列
            column_mapping = {
                '股票代码': 'code',
                '股票简称': 'name',
                '报告期': 'report_date'
            }
            
            df = df.rename(columns=column_mapping)
            required_columns = ['code', 'name', 'report_date']
            df = df[required_columns]
            
            return df
        except Exception as e:
            print(f"获取股票 {symbol} 财务数据失败: {e}")
            # 尝试使用备用API
            try:
                # 获取最近一年的财务数据
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
                
                df = ak.stock_financial_analysis_indicator_em(symbol=clean_symbol)
                if df.empty:
                    return df
                    
                df = df.rename(columns=column_mapping)
                df = df[required_columns]
                return df
            except Exception as e2:
                print(f"获取股票 {symbol} 财务数据失败(备用API): {e2}")
                return pd.DataFrame()

# 默认使用Akshare实现
StockDataFetcher = AkshareStockDataFetcher 