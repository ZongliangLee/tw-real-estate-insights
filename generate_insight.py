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
### 台中房市現況：多重利空因素夾擊

台中房市受到多重因素影響，呈現悲觀氛圍。

首先，全球經濟環境惡化，川普的對等關稅政策讓台灣出口導向的經濟承壓，中小企業面臨訂單縮減與成本增加的挑戰，預估2025年GDP下調，股市疲弱進一步拖累房市。

其次，政策面持續收緊，央行自2024年9月19日推出第七波選擇性信用管制措施後，資金流入房市受限，2025年3月央行更表示無鬆綁機會，並加強金檢，導致小型建商資金斷鏈，甚至退場。

此外，高利率環境抑制買氣，非新青安第一屋利率2.6%，第二屋利率甚至超過3%，銀行採取「以價制量」策略，貸款條件嚴格，影響購屋意願。

最後，地緣政治風險加劇，兩岸關係緊張與中美對立讓台中房市的不確定性增加。

### 台中房市趨勢與預測

從今日價格波動來看，台中房市呈現「核心穩定、邊緣下跌」的趨勢。北屯區與西屯區等蛋黃區因地段優勢與生活機能，房價降幅較小，符合文章中提到的「好地段、品牌佳、價格合理仍有成交機會」。反觀大里區等蛋殼區，過去房價虛胖，缺乏題材支撐，跌價風險較高，符合「蛋殼區需特別留意跌價風險」的預測。

未來台中房市仍將受到多重利空因素影響。政策面持續收緊，央行無意鬆綁信用管制，高利率環境可能延續，地緣政治風險也難以緩解。房市將進一步回歸自住剛需市場，消費者購屋決策時間拉長，挑選物件更謹慎。對於購屋者，建議優先考慮核心地段的優質物件，避免投資非核心地段的高風險房產。

### 結論

台中房市在2025年下半年面臨多重挑戰，今日信義房屋物件價格波動顯示核心地段房價相對穩定，但非核心地段跌價風險加劇。購屋者應密切關注政策、利率與經濟動向，謹慎評估購屋時機與地段選擇，以降低投資風險。
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