#!/bin/bash

# 设置Python路径
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 运行streamlit应用
streamlit run src/streamlit_app.py 