import datetime
import random
import os

# 模擬 AI 生成（可替換為 xAI API）
def generate_insight():
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    topics = [
        "房市新聞：最新成交量數據解析",
        "政策影響：政府打炒房措施更新",
        "國際經濟：美元走勢對台灣房市的影響"
    ]
    title = random.choice(topics)
    content = """
    今日房市數據顯示，台北市成交量下跌 5%，專家分析與新政策有關。
    同時，國際原油價格上漲可能推高建築成本，影響未來房價走勢。
    每日洞見將持續追蹤最新動態！
    """
    return date, title, content

def save_insight():
    date, title, content = generate_insight()
    filename = f"content/posts/insight-{date[:10]}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"""---title: "{title}"
        date: {date}
        draft: false
        {content}
        """)
        print(f"Generated: {filename}")

if __name__ == '__main__':
    save_insight()

