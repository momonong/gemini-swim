import pandas as pd
from databases import Database
from dotenv import load_dotenv
import os
import json

# 加載 .env 文件
load_dotenv()

# 從環境變量中獲取數據庫URL
DATABASE_URL = os.getenv("DATABASE_URL")

# 創建數據庫連接
database = Database(DATABASE_URL)


async def fetch_data_from_db(query="SELECT * FROM swim_competitions LIMIT 5"):
    # 從數據庫中提取數據
    rows = await database.fetch_all(query)
    # 轉換為 JSON 格式
    json_data = [dict(row) for row in rows]
    return json_data


async def connect_to_db():
    await database.connect()
    print("Database connected successfully")


async def disconnect_from_db():
    await database.disconnect()
    print("Database disconnected successfully")
