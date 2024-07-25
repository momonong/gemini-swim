import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 从环境变量中获取数据库URL，并确保使用 asyncpg 驱动
DATABASE_URL = os.getenv("DATABASE_URL").replace(
    "postgresql://", "postgresql+asyncpg://"
)

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def fetch_data_from_db(query):
    async with AsyncSessionLocal() as session:
        result = await session.execute(text(query))  # 使用 text 函数来包装查询
        rows = result.fetchall()
        json_data = [
            dict(row._mapping) for row in rows
        ]  # 使用 row._mapping 确保正确转换为字典
        return json_data


async def connect_to_db():
    async with engine.begin() as conn:
        # 如果有模型定义，可以在这里创建表结构
        # await conn.run_sync(Base.metadata.create_all)
        pass
    print("Database connected successfully")


async def disconnect_from_db():
    await engine.dispose()
    print("Database disconnected successfully")
