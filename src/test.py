from flask import Flask, render_template, request
import pandas as pd
from database import fetch_data_from_db, connect_to_db, disconnect_from_db
import asyncio
import datetime

# 创建 Flask 应用
app = Flask(__name__)

# 异步获取数据函数
async def query_db(competition_name, name, event_number, unit_name, competition_event, competition_category):
    await connect_to_db()

    # 动态生成查询条件
    conditions = ["1=1"]  # 使用 1=1 作为占位符，确保后续添加条件时语法正确
    conditions.append(f"competition_name LIKE '%{competition_name}%'")
    conditions.append(f"name LIKE '%{name}%'")
    if event_number:
        conditions.append(f"event_number = {event_number}")
    if unit_name:
        conditions.append(f"unit_name LIKE '%{unit_name}%'")
    if competition_event:
        conditions.append(f"competition_event LIKE '%{competition_event}%'")
    if competition_category:
        conditions.append(f"competition_category LIKE '%{competition_category}%'")

    # 组合查询条件
    condition_str = " AND ".join(conditions)
    query = f"SELECT * FROM swim_competitions WHERE {condition_str}"

    results = await fetch_data_from_db(query)
    await disconnect_from_db()
    return results

# 同步包装异步函数
def get_query_results(competition_name, name, event_number, unit_name, competition_event, competition_category):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(
        query_db(competition_name, name, event_number, unit_name, competition_event, competition_category)
    )

    # 处理比賽成績字段和狀態字段
    for result in results:
        grade = result["grade"]
        if grade is None:
            result["grade"] = ""
        elif isinstance(grade, (int, float)):
            result["grade"] = f"{grade:.2f}"
        elif isinstance(grade, str):
            try:
                result["grade"] = f"{float(grade):.2f}"
            except ValueError:
                result["grade"] = grade
        elif isinstance(grade, datetime.time):
            result["grade"] = grade.strftime("%H:%M:%S.%f")[:-4]
        else:
            result["grade"] = str(grade)

        # 处理狀態字段
        if result["status"] is None:
            result["status"] = ""

    return results

@app.route("/")
def index():
    return render_template("index.html", title="Swimming Competition Dashboard")

@app.route("/query", methods=["GET", "POST"])
def query():
    if request.method == "POST":
        competition_name = request.form["competition_name"]
        name = request.form["name"]
        event_number = request.form.get("event_number")
        unit_name = request.form.get("unit_name")
        competition_event = request.form.get("competition_event")
        competition_category = request.form.get("competition_category")

        results = get_query_results(
            competition_name, name, event_number, unit_name, competition_event, competition_category
        )
        df = pd.DataFrame(results)
        return render_template(
            "results.html", title="Query Results", results=df.to_dict(orient="records")
        )
    return render_template("query.html", title="Swimming Competition Query")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
