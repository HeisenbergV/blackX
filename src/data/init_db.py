from .models import init_db

def main():
    """初始化数据库"""
    print("正在初始化数据库...")
    init_db()
    print("数据库初始化完成！")

if __name__ == "__main__":
    main() 