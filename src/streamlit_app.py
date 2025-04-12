import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.backtest.strategy_engine import StrategyEngine
import akshare as ak
import numpy as np
import yaml
import os
from pathlib import Path

# 设置页面配置
st.set_page_config(
    page_title="股票分析系统",
    page_icon="📈",
    layout="wide"
)

# 创建策略目录
STRATEGY_DIR = Path("strategies")
STRATEGY_DIR.mkdir(parents=True, exist_ok=True)

# 加载所有策略配置
def load_all_strategies():
    """加载所有策略配置"""
    strategies = {}
    
    # 从 user_strategies 目录加载所有策略
    for strategy_file in STRATEGY_DIR.glob("*.y*ml"):  # 支持 .yaml 和 .yml
        with open(strategy_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            strategies.update(config.get('strategies', {}))
    
    return strategies

# 保存用户策略
def save_user_strategy(file_content, filename):
    """保存用户上传的策略"""
    file_path = STRATEGY_DIR / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(file_content)
    return file_path

# 创建侧边栏导航
st.sidebar.title("导航")
page = st.sidebar.radio(
    "选择功能",
    ["股票数据查看", "策略回测", "策略管理"]
)

# 股票选择（共用）
st.sidebar.header("股票选择")
stock_code = st.sidebar.text_input("输入股票代码（例如：000001）", "000001")
stock_name = st.sidebar.text_input("输入股票名称", "平安银行")

# 日期选择（共用）
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input(
        "开始日期",
        datetime.now() - timedelta(days=365)
    )
with col2:
    end_date = st.date_input(
        "结束日期",
        datetime.now()
    )

# 获取股票数据（共用）
@st.cache_data
def get_stock_data(code, start_date, end_date):
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
        st.error(f"获取数据失败: {str(e)}")
        return None

# 获取数据
data = get_stock_data(stock_code, start_date, end_date)

if data is not None:
    if page == "股票数据查看":
        # 显示股票数据
        st.title(f"{stock_name}({stock_code}) 股票数据")
        
        # 显示基本信息
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("当前价格", f"{data['close'].iloc[-1]:.2f}")
        with col2:
            change = (data['close'].iloc[-1] / data['close'].iloc[-2] - 1) * 100
            st.metric("涨跌幅", f"{change:.2f}%")
        with col3:
            st.metric("最高价", f"{data['high'].max():.2f}")
        with col4:
            st.metric("最低价", f"{data['low'].min():.2f}")
        
        # 绘制K线图
        fig = go.Figure(data=[go.Candlestick(
            x=data.index,
            open=data['open'],
            high=data['high'],
            low=data['low'],
            close=data['close']
        )])
        
        fig.update_layout(
            title="K线图",
            xaxis_title="日期",
            yaxis_title="价格",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示数据表格
        st.subheader("历史数据")
        st.dataframe(data)
        
    elif page == "策略回测":
        st.title("策略回测系统")
        
        # 加载所有策略
        all_strategies = load_all_strategies()
        
        # 策略选择
        st.sidebar.header("策略配置")
        strategy_names = [f"{name} ({config['name']})" 
                         for name, config in all_strategies.items()]
        selected_strategy_names = st.sidebar.multiselect(
            "选择策略",
            strategy_names,
            default=[strategy_names[0]] if strategy_names else []
        )
        
        if st.sidebar.button("开始回测"):
            # 初始化策略引擎
            engine = StrategyEngine()  # 不指定配置文件，自动加载所有策略
            
            # 执行回测
            results = engine.backtest(
                data,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
            )
            
            # 创建标签页
            tab1, tab2, tab3 = st.tabs(["策略收益", "持仓变化", "交易信号"])
            
            with tab1:
                # 绘制收益曲线
                fig = go.Figure()
                
                # 添加基准收益（股票本身）
                stock_returns = (data['close'] / data['close'].iloc[0] - 1) * 100
                fig.add_trace(go.Scatter(
                    x=stock_returns.index,
                    y=stock_returns,
                    name="基准收益",
                    line=dict(color="gray")
                ))
                
                # 添加策略收益
                for strategy in selected_strategy_names:
                    strategy_name = strategy.split(' ')[0]
                    if strategy_name in results:
                        strategy_returns = (1 + results[strategy_name]['returns']).cumprod() * 100
                        fig.add_trace(go.Scatter(
                            x=strategy_returns.index,
                            y=strategy_returns,
                            name=strategy
                        ))
                
                fig.update_layout(
                    title="策略收益对比",
                    xaxis_title="日期",
                    yaxis_title="累计收益(%)",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # 显示策略统计信息
                st.subheader("策略统计")
                stats_data = []
                for strategy in selected_strategy_names:
                    strategy_name = strategy.split(' ')[0]
                    if strategy_name in results:
                        returns = results[strategy_name]['returns']
                        total_return = (1 + returns).prod() - 1
                        annual_return = (1 + total_return) ** (252/len(returns)) - 1
                        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
                        
                        stats_data.append({
                            "策略": strategy,
                            "总收益": f"{total_return:.2%}",
                            "年化收益": f"{annual_return:.2%}",
                            "夏普比率": f"{sharpe_ratio:.2f}"
                        })
                
                st.dataframe(pd.DataFrame(stats_data))
            
            with tab2:
                # 绘制持仓变化
                fig = go.Figure()
                
                for strategy in selected_strategy_names:
                    strategy_name = strategy.split(' ')[0]
                    if strategy_name in results:
                        positions = results[strategy_name]['positions']
                        fig.add_trace(go.Scatter(
                            x=positions.index,
                            y=positions['position'],
                            name=strategy,
                            line=dict(width=2)
                        ))
                
                fig.update_layout(
                    title="策略持仓变化",
                    xaxis_title="日期",
                    yaxis_title="持仓比例",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                # 绘制交易信号
                fig = go.Figure()
                
                # 添加价格
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data['open'],
                    high=data['high'],
                    low=data['low'],
                    close=data['close'],
                    name="K线"
                ))
                
                # 添加交易信号
                for strategy in selected_strategy_names:
                    strategy_name = strategy.split(' ')[0]
                    if strategy_name in results:
                        signals = results[strategy_name]['signals']
                        buy_signals = signals[signals['signal'] == 1]
                        sell_signals = signals[signals['signal'] == -1]
                        
                        fig.add_trace(go.Scatter(
                            x=buy_signals.index,
                            y=data.loc[buy_signals.index, 'low'] * 0.98,
                            mode='markers',
                            marker=dict(symbol='triangle-up', size=10, color='green'),
                            name=f"{strategy}买入信号"
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=sell_signals.index,
                            y=data.loc[sell_signals.index, 'high'] * 1.02,
                            mode='markers',
                            marker=dict(symbol='triangle-down', size=10, color='red'),
                            name=f"{strategy}卖出信号"
                        ))
                
                fig.update_layout(
                    title="交易信号",
                    xaxis_title="日期",
                    yaxis_title="价格",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
            
    else:  # 策略管理页面
        st.title("策略管理")
        
        # 策略导入
        st.header("导入策略")
        uploaded_file = st.file_uploader("上传策略配置文件（YAML格式）", type=['yaml', 'yml'])
        
        if uploaded_file is not None:
            try:
                # 读取文件内容
                file_content = uploaded_file.getvalue().decode('utf-8')
                
                # 验证YAML格式
                yaml.safe_load(file_content)
                
                # 保存文件
                filename = uploaded_file.name
                save_path = save_user_strategy(file_content, filename)
                
                st.success(f"策略文件已成功导入：{save_path}")
                
                # 显示策略预览
                st.subheader("策略预览")
                st.code(file_content, language='yaml')
                
            except yaml.YAMLError as e:
                st.error(f"YAML格式错误：{str(e)}")
            except Exception as e:
                st.error(f"导入失败：{str(e)}")
        
        # 显示现有策略
        st.header("现有策略")
        all_strategies = load_all_strategies()
        
        for strategy_id, strategy_config in all_strategies.items():
            with st.expander(f"{strategy_config['name']} ({strategy_id})"):
                st.write(f"描述: {strategy_config.get('description', '无描述')}")
                st.write("参数:")
                st.json(strategy_config.get('parameters', {}))
                
                # 添加删除按钮
                if st.button(f"删除策略 {strategy_config['name']}", key=f"delete_{strategy_id}"):
                    # 找到并删除对应的策略文件
                    for strategy_file in STRATEGY_DIR.glob("*.y*ml"):
                        with open(strategy_file, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f)
                            if strategy_id in config.get('strategies', {}):
                                os.remove(strategy_file)
                                st.success(f"已删除策略: {strategy_config['name']}")
                                st.rerun()  # 使用新的 rerun API 