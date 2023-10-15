# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, make_response, redirect, render_template
import mysql.connector
import json


# MariaDB 연결 설정
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="cafe",
    charset="utf8mb4",  # UTF-8 인코딩 설정
)
db.set_charset_collation('utf8mb4')
cursor = db.cursor()
cursor.execute("set names utf8")

app = Flask(__name__)
app.debug = True

app.config['JSON_AS_ASCII'] = False

app.secret_key = 'ABCD'  # 세션 암호화를 위한 비밀키 설정



# 회원 가입 페이지
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return 
    else:
        data = request.get_json()
        get_name = data.get('get_name')
        get_ID= data.get('get_ID')
        get_PW = data.get('get_PW')
        get_PW_confirm = data.get('get_PW_confirm')
        
        if not (get_ID and get_name and get_PW and get_PW_confirm):
            return jsonify({'message': '입력되지않은 정보가 있음 상태코드: '}), 501
        elif get_PW != get_PW_confirm:
            return jsonify({'message': '비밀번호가 서로 맞지 않음 상태코드: '}), 502
        else:
            cursor.execute("INSERT INTO user (ID, password,userName) VALUES (%s, %s, %s)", (get_ID, get_PW, get_name))
            db.commit()
        return jsonify({'message': '회원가입 성공! 상태코드: '}), 201


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user,favorite_ID
    if request.method == 'GET':
        userName=user[2]
        response = make_response(json.dumps(userName, ensure_ascii=False))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    else:
        data = request.get_json()
        ID = data.get('ID')
        password = data.get('password')
        
        if not (ID and password):
            return "아이디와 비밀번호를 입력해주세요."

        # 로그인 처리
        cursor.execute("SELECT * FROM user WHERE ID = %s AND password = %s", (ID, password))
        user = cursor.fetchone()

        if user:
            favorite_ID=user[0]
            userName = user[2]
            return jsonify({'message': 'logged_in'}), 201
        else:
            return jsonify({'message': 'Failed to create order'}), 501


@app.route('/menus', methods=['GET'])
def get_menu():
    cursor.execute("SELECT DISTINCT menu_name, price, category FROM menu")
    menu_list = cursor.fetchall()
    menus = []
    for menu in menu_list:
        menu_name, price, category = menu
        menus.append({
            'menu_name': menu_name,
            'price': price,
            'category': category
        })

    response = make_response(json.dumps(menus, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

@app.route('/',methods=['GET'])
def get_ping():
    return "pong"

@app.route('/orders', methods=['GET', 'POST'])
def get_order():
    if request.method == 'POST':
        orders = request.get_json()
        
        if not orders:
            return jsonify({'message': 'Invalid request'}), 400

        if save_order_to_db(orders):   
            return jsonify({'message': 'Order created'}), 201
        else:
            return jsonify({'message': 'Failed to create order'}), 500
    
    elif request.method == 'GET':
        cursor.execute("SELECT DISTINCT order_num, menu_name, quantity FROM orderList WHERE order_num IS NOT NULL ORDER BY order_num ASC")
        post_order_list = cursor.fetchall()
        post_orders = []
        for post_order in post_order_list:
            order_num, menu_name, quantity = post_order
            post_orders.append({
            'order_num': order_num,
            'menu_name': menu_name,
            'quantity': quantity
        })
    response = make_response(json.dumps(post_orders, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response 
            
    

def save_order_to_db(orders):
    try:
        cursor.execute("SELECT MAX(order_num) FROM orderList")
        result = cursor.fetchone()
        order_num = (result[0] + 1 if result[0] is not None else 1)
        for order in orders:
           
            menu_name = order['menu_name']
            quantity = order['quantity']
        
            cursor.execute("INSERT INTO orderList (menu_name, quantity,order_num) VALUES (%s, %s, %s)", (menu_name, quantity,order_num))
            
            cursor.execute("INSERT INTO famous (menu_name, quantity) VALUES (%s, %s) " \
                "ON DUPLICATE KEY UPDATE quantity = quantity + %s",(menu_name, quantity,quantity))
        db.commit()
        return True
    except mysql.connector.Error as error:
        print("DB Error:", error)
        return False
 
@app.route('/favorite',methods=['GET','POST'])
def favorite():
    if(request.method=='GET'):
        ID=favorite_ID
        if ID:
            cursor.execute("SELECT menu_name, MAX(`count`) AS max_count FROM favorite WHERE ID = %s GROUP BY menu_name ORDER BY max_count DESC LIMIT 1", 
                           (favorite_ID,))

            result = cursor.fetchone()
            if result:
                menu_name = result[0]
                response = make_response(json.dumps(menu_name, ensure_ascii=False))
                response.headers['Content-Type'] = 'application/json; charset=utf-8'
                print(response)
                return response
            else :
                return jsonify({'message': '메뉴 조회 실패 상태코드: '}), 501
    else:
        try:
        # 커서 생성
            ID=str(favorite_ID)
            menu_name=str(request.get_json())
            order_count=1
                # favorite 테이블에 새로운 행 삽입 또는 업데이트
            cursor.execute("INSERT INTO favorite (ID, menu_name, count) VALUES (%s, %s,%s) " \
                "ON DUPLICATE KEY UPDATE count = count + %s",(ID, menu_name ,order_count,order_count))
            db.commit()
            return jsonify({'message': '회원가입 성공! 상태코드: '}), 201
        except mysql.connector.Error as error:
            print("DB Error:", error)
            return jsonify({'message': 'Failed to create order'}), 500

@app.route('/orders',methods=['DELETE'])
def orderComplete():
    try:
        order_num=int(request.get_json())
        cursor.execute("DELETE FROM orderList WHERE order_num = %s", (order_num,))
        db.commit()
        return jsonify({'message': '주문이 성공적으로 완료되었습니다.'}), 200
    except:
        print(order_num)
        return jsonify({'message': '메뉴 삭제 실패 오류 상태 코드 : '}), 501
    
@app.route("/admin",methods=["GET", "POST"])
def admin_page():
    if request.method == "POST":
        admin_id = request.form.get("ID")
        password = request.form.get("password")
        cursor.execute("SELECT * FROM user WHERE ID = %s", ("admin",))
        info=cursor.fetchone()
        ID=info[0]
        PW=info[1]
        if admin_id == ID and password == PW:  
            return redirect('/admin/admin_famous')
        else:
            return redirect('/admin')
    return render_template('admin_login.html')
@app.route('/admin/admin_menu',methods=["GET","POST"])

def add_menu():
    add_menu_name = request.form.get("menu_name")
    add_menu_price = request.form.get("menu_price")
    add_menu_category= request.form.get("menu_category")
    if request.method == "POST":
        cursor.execute("INSERT INTO menu (menu_name, price, category) VALUES (%s, %s,%s)",
                        (add_menu_name,add_menu_price,add_menu_category))
        return redirect('/admin/admin_menu')
    db.commit()
    return render_template('add_menu.html')

@app.route("/admin/admin_famous",methods=["GET", "POST"])
def show_famoous():
    if request.method == "GET":
        cursor.execute("SELECT menu_name, quantity FROM famous ORDER BY quantity DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            menu_name = result[0]
            quantity = result[1]
            return render_template('famous.html', menu_name=menu_name, quantity=quantity)
        else:
            return "No favorite menu found."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)