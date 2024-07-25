from flask import Flask
from flask_caching import Cache

# 创建 Flask 应用
app = Flask(__name__, template_folder='templates', static_folder='static')

# 配置缓存
cache = Cache(app, config={"CACHE_TYPE": "simple"})

from src import routes  # 导入路由
