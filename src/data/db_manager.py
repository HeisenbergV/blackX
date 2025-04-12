from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta
import pandas as pd
from .models import Session as DBSession, StockList, StockDaily, StockRealtime, StockFinancial

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        """初始化数据库管理器"""
        self.session = DBSession()
        
    def __del__(self):
        """关闭数据库连接"""
        self.session.close()
        
    def get_stock_list(self) -> pd.DataFrame:
        """从数据库获取股票列表"""
        try:
            stocks = self.session.query(StockList).all()
            if not stocks:
                return pd.DataFrame()
                
            data = []
            for stock in stocks:
                data.append({
                    'code': stock.code,
                    'name': stock.name
                })
                
            return pd.DataFrame(data)
        except Exception as e:
            print(f"从数据库获取股票列表失败: {e}")
            return pd.DataFrame()
            
    def save_stock_list(self, df: pd.DataFrame):
        """保存股票列表到数据库"""
        try:
            for _, row in df.iterrows():
                stock = StockList(
                    code=row['code'],
                    name=row['name']
                )
                self.session.merge(stock)  # 使用merge而不是add，避免重复
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"保存股票列表失败: {e}")
            
    def get_stock_daily(self, code: str, start_date: str, end_date: str) -> pd.DataFrame:
        """从数据库获取股票日线数据"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
            
            data = self.session.query(StockDaily).filter(
                and_(
                    StockDaily.code == code,
                    StockDaily.date >= start,
                    StockDaily.date <= end
                )
            ).all()
            
            if not data:
                return pd.DataFrame()
                
            records = []
            for d in data:
                records.append({
                    'date': d.date,
                    'open': d.open,
                    'high': d.high,
                    'low': d.low,
                    'close': d.close,
                    'volume': d.volume
                })
                
            return pd.DataFrame(records)
        except Exception as e:
            print(f"从数据库获取股票日线数据失败: {e}")
            return pd.DataFrame()
            
    def save_stock_daily(self, code: str, df: pd.DataFrame):
        """保存股票日线数据到数据库"""
        try:
            for _, row in df.iterrows():
                daily = StockDaily(
                    code=code,
                    date=row['date'],
                    open=row['open'],
                    high=row['high'],
                    low=row['low'],
                    close=row['close'],
                    volume=row['volume']
                )
                self.session.merge(daily)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"保存股票日线数据失败: {e}")
            
    def get_stock_realtime(self, code: str) -> pd.DataFrame:
        """从数据库获取股票实时行情"""
        try:
            data = self.session.query(StockRealtime).filter(
                StockRealtime.code == code
            ).first()
            
            if not data:
                return pd.DataFrame()
                
            return pd.DataFrame([{
                'code': data.code,
                'name': data.name,
                'price': data.price,
                'change': data.change,
                'volume': data.volume
            }])
        except Exception as e:
            print(f"从数据库获取股票实时行情失败: {e}")
            return pd.DataFrame()
            
    def save_stock_realtime(self, df: pd.DataFrame):
        """保存股票实时行情到数据库"""
        try:
            for _, row in df.iterrows():
                realtime = StockRealtime(
                    code=row['code'],
                    name=row['name'],
                    price=row['price'],
                    change=row['change'],
                    volume=row['volume']
                )
                self.session.merge(realtime)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"保存股票实时行情失败: {e}")
            
    def get_stock_financial(self, code: str) -> pd.DataFrame:
        """从数据库获取股票财务数据"""
        try:
            data = self.session.query(StockFinancial).filter(
                StockFinancial.code == code
            ).all()
            
            if not data:
                return pd.DataFrame()
                
            records = []
            for d in data:
                records.append({
                    'code': d.code,
                    'name': d.name,
                    'report_date': d.report_date
                })
                
            return pd.DataFrame(records)
        except Exception as e:
            print(f"从数据库获取股票财务数据失败: {e}")
            return pd.DataFrame()
            
    def save_stock_financial(self, df: pd.DataFrame):
        """保存股票财务数据到数据库"""
        try:
            for _, row in df.iterrows():
                financial = StockFinancial(
                    code=row['code'],
                    name=row['name'],
                    report_date=row['report_date']
                )
                self.session.merge(financial)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            print(f"保存股票财务数据失败: {e}") 