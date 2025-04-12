from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class StockInfo:
    """股票基本信息"""
    symbol: str
    name: str
    industry: Optional[str] = None
    update_time: Optional[datetime] = None

@dataclass
class DailyData:
    """股票日线数据"""
    symbol: str
    date: datetime
    open: float
    close: float
    high: float
    low: float
    volume: int
    amount: float
    amplitude: float
    pct_change: float
    change: float
    turnover: float

@dataclass
class FinancialData:
    """股票财务数据"""
    symbol: str
    report_date: datetime
    data_type: str
    value: float

@dataclass
class RealtimeData:
    """股票实时行情数据"""
    symbol: str
    name: str
    price: float
    change: float
    pct_change: float
    volume: int
    amount: float
    high: float
    low: float
    open: float
    pre_close: float
    update_time: datetime 