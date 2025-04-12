import pandas as pd
from typing import Dict, Any, Optional

class TechnicalIndicator:
    """技术指标基类"""
    
    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        self.name = name
        self.params = params or {}
        
    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """计算指标值
        
        Args:
            data: 包含OHLCV数据的DataFrame
            
        Returns:
            计算后的指标值Series
        """
        raise NotImplementedError("子类必须实现calculate方法")
        
    def __str__(self) -> str:
        return f"{self.name}({', '.join(f'{k}={v}' for k, v in self.params.items())})" 