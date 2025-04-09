import datetime
import os

def generate_insight():
    date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")
    title = "房市動態：測試 Python 執行"
    content = """美國對全球增加關稅可能會間接影響台灣房地產市場，主要通過以下幾個方面：

出口下降：台灣許多行業依賴出口，尤其是電子和科技產業。美國提高关税可能導致出口商品成本上升，企業利潤減少，從而影響其擴張能力和 найм員工的能力。

經濟增長放缓：如果出口减少，整體經濟增速可能放緩。這會降低人民的購買力，影響房地產需求。

供應鏈調整：企業可能重新調整供應鏈或尋找新的生產基地以避免高額关税，導致台灣某些產業轉移，減少對工業用地和廠房的需求。

利率政策：經濟放緩可能导致中央銀行降低利率以刺激經濟。低利率通常會增加購房需求，推高房价。

投資者情緒：國際貿易緊張可能影響投資者的信心，導致股市和房地產市場交易量下降。

多元化經濟：台灣的內需和服務業發展也可能部分抵消出口下滑的影響，支撐房地產市場。

"""
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