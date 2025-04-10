import sqlite3
import json
from datetime import datetime

def get_db_connection():
    db_path = 'house.db'  # 替換為你的 SQLite 數據庫路徑
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def generate_daily_data():
    conn = get_db_connection()
    today = datetime.now().strftime('%Y-%m-%d')

    # 提取當日更新的房價波動物件
    cursor = conn.execute("""
        SELECT p.houseNo, p.totalPrice, p.updatedDate, p.shareURL, 
               COALESCE(p.commName, p.name) AS displayName
        FROM properties p
        WHERE p.updatedDate LIKE ? 
        AND EXISTS (SELECT 1 FROM propertyHistory h WHERE h.houseNo = p.houseNo)
    """, (f"{today}%",))
    data = cursor.fetchall()

    # 轉換為 JSON 格式
    daily_data = []
    for row in data:
        daily_data.append({
            "houseNo": row["houseNo"],
            "totalPrice": row["totalPrice"],
            "updatedDate": row["updatedDate"],
            "shareURL": row["shareURL"],
            "displayName": row["displayName"]
        })

    # 保存到 Hugo 的 data/ 目錄
    with open('data/daily_data.json', 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)

    conn.close()
    print(f"Generated daily_data.json with {len(daily_data)} entries.")

if __name__ == "__main__":
    generate_daily_data()