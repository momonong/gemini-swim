import asyncio
from flask import Flask, render_template, request
from flask_caching import Cache
import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

# 从环境变量中获取数据库URL
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")

# 创建 Flask 应用
server = Flask(__name__, template_folder='templates', static_folder='static')

# 配置缓存
cache = Cache(server, config={"CACHE_TYPE": "simple"})

# 创建 Dash 应用
app = dash.Dash(__name__, server=server, url_base_pathname="/dash/")

# 创建异步引擎和会话
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 从数据库中提取数据并缓存
@cache.cached(timeout=60, key_prefix="all_swim_data")
def get_data_sync():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(get_data())

async def get_data():
    async with async_session() as session:
        query = text("SELECT * FROM swim_competitions WHERE gender = '女生' LIMIT 100")
        result = await session.execute(query)
        rows = result.fetchall()
    return [dict(row) for row in rows]

# 获取数据并创建图表
json_data = get_data_sync()
df = pd.DataFrame(json_data)

def create_figures(df):
    scatter_fig = px.scatter(
        df, x="event_number", y="grade", color="gender", hover_data=["name"]
    )
    bar_fig = px.bar(df, x="event_number", y="grade", color="gender", hover_data=["name"])
    line_fig = px.line(df, x="event_number", y="grade", color="gender", hover_data=["name"])
    return scatter_fig, bar_fig, line_fig

scatter_fig, bar_fig, line_fig = create_figures(df)

# 定义 Dash 应用布局
app.layout = html.Div(
    children=[
        html.H1(children="Swimming Competition Dashboard"),
        html.Div(
            [
                html.Label("Select Gender"),
                dcc.Dropdown(
                    id="gender-dropdown",
                    options=[{"label": i, "value": i} for i in df["gender"].unique()],
                    value="女生",
                ),
            ]
        ),
        dcc.Graph(id="scatter-graph", figure=scatter_fig),
        dcc.Graph(id="bar-graph", figure=bar_fig),
        dcc.Graph(id="line-graph", figure=line_fig),
    ]
)

# 更新图表的回调
@app.callback(
    [
        dash.dependencies.Output("scatter-graph", "figure"),
        dash.dependencies.Output("bar-graph", "figure"),
        dash.dependencies.Output("line-graph", "figure"),
    ],
    [dash.dependencies.Input("gender-dropdown", "value")],
)
def update_graph(selected_gender):
    filtered_df = df[df["gender"] == selected_gender]
    scatter_fig, bar_fig, line_fig = create_figures(filtered_df)
    return scatter_fig, bar_fig, line_fig

# 异步获取数据函数
async def query_db(gender, event, min_grade, max_grade):
    async with async_session() as session:
        query = text(f"""
        SELECT * FROM swim_competitions 
        WHERE gender = '{gender}' 
        AND comptetion_event LIKE '%{event}%'
        AND grade >= '{min_grade}'
        AND grade <= '{max_grade}'
        """)
        result = await session.execute(query)
        rows = result.fetchall()
    return [dict(row) for row in rows]

# 同步包装异步函数
def get_query_results(gender, event, min_grade, max_grade):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(query_db(gender, event, min_grade, max_grade))
    return results

# 定义 Flask 路由
@server.route('/')
def index():
    return render_template('index.html', title='Swimming Competition Dashboard')

@server.route('/query_page')
def query_page():
    return render_template('query.html', title='Swimming Competition Query')

@server.route('/query', methods=['POST'])
def query():
    gender = request.form['gender']
    event = request.form['event']
    min_grade = request.form['min_grade'] or '00:00:00.00'
    max_grade = request.form['max_grade'] or '99:59:59.99'

    results = get_query_results(gender, event, min_grade, max_grade)
    df = pd.DataFrame(results)
    return render_template('results.html', title='Query Results', results=df.to_dict(orient='records'))

# 运行应用
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000, debug=True)
