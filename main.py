import asyncio
from database import fetch_data_from_db, connect_to_db, disconnect_from_db
from gemini import interact_with_gemini

async def main():
    # 打開數據庫連接
    await connect_to_db()

    # 從數據庫中提取數據
    df = await fetch_data_from_db(limit=5)
    print("Database Data:")
    print(df)

    # 將數據庫中的每條記錄作為提示傳遞給 Gemini API
    for index, row in df.iterrows():
        prompt = f"請介紹一下 {row['name']} 在 {row['competition_event']} 的比賽成績 {row['grade']}。"
        print(f"Prompt: {prompt}")
        response = interact_with_gemini(prompt)
        print("LangChain Response:")
        print(response)

    # 關閉數據庫連接
    await disconnect_from_db()

if __name__ == "__main__":
    asyncio.run(main())
