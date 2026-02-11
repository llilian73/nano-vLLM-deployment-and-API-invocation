import requests
import re

# 你的服务器地址
SERVER_URL = "https://u835453-9783-227d6635.bjb1.seetacloud.com:8443/chat"


def chat_once(prompt):
    data = {"prompt": prompt}
    try:
        print("Waiting for response...", end="", flush=True)  # 提示正在生成
        response = requests.post(SERVER_URL, json=data)
        response.raise_for_status()

        result = response.json()
        raw_text = result['response']

        # --- 清洗数据 (移除 <think> 和 <|im_end|>) ---
        # 如果你想看思考过程，把下面这行注释掉即可
        clean_text = re.sub(r'<think>.*?</think>', '', raw_text, flags=re.DOTALL)
        clean_text = clean_text.replace('<|im_end|>', '').strip()

        # 打印回车把 "Waiting..." 顶掉
        print("\r" + " " * 20 + "\r", end="")
        print(f"🤖 AI: {clean_text}\n")

    except Exception as e:
        print(f"\n❌ 出错了: {e}")


if __name__ == "__main__":
    print("=== 本地 AI 聊天终端 (输入 'exit' 或 'q' 退出) ===")

    while True:
        # 这里就是让你输入的地方
        user_input = input("👉 你: ")

        if user_input.lower() in ['exit', 'quit', 'q']:
            print("再见！")
            break

        if not user_input.strip():
            continue

        # 发送给模型
        chat_once(user_input)