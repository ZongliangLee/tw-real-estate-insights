import sqlite3
import json
from datetime import datetime, timedelta

def get_db_connection():
    db_path = 'house.db'  # 替換為你的 SQLite 數據庫路徑
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def generate_daily_data():
    conn = get_db_connection()
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    today_filename = today.replace('-', '_')  # 將日期格式從 2025-04-10 改為 2025_04_10

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

    # 修改保存路徑，加入日期
    output_path = f'data/daily_data_{today_filename}.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)

    conn.close()
    print(f"Generated {output_path} with {len(daily_data)} entries.")

if __name__ == "__main__":
    generate_daily_data()