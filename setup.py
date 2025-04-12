from setuptools import setup, find_packages

setup(
    name="blackx",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "akshare==1.16.76",
        "backtrader>=1.9.78.123",
        "pandas-ta>=0.3.14b0",
        "pandas==2.2.1",
        "numpy==1.26.4",
        "plotly==5.19.0",
        "fastapi==0.115.12",
        "uvicorn==0.34.0",
        "streamlit==1.32.0",
        "sqlalchemy>=1.4.0",
        "apscheduler>=3.10.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
        "pytest>=7.3.1",
        "python-dateutil>=2.8.0",
        "pyyaml==6.0.1",
        "python-multipart==0.0.9"
    ],
    python_requires=">=3.8",
) 