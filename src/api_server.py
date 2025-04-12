from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import akshare as ak
import pandas as pd
import uvicorn
from pathlib import Path

# 创建 FastAPI 应用
app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建策略目录
STRATEGY_DIR = Path("strategies")
STRATEGY_DIR.mkdir(parents=True, exist_ok=True)

def get_stock_data(code, start_date, end_date):
    """获取股票数据"""
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                               start_date=start_date.strftime("%Y%m%d"),
                               end_date=end_date.strftime("%Y%m%d"))
        df = df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume'
        })
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df
    except Exception as e:
        print(f"获取数据失败: {str(e)}")
        return None

# 股票数据 API
@app.get("/api/stock_data")
async def get_stock_data_api(code: str, start_date: str, end_date: str):
    try:
        # 转换日期格式
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        
        # 获取股票数据
        df = get_stock_data(code, start, end)
        
        if df is None:
            return Response(content="获取数据失败", status_code=400)
            
        # 转换为 JSON
        return {
            "data": df.to_dict(orient="records"),
            "columns": list(df.columns),
            "index": df.index.strftime("%Y-%m-%d").tolist()
        }
    except Exception as e:
        return Response(content=str(e), status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 