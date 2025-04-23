# 配置参数
APP_NAME = "apiOfDeepSeek"
VERSION = "1.0.0"

# 数据库配置 -- 这个不写也没事
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    'user': 'root',
    'password': 'root',
    'database': 'miband'
}

# API配置
API_CONFIG = {
    "api_key": "sk-e4c57f9f44c5430ca1dd8eb81b867fe1",
    "base_url": "https://api.deepseek.com"
}

# 服务器配置
SERVER_CONFIG = {
    "host": "0.0.0.0",  # 监听所有网络接口
    "port": 8080,       # 使用8080端口
    "debug": False      # 生产环境关闭调试模式
}