import datetime
import os


def generate_insight():
    """
    生成房市分析文章的內容，包括日期、標題和正文。
    
    Returns:
        tuple: (date, title, content) - 日期、標題和文章內容
    """
    # 獲取當前日期並格式化
    current_date = datetime.datetime.now()
    date = current_date.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    title = f"{current_date.strftime('%Y-%m-%d')} 房市黑天鵝來襲？台中房市現況與今日價格波動分析"

    # 文章內容
    content = """
### 測試
"""

    print("Starting insight generation...")
    return date, title, content


def save_insight():
    """
    將生成的房市分析文章保存為 Markdown 檔案。
    檔案將保存到 content/posts/ 目錄下，檔名格式為 insight-YYYY-MM-DD.md。
    """
    # 生成文章內容
    date, title, content = generate_insight()

    # 構造檔案路徑
    filename = f"content/posts/insight-{date[:10]}.md"

    # 確保目錄存在
    os.makedirs("content/posts", exist_ok=True)
    print(f"Ensured directory exists: content/posts")

    # 構造 Markdown 檔案內容
    markdown_content = f"""---
title: "{title}"
date: {date}
draft: false
showChart: true
---
{content}
"""

    # 寫入檔案
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Generated file: {filename}")


if __name__ == "__main__":
    save_insight()