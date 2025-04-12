from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# 创建数据库目录
db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
os.makedirs(db_dir, exist_ok=True)

# 数据库路径
DB_PATH = os.path.join(db_dir, 'stock_data.db')

# 创建数据库引擎
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)
Base = declarative_base()

class StockList(Base):
    """股票列表"""
    __tablename__ = 'stock_list'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(50), nullable=False)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class StockDaily(Base):
    """股票日线数据"""
    __tablename__ = 'stock_daily'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False)
    date = Column(DateTime, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        # 创建联合唯一索引
        {'sqlite_autoincrement': True},
    )

class StockRealtime(Base):
    """股票实时行情"""
    __tablename__ = 'stock_realtime'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(50))
    price = Column(Float)
    change = Column(Float)
    volume = Column(Float)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class StockFinancial(Base):
    """股票财务数据"""
    __tablename__ = 'stock_financial'
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False)
    name = Column(String(50))
    report_date = Column(DateTime)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    __table_args__ = (
        # 创建联合唯一索引
        {'sqlite_autoincrement': True},
    )

# 创建所有表
def init_db():
    Base.metadata.create_all(engine) 