from flask import Flask, jsonify, send_from_directory, request
from datetime import datetime
from flask_cors import CORS  # Import CORS
import time
import requests
import os
import sqlite3
import json
from generate_insight import generate_insight, save_insight
from generate_daily_and_history_data import generate_daily_and_history_data
from git import Repo


app = Flask(__name__, static_folder='vue-app/dist', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})
MINUS_DATE = "-24 hours"

url = "https://sinyiwebapi.sinyi.com.tw/searchObject.php"
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json;charset=UTF-8',
    'Origin': 'https://www.sinyi.com.tw',
    'Pragma': 'no-cache',
    'Referer': 'https://www.sinyi.com.tw/',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
    'code': '0',
    'sat': '730282',
    'sid': '20240313143042818',
    'Cookie': 'PHPSESSID=lc6v3una79urtm8h3csaf48om6; lang=tc'
    }
    
def get_db_connection():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'house.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def getTotalCount():
    payload = "{\"machineNo\":\"\",\"ipAddress\":\"218.161.65.164\",\"osType\":4,\"model\":\"web\",\"deviceVersion\":\"Mac OS X 10.15.7\",\"appVersion\":\"128.0.0.0\",\"deviceType\":3,\"apType\":3,\"browser\":1,\"memberId\":\"\",\"domain\":\"www.sinyi.com.tw\",\"utmSource\":\"\",\"utmMedium\":\"\",\"utmCampaign\":\"\",\"utmCode\":\"\",\"requestor\":1,\"utmContent\":\"\",\"utmTerm\":\"\",\"sinyiGroup\":1,\"filter\":{\"exludeSameTrade\":false,\"objectStatus\":0,\"retType\":2,\"retRange\":[\"400\",\"401\",\"402\",\"403\",\"404\",\"406\",\"407\",\"408\"],\"houselandtype\":[\"L\",\"D\"]},\"page\":1,\"pageCnt\":20,\"sort\":\"0\",\"isReturnTotal\":true}"
    response = requests.post(url, headers=headers, data=payload)
    return response.json()["content"]["totalCnt"]

def searchObject(page):
    payload = "{\"machineNo\":\"\",\"ipAddress\":\"218.161.65.164\",\"osType\":4,\"model\":\"web\",\"deviceVersion\":\"Mac OS X 10.15.7\",\"appVersion\":\"128.0.0.0\",\"deviceType\":3,\"apType\":3,\"browser\":1,\"memberId\":\"\",\"domain\":\"www.sinyi.com.tw\",\"utmSource\":\"\",\"utmMedium\":\"\",\"utmCampaign\":\"\",\"utmCode\":\"\",\"requestor\":1,\"utmContent\":\"\",\"utmTerm\":\"\",\"sinyiGroup\":1,\"filter\":{\"exludeSameTrade\":false,\"objectStatus\":0,\"retType\":2,\"retRange\":[\"400\",\"401\",\"402\",\"403\",\"404\",\"406\",\"407\",\"408\"],\"houselandtype\":[\"L\",\"D\"]},\"page\":" + str(page) + ",\"pageCnt\":20,\"sort\":\"0\",\"isReturnTotal\":true}"
    response = requests.post(url, headers=headers, data=payload)
    return response

def sync_data():
    totalCount= getTotalCount()
    loopCount = int(totalCount/10)
    if totalCount%10 != 0:
        loopCount+=1
    for i in range(loopCount):
        response= searchObject(i)
        if response.status_code == 200:
            data = response.json()
            properties = data["content"]["object"]
            if properties is None:
                break
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            for property in properties:
                house_no = property.get('houseNo')
                total_price = property.get('totalPrice')
                current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Check if the property already exists
                cursor.execute("SELECT totalPrice FROM properties WHERE houseNo = ?", (house_no,))
                existing_property = cursor.fetchone()
                if existing_property is None:
                    # Insert new property
                    print(f"Inserting new property {house_no}")
                    insert_property(cursor, property, current_time)
                else:
                    # If the totalPrice has changed, move old data to history and update the property
                    if total_price != existing_property['totalPrice']:
                        print(f"Updating property {house_no} due to price change from {existing_property['totalPrice']} to {total_price}")
                        move_to_history(cursor, house_no, current_time)
                        update_property(cursor, property, current_time)

            conn.commit()
            conn.close()
            print("Data synchronized successfully.")
        else:
            print(f"Failed to fetch data: {response.status_code} - {response.text}")
        time.sleep(1)



def insert_property(cursor, property, created_time):
    parking = None
    if property.get('parking') is not None:
        parking = ",".join(map(str, property.get('parking')))

    cursor.execute("""
        INSERT INTO properties (houseNo, name, discount, address, age, commId, commName, priceFirst, totalPrice, areaBuilding, areaLand, isHasBalcony, pingUsed, layout, floor, totalfloor, isParking, parking, status, uniPrice, totalLayout, zipCode, createdDate, updatedDate, shareURL)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
        property.get('houseNo'),
        property.get('name'),
        property.get('discount'),
        property.get('address'),
        property.get('age'),
        property.get('commId'),
        property.get('commName'),
        property.get('priceFirst'),
        property.get('totalPrice'),
        property.get('areaBuilding'),
        property.get('areaLand'),
        property.get('isHasBalcony'),
        property.get('pingUsed'),
        property.get('layout'),
        property.get('floor'),
        property.get('totalfloor'),
        property.get('isParking'),
        parking,
        property.get('status'),
        property.get('uniPrice'),
        property.get('totalLayout'),
        property.get('zipCode'),
        created_time,
        created_time,
        property.get('shareURL')
    ))

def update_property(cursor, property, updated_time):
    parking = None
    if property.get('parking') is not None:
        parking = ",".join(map(str, property.get('parking')))

    cursor.execute("""
        UPDATE properties
        SET name = ?, discount = ?, address = ?, age = ?, commId = ?, commName = ?, priceFirst = ?, totalPrice = ?, areaBuilding = ?, areaLand = ?, isHasBalcony = ?, pingUsed = ?, layout = ?, floor = ?, totalfloor = ?, isParking = ?, parking = ?, status = ?, uniPrice = ?, totalLayout = ?, zipCode = ?, updatedDate = ?, shareURL = ?
        WHERE houseNo = ?""", (
        property.get('name'),
        property.get('discount'),
        property.get('address'),
        property.get('age'),
        property.get('commId'),
        property.get('commName'),
        property.get('priceFirst'),
        property.get('totalPrice'),
        property.get('areaBuilding'),
        property.get('areaLand'),
        property.get('isHasBalcony'),
        property.get('pingUsed'),
        property.get('layout'),
        property.get('floor'),
        property.get('totalfloor'),
        property.get('isParking'),
        parking,
        property.get('status'),
        property.get('uniPrice'),
        property.get('totalLayout'),
        property.get('zipCode'),
        updated_time,
        property.get('shareURL'),
        property.get('houseNo')
    ))

def move_to_history(cursor, house_no, updated_time):
    cursor.execute("SELECT * FROM properties WHERE houseNo = ?", (house_no,))
    old_data = cursor.fetchone()

    if old_data:
        cursor.execute("""
            INSERT INTO propertyHistory (houseNo, name, discount, address, age, commId, commName, priceFirst, totalPrice, areaBuilding, areaLand, isHasBalcony, pingUsed, layout, floor, totalfloor, isParking, parking, status, uniPrice, totalLayout, zipCode, createdDate, updatedDate, shareURL)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
            old_data['houseNo'],
            old_data['name'],
            old_data['discount'],
            old_data['address'],
            old_data['age'],
            old_data['commId'],
            old_data['commName'],
            old_data['priceFirst'],
            old_data['totalPrice'],
            old_data['areaBuilding'],
            old_data['areaLand'],
            old_data['isHasBalcony'],
            old_data['pingUsed'],
            old_data['layout'],
            old_data['floor'],
            old_data['totalfloor'],
            old_data['isParking'],
            old_data['parking'],
            old_data['status'],
            old_data['uniPrice'],
            old_data['totalLayout'],
            old_data['zipCode'],
            old_data['createdDate'],
            updated_time,
            old_data['shareURL']
        ))

        # Optionally, you might want to delete the old property from the original table after moving
        # cursor.execute("DELETE FROM properties WHERE houseNo = ?", (house_no,))

@app.route('/sync', methods=['POST'])
def sync():
    sync_data()
    return jsonify({"message": "Synchronization complete."})

@app.route('/api/houses/<house_no>', methods=['GET'])
def get_houses(house_no):
    conn = get_db_connection()
    houses = conn.execute('SELECT * FROM properties WHERE houseNo = ?', (house_no,)).fetchall()
    conn.close()
    return jsonify([dict(house) for house in houses])

@app.route('/api/propertyHistory', methods=['GET'])
def get_property_history():
    conn = get_db_connection()
    houses = conn.execute('SELECT houseNo FROM propertyHistory').fetchall()
    conn.close()
    return jsonify([dict(house) for house in houses])

@app.route('/api/getTodayChangeNumber', methods=['GET'])
def get_today_change_number():
    conn = get_db_connection()
    data = conn.execute("SELECT COUNT(p.houseNo) FROM properties p WHERE p.updatedDate >= DATETIME('now', '{}') \
        AND EXISTS (SELECT 1 FROM propertyHistory h WHERE h.houseNo = p.houseNo)".format(MINUS_DATE)).fetchone()
    conn.close()
    return jsonify(data["COUNT(p.houseNo)"])

@app.route('/api/priceTrend/<house_no>', methods=['GET'])
def get_price_trend(house_no):
    conn = get_db_connection()

    # Default pagination values
    page = int(request.args.get('page', 1))  # Default to page 1
    rows = int(request.args.get('rows', 20))  # Default to 10 rows per page
    start_index = (page - 1) * rows  # Starting index for slicing
    end_index = start_index + rows  # Ending index for slicing

    if house_no == "All":
        # Fetch all unique house numbers from propertyHistory
        price_trends = {}
        all_propertyHistory = conn.execute('SELECT DISTINCT houseNo FROM propertyHistory').fetchall()

        for property in all_propertyHistory:
            house_no = property['houseNo']
            price_history_list = []

            # Get the current price
            data = conn.execute(
                "SELECT totalPrice, createdDate, updatedDate FROM properties WHERE houseNo = ? AND updatedDate >= DATETIME('now', ?)",
                (house_no, MINUS_DATE)
            ).fetchone()

            # Add current price to the trend data
            if data:
                current_price_data = {
                    "createdDate": data["createdDate"],
                    "updatedDate": data["updatedDate"],
                    "totalPrice": data["totalPrice"]
                }

                # Fetch all price history entries for this houseNo
                price_history = conn.execute(
                    "SELECT totalPrice, createdDate, updatedDate FROM propertyHistory WHERE houseNo = ?",
                    (house_no,)
                ).fetchall()
                price_history_list = [dict(row) for row in price_history]
                price_history_list.append(current_price_data)

            # Only add to the dictionary if the list is not empty
            if price_history_list:
                price_trends[house_no] = price_history_list

        # Filter out empty lists and apply pagination
        non_empty_trends = {key: value for key, value in price_trends.items() if value}
        paginated_keys = list(non_empty_trends.keys())[start_index:end_index]
        paginated_price_trends = {key: non_empty_trends[key] for key in paginated_keys}

        conn.close()
        return jsonify(paginated_price_trends)

    # Logic for a single house (no pagination needed for single house)
    price_trend = conn.execute(
        'SELECT totalPrice, updatedDate, createdDate FROM propertyHistory WHERE houseNo = ?',
        (house_no,)
    ).fetchall()
    price_trend_list = [dict(row) for row in price_trend]

    # Get current price
    data = conn.execute(
        'SELECT totalPrice, updatedDate, createdDate FROM properties WHERE houseNo = ?',
        (house_no,)
    ).fetchone()

    if data:
        current_price_data = {
            "createdDate": data["createdDate"],
            "updatedDate": data["updatedDate"],
            "totalPrice": data["totalPrice"]
        }
        price_trend_list.append(current_price_data)

    conn.close()
    return jsonify(price_trend_list)

    # Logic for a single house (no pagination needed for single house)
    price_trend = conn.execute(
        'SELECT totalPrice, updatedDate, createdDate FROM propertyHistory WHERE houseNo = ?',
        (house_no,)
    ).fetchall()
    price_trend_list = [dict(row) for row in price_trend]

    # Get current price
    data = conn.execute(
        'SELECT totalPrice, updatedDate, createdDate FROM properties WHERE houseNo = ?',
        (house_no,)
    ).fetchone()

    if data:
        current_price_data = {
            "createdDate": data["createdDate"],
            "updatedDate": data["updatedDate"],
            "totalPrice": data["totalPrice"]
        }
        price_trend_list.append(current_price_data)

    conn.close()
    return jsonify(price_trend_list)

@app.route('/api/shareURL/<house_no>', methods=['GET'])
def generate_share_url(house_no):
    # Fetch the static share URL from the database based on house_no
    conn = get_db_connection()
    share_url_data = conn.execute('SELECT shareURL FROM properties WHERE houseNo = ?', (house_no,)).fetchone()
    conn.close()
    
    if share_url_data:
        return jsonify({"shareURL": share_url_data["shareURL"]})
    else:
        return jsonify({"error": "House not found"}), 404

@app.route('/api/getPropertyName/<house_no>', methods=['GET'])
def get_property_name(house_no):
    conn = get_db_connection()

    if house_no == "All":
        # Query all houses
        all_properties = conn.execute('SELECT houseNo, commName, name FROM properties').fetchall()
        conn.close()

        result = {}
        for property in all_properties:
            house_no = property['houseNo']
            if property['commName']:
                result[house_no] = property['commName']
            else:
                result[house_no] = property['name']
        
        return json.dumps(result, ensure_ascii=False), 200

    # Existing logic for single house_no
    commName = conn.execute('SELECT commName FROM properties WHERE houseNo = ?', (house_no,)).fetchone()
    if commName and commName["commName"]:
        conn.close()
        return json.dumps({house_no: commName["commName"]}, ensure_ascii=False), 200
    
    name = conn.execute('SELECT name FROM properties WHERE houseNo = ?', (house_no,)).fetchone()
    conn.close()
    if name and name["name"]:
        return json.dumps({house_no: name["name"]}, ensure_ascii=False), 200
    
    return jsonify({"error": "House not found"}), 404

@app.route('/api/generate-insight', methods=['POST'])
def generate_insight_endpoint():
    """
    接受 themes 數據，調用 generate_insight.py，生成房市分析文章。
    
    Request Body:
        {
            "themes": [
                {"theme": "房地產", "summary": "房地產市場持續升溫，房價上漲。", "articles": ["房地產市場持續升溫，房價上漲10%。"]},
                {"theme": "財經市場", "summary": "股市下跌2000點，市場震盪。", "articles": ["股市今日下跌2000點，財經市場震盪。"]}
            ]
        }
    
    Returns:
        {
            "filename": "content/posts/insight-YYYY-MM-DD.md",
            "markdown_content": "..."
        }
    """
    try:
        # 獲取請求數據
        data = request.get_json()
        if not data or 'themes' not in data:
            return jsonify({"error": "Missing 'themes' in request body"}), 400

        themes = data['themes']
        
        # 調用 generate_insight.py
        result = save_insight(themes)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/generate-daily-data', methods=['POST'])
def generate_daily_data_endpoint():
    try:
        # 執行 generate_daily_and_history_data.py
        generate_daily_and_history_data()

        # 獲取當前日期
        today = datetime.now().strftime('%Y-%m-%d')
        today_filename = today.replace('-', '_')
        daily_file_path = f"data/daily_data_{today_filename}.json"
        history_file_path = "data/history_data.json"

        # 提交檔案到 GitHub 儲存庫
        repo_path = os.path.dirname(os.path.abspath(__file__))
        repo = Repo(repo_path)

        if repo.bare:
            return jsonify({"error": "Git repository not initialized."}), 500

        # 確保當前分支是 main
        if repo.active_branch.name != 'main':
            repo.git.checkout('main')
        # 添加 data/daily_data_YYYY_MM_DD.json、data/history_data.json 和 house.db
        repo.index.add([daily_file_path, history_file_path, "house.db"])

        # 提交更改
        commit_message = f"Add daily and history data, house.db for {today}"
        repo.index.commit(commit_message)

        # 拉取遠端更改，避免推送失敗
        repo.git.stash()
        repo.git.pull('origin', 'main')

        # 推送到遠端儲存庫的 main 分支
        origin = repo.remote(name='origin')
        origin.push(refspec='main:main')

        return jsonify({
            "message": "Daily and history data generated, committed, and workflow triggered successfully.",
            "daily_file_path": daily_file_path,
            "history_file_path": history_file_path
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def index():
    return send_from_directory('vue-app/dist', 'index.html')

if __name__ == '__main__':
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule} -> {rule.endpoint}")
    app.run(host='0.0.0.0',debug=True)