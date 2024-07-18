import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from database import fetch_data_from_db, connect_to_db, disconnect_from_db
import asyncio
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware

# 創建 FastAPI 應用
app = FastAPI()

# 創建 Dash 應用
dash_app = dash.Dash(__name__)


# 從數據庫中提取數據
async def get_data():
    await connect_to_db()
    query = "SELECT * FROM swim_competitions WHERE gender = 'female' LIMIT 100"  # 根據需要修改查詢語句
    df = await fetch_data_from_db(query)
    await disconnect_from_db()
    return df


# 獲取數據並創建圖表
loop = asyncio.get_event_loop()
df = loop.run_until_complete(get_data())

# 創建散點圖
fig = px.scatter(df, x="event_number", y="grade", color="gender", hover_data=["name"])

# 定義 Dash 應用佈局
dash_app.layout = html.Div(
    children=[
        html.H1(children="Swimming Competition Dashboard"),
        dcc.Graph(id="example-graph", figure=fig),
    ]
)

# 將 Dash 應用添加到 FastAPI 應用
app.mount("/dash", WSGIMiddleware(dash_app.server))


# 測試端點
@app.get("/")
async def read_root():
    return {"message": "Hello, this is FastAPI!"}


# 運行應用
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
