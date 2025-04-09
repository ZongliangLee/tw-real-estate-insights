import datetime
import os

def generate_insight():
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    title = "房市動態：測試 Python 執行"
    content = "這是一篇測試文章，確認 Python 在 GitHub Actions 中執行成功。"
    print("Starting insight generation...")
    return date, title, content

def save_insight():
    date, title, content = generate_insight()
    filename = f"content/posts/insight-{date[:10]}.md"
    # 確保目錄存在
    os.makedirs("content/posts", exist_ok=True)
    print(f"Ensured directory exists: content/posts")
    # 使用多行字串確保格式完整
    markdown_content = f"""---
title: "{title}"
date: {date}
draft: false
---
{content}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Generated file: {filename}")

if __name__ == "__main__":
    save_insight()