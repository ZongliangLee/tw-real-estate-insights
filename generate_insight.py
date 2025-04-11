import datetime
import os

def generate_insight(themes):
    """
    生成房市分析文章的內容，包括日期、標題和正文。
    
    Args:
        themes (list): 包含新聞主題和摘要的列表，例如：
            [
                {"theme": "房地產", "summary": "房地產市場持續升溫，房價上漲。", "articles": ["房地產市場持續升溫，房價上漲10%。"]},
                {"theme": "財經市場", "summary": "股市下跌2000點，市場震盪。", "articles": ["股市今日下跌2000點，財經市場震盪。"]}
            ]
    
    Returns:
        dict: 包含 date, title, content 的字典
    """
    # 獲取當前日期並格式化
    current_date = datetime.datetime.now()
    date = current_date.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    title = f"{current_date.strftime('%Y-%m-%d')} 房市黑天鵝來襲？台中房市現況與今日價格波動分析"

    # 生成新聞摘要部分
    news_summary = "# 每日房地產與財經新聞摘要\n\n"
    for theme in themes:
        news_summary += f"### {theme['theme']}\n"
        news_summary += f"**摘要**：{theme['summary']}\n\n"
        for article in theme['articles']:
            news_summary += f"- {article}\n"
        news_summary += "\n"

    # 文章內容
    content = f"""
{news_summary}
"""

    print("Starting insight generation...")
    return {
        "date": date,
        "title": title,
        "content": content
    }

def save_insight(themes):
    """
    將生成的房市分析文章保存為 Markdown 檔案。
    
    Args:
        themes (list): 包含新聞主題和摘要的列表
    
    Returns:
        dict: 包含 filename 和 markdown_content 的字典
    """
    result = generate_insight(themes)
    date = result["date"]
    title = result["title"]
    content = result["content"]

    filename = f"content/posts/insight-{date[:10]}.md"
    os.makedirs("content/posts", exist_ok=True)
    print(f"Ensured directory exists: content/posts")
    markdown_content = f"""---
title: "{title}"
date: {date}
draft: false
showChart: true
---
{content}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Generated file: {filename}")

    return {
        "filename": filename,
        "markdown_content": markdown_content
    }