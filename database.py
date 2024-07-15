import pandas as pd
from databases import Database
from dotenv import load_dotenv
import os

# 加載 .env 文件
load_dotenv()

# 從環境變量中獲取數據庫URL
DATABASE_URL = os.getenv("DATABASE_URL")

# 創建數據庫連接
database = Database(DATABASE_URL)

async def fetch_data_from_db(limit=5):
    # 從數據庫中提取數據
    query = f"SELECT * FROM swim_competitions LIMIT {limit}"
    rows = await database.fetch_all(query)
    # 轉換為 DataFrame 並設置列名
    df = pd.DataFrame([dict(row) for row in rows])
    return df

async def connect_to_db():
    await database.connect()
    print("Database connected successfully")

async def disconnect_from_db():
    await database.disconnect()
    print("Database disconnected successfully")
