from flask import Flask, render_template, request
import pandas as pd
from database import fetch_data_from_db, connect_to_db, disconnect_from_db
import asyncio

# 创建 Flask 应用
app = Flask(__name__)

# 异步获取数据函数
async def query_db(gender, event, min_grade, max_grade):
    await connect_to_db()
    query = f"""
    SELECT * FROM swim_competitions 
    WHERE gender = '{gender}' 
    AND event LIKE '%{event}%'
    AND grade >= {min_grade}
    AND grade <= {max_grade}
    """
    results = await fetch_data_from_db(query)
    await disconnect_from_db()
    return results

# 同步包装异步函数
def get_query_results(gender, event, min_grade, max_grade):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(query_db(gender, event, min_grade, max_grade))
    return results

@app.route('/')
def index():
    return render_template('index.html', title='Swimming Competition Query')

@app.route('/query', methods=['POST'])
def query():
    gender = request.form['gender']
    event = request.form['event']
    min_grade = request.form['min_grade'] or 0
    max_grade = request.form['max_grade'] or 100

    results = get_query_results(gender, event, min_grade, max_grade)
    df = pd.DataFrame(results)
    return render_template('results.html', title='Query Results', results=df.to_dict(orient='records'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
