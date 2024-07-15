import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# 加載 .env 文件
load_dotenv()


# 定義與 Google Gemini API 交互的函數
def interact_with_gemini(prompt):
    model = ChatGoogleGenerativeAI(model="gemini-pro")
    message = HumanMessage(content=[{"type": "text", "text": prompt}])
    response = model.stream([message])

    buffer = []
    for chunk in response:
        buffer.append(chunk.content)
        print(chunk.content)  # 逐步顯示每個chunk的內容

    # 最終顯示完整的響應
    final_output = "".join(buffer)
    print(final_output)


# 測試與 Google Gemini API 交互的函數
# if __name__ == "__main__":
#     prompt = "幫我介紹gemini api的使用方法"
#     interact_with_gemini(prompt)
