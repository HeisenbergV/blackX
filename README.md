# 股票分析系统

## 系统简介
一个基于 Python 的股票分析系统，支持 A 股数据获取、技术分析、策略回测等功能。系统采用 Docker 容器化部署，支持一键启动。

## 系统要求
- Docker
- Docker Compose
- 4GB 以上内存
- 2核以上 CPU

## 功能特点
1. 数据获取
   - 支持 A 股实时和历史数据获取
   - 支持多种数据源（akshare）
   - 自动数据缓存和更新

2. 技术分析
   - 支持常用技术指标计算（MA、RSI、MACD 等）
   - 支持自定义指标
   - 实时数据可视化

3. 策略回测
   - 支持多策略组合回测
   - 支持自定义策略导入
   - 详细的回测报告和图表

4. 系统架构
   - 前端：Streamlit 交互式界面
   - 后端：FastAPI 高性能 API
   - 数据：SQLite 轻量级数据库

## 快速部署

### 1. 环境准备
```bash
# 安装 Docker
curl -fsSL https://get.docker.com | bash -s docker

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 获取代码
```bash
git clone [您的代码库地址]
cd [代码库目录]
```

### 3. 启动服务
```bash
# 首次启动（包含构建镜像）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 访问服务
- Web界面: http://localhost:8501
- API服务: http://localhost:8000

## 使用说明

### 1. 数据查看
- 在 Web 界面选择股票代码和时间范围
- 查看 K 线图和技术指标
- 导出数据为 CSV 格式

### 2. 策略回测
- 选择或导入交易策略
- 设置回测参数
- 查看回测结果和图表
- 导出回测报告

### 3. API 使用
```bash
# 获取股票数据
curl "http://localhost:8000/api/stock_data?code=000001&start_date=20240301&end_date=20240331"

# 更多 API 文档请访问 http://localhost:8000/docs
```

## 目录结构
```
.
├── src/                    # 源代码目录
│   ├── api_server.py       # API 服务
│   ├── streamlit_app.py    # Web 界面
│   └── strategies/         # 策略文件
├── data/                   # 数据目录
├── docker-compose.yml      # Docker 编排文件
├── Dockerfile             # Docker 构建文件
└── requirements.txt       # Python 依赖
```

## 常见问题

1. 服务启动失败
   - 检查端口是否被占用
   - 检查 Docker 是否正常运行
   - 查看日志：`docker-compose logs -f`

2. 数据获取失败
   - 检查网络连接
   - 确认股票代码是否正确
   - 检查 API 服务是否正常运行

3. 策略导入失败
   - 检查策略文件格式
   - 确认文件权限
   - 查看错误日志

## 维护说明

### 更新服务
```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose up -d --build
```

### 备份数据
```bash
# 备份数据目录
tar -czvf data_backup.tar.gz data/
```

### 清理系统
```bash
# 停止并删除容器
docker-compose down

# 删除未使用的镜像
docker image prune -a
```
