import sqlite3
import json
from datetime import datetime, timedelta

def get_db_connection():
    db_path = 'house.db'  # 替換為你的 SQLite 數據庫路徑
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def generate_daily_and_history_data():
    conn = get_db_connection()
    today = datetime.now().strftime('%Y-%m-%d')
    today_filename = today.replace('-', '_')  # 將日期格式從 2025-04-10 改為 2025_04_10

    # 1. 提取當日更新的房價波動物件
    cursor_daily = conn.execute("""
        SELECT p.houseNo, p.totalPrice, p.updatedDate, p.shareURL, 
               COALESCE(p.commName, p.name) AS displayName
        FROM properties p
        WHERE DATE(p.updatedDate) = ? 
        AND EXISTS (SELECT 1 FROM propertyHistory h WHERE h.houseNo = p.houseNo)
    """, (today,))
    daily_data_rows = cursor_daily.fetchall()

    # 轉換為 JSON 格式 (daily_data)
    daily_data = []
    for row in daily_data_rows:
        daily_data.append({
            "houseNo": row["houseNo"],
            "totalPrice": row["totalPrice"],
            "updatedDate": row["updatedDate"],
            "shareURL": row["shareURL"],
            "displayName": row["displayName"]
        })

    # 保存到 daily_data_YYYY_MM_DD.json
    daily_output_path = f'data/daily_data_{today_filename}.json'
    with open(daily_output_path, 'w', encoding='utf-8') as f:
        json.dump(daily_data, f, ensure_ascii=False, indent=2)
    print(f"Generated {daily_output_path} with {len(daily_data)} entries.")

    # 2. 提取歷史資訊
    cursor_history = conn.execute("""
        SELECT h.houseNo, h.totalPrice, h.updatedDate
        FROM propertyHistory h
        ORDER BY h.updatedDate DESC
    """)
    history_data_rows = cursor_history.fetchall()

    # 轉換為 JSON 格式 (history_data)
    history_data = []
    for row in history_data_rows:
        history_data.append({
            "houseNo": row["houseNo"],
            "totalPrice": row["totalPrice"],
            "updatedDate": row["updatedDate"]
        })

    # 保存到 history_data.json
    history_output_path = 'data/history_data.json'
    with open(history_output_path, 'w', encoding='utf-8') as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)
    print(f"Generated {history_output_path} with {len(history_data)} entries.")

    conn.close()

if __name__ == "__main__":
    generate_daily_and_history_data()