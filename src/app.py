import streamlit as st
import akshare as ak
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 设置页面配置
st.set_page_config(
    page_title="股票分析系统",
    page_icon="📈",
    layout="wide"
)

# 设置页面标题
st.title("股票分析系统")

# 侧边栏
st.sidebar.header("股票查询")
stock_code = st.sidebar.text_input("输入股票代码（例如：000001）", "000001")
start_date = st.sidebar.date_input("开始日期", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("结束日期", datetime.now())

# 获取股票数据
@st.cache_data
def get_stock_data(code, start, end):
    try:
        df = ak.stock_zh_a_hist(symbol=code, start_date=start.strftime("%Y%m%d"), 
                               end_date=end.strftime("%Y%m%d"), adjust="qfq")
        return df
    except Exception as e:
        st.error(f"获取数据失败: {str(e)}")
        return None

# 显示股票数据
if st.sidebar.button("查询"):
    with st.spinner("正在获取数据..."):
        df = get_stock_data(stock_code, start_date, end_date)
        
        if df is not None:
            # 显示数据表格
            st.subheader("股票数据")
            st.dataframe(df)
            
            # 绘制K线图
            st.subheader("K线图")
            fig = go.Figure(data=[go.Candlestick(
                x=df['日期'],
                open=df['开盘'],
                high=df['最高'],
                low=df['最低'],
                close=df['收盘']
            )])
            fig.update_layout(
                title=f"股票 {stock_code} K线图",
                xaxis_title="日期",
                yaxis_title="价格",
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # 显示基本统计信息
            st.subheader("基本统计信息")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("最高价", f"{df['最高'].max():.2f}")
            with col2:
                st.metric("最低价", f"{df['最低'].min():.2f}")
            with col3:
                st.metric("平均价", f"{df['收盘'].mean():.2f}")
            with col4:
                st.metric("成交量", f"{df['成交量'].sum():,.0f}")

# 添加页脚
st.markdown("---")
st.markdown("© 2024 股票分析系统") 