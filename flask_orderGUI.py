import tkinter as tk
import requests


menu_data = None
categorized_menu_data = None
quantity_labels = {}
place_order_menu_data = []  # 주문을 보낸 후에는 주문할 메뉴 데이터 초기화
favorite_order_menu_data = []
global is_not_login
is_not_login=True

def get_menu_data():
    global menu_data, categorized_menu_data
    try:
        response = requests.get('http://192.168.0.91:5000/menus')
        if response.status_code == 200:
            menu_data = response.json()
            categorized_menu_data = {}
            for menu in menu_data:
                category = menu['category']
                if category in categorized_menu_data:
                    categorized_menu_data[category].append(menu)
                else:
                    categorized_menu_data[category] = [menu]
            for category in categorized_menu_data:
                for menu in categorized_menu_data[category]:
                    menu['quantity'] = 0
            menu_text = ""
            for category in categorized_menu_data:
                menu_text += f"{category}\n"
                for menu in categorized_menu_data[category]:
                    menu_text += f"- {menu['menu_name']}: {menu['price']}원\n"
                menu_text += "\n"
            get_menu_button.pack_forget()
            
            menu_label.config(text=menu_text)
            create_quantity_controls()
            order_list_label.pack(pady=20)
            loginStart_button.pack(side=tk.RIGHT)
            signup_Start_button.pack(side=tk.LEFT)
            order_button.pack(pady=20)  # 주문하기 버튼을 하단에 배치

        else:
            menu_label.config(text=f"Error: {response.status_code}")
    except requests.exceptions.RequestException as e:
        menu_label.config(text=f"Error: {str(e)}")


        
def signupGUI():
    login_frame.pack_forget()
    signup_frame.pack()
    signup_Start_button.pack_forget()
    loginStart_button.pack_forget()
    get_name_label.pack(side=tk.LEFT)
    get_name_entry.pack(side=tk.LEFT)
    get_ID_label.pack(side=tk.LEFT)
    get_ID_entry.pack(side=tk.LEFT)
    get_PW_label.pack(side=tk.LEFT)
    get_PW_entry.pack(side=tk.LEFT)
    get_PW_confirm_label.pack(side=tk.LEFT)
    get_PW_confirm_entry.pack(side=tk.LEFT)
    signup_button.pack(side=tk.RIGHT)

def signup():
    get_name= get_name_entry.get()
    get_ID=get_ID_entry.get()
    get_PW = get_PW_entry.get()
    get_PW_confirm=get_PW_confirm_entry.get()
        
    payload = {
        'get_name': get_name,
        'get_ID': get_ID,
        'get_PW':get_PW,
        'get_PW_confirm':get_PW_confirm
    }

    response = requests.post('http://localhost:5000/signup', json=payload)
    if response.status_code == 201:
        signup_frame.pack_forget()
        result_label.config(text="회원가입 성공")
        loginStart_button.pack(side=tk.TOP)

    elif response.status_code ==500:
        result_label.config(text="중복된 아이디입니다.")
    else:
        result_label.config(text="회원정보를 다시 입력해주세요")




def loginGUI():
    signup_frame.pack_forget()
    signup_Start_button.pack_forget()
    login_frame.pack()
    loginStart_button.pack_forget()
    ID_label.pack(side=tk.LEFT)
    ID_entry.pack(side=tk.LEFT)
    password_label.pack(side=tk.LEFT)
    password_entry.pack(side=tk.LEFT)
    login_button.pack(side=tk.RIGHT)
    



def login():
    global login_id,password,user_name
    login_id = ID_entry.get()
    password = password_entry.get()
    
    if not login_id or not password:
        result_label.config(text="아이디와 비밀번호를 모두 입력해주세요")

    payload = {
        'ID': login_id,
        'password': password
    }

    response = requests.post('http://localhost:5000/login', json=payload)
    if response.status_code == 201:
        response = requests.get('http://localhost:5000/login')
        if response.status_code==200:
            user_name = response.json()
            global is_login,is_not_login
            is_login=True
            is_not_login=False
            if is_login==True :
                login_frame.pack_forget()
                loginStart_button.pack_forget()
                logout_button.pack()
                result_label.config(text="환영합니다 "+user_name+"님")
                get_favorite()

                
        else:
            return
        
    else:
        result_label.config(text="아이디와 비밀번호를 다시 입력해주세요")

def logout():
    global is_login,login_id,password,is_not_login
    is_login=False
    is_not_login=True
    if is_login==False:
        loginStart_button.pack(side=tk.RIGHT)
        signup_Start_button.pack(side=tk.LEFT)
        logout_button.pack_forget()  # 로그아웃 버튼 숨김
        get_favorite_label.pack_forget()
        result_label.config(text="로그아웃 되었습니다.")
        
        login_id = ""
        password = ""
        ID_entry.delete(0, tk.END)  # 아이디 입력칸 초기화
        password_entry.delete(0, tk.END)


def update_quantity(category, index, change):
    global categorized_menu_data, quantity_labels
    menu = categorized_menu_data[category][index]
    menu['quantity'] += change
    quantity_labels[category][index].config(text=f"수량: {menu['quantity']}")

def create_quantity_controls():
    global categorized_menu_data, quantity_labels
    for category in categorized_menu_data:
        category_label = tk.Label(window, text=category, font=("Helvetica", 16, "bold"))
        category_label.pack(pady=(20, 5))
        quantity_labels[category] = []
        for i, menu in enumerate(categorized_menu_data[category]):
            quantity_frame = tk.Frame(window)
            quantity_frame.pack()
            menu_label = tk.Label(quantity_frame, text=f"{menu['menu_name']}: {menu['price']}원", font=("Helvetica", 14))
            menu_label.pack(side=tk.LEFT)
            minus_button = tk.Button(quantity_frame, text="-", command=lambda c=category, idx=i: update_quantity(c, idx, -1), width=2, font=("Helvetica", 14))
            minus_button.pack(side=tk.LEFT)
            quantity_label = tk.Label(quantity_frame, text=f"수량: {menu['quantity']}", font=("Helvetica", 14))
            quantity_label.pack(side=tk.LEFT)
            quantity_labels[category].append(quantity_label)
            plus_button = tk.Button(quantity_frame, text="+", command=lambda c=category, idx=i: update_quantity(c, idx, 1), width=2, font=("Helvetica", 14))
            plus_button.pack(side=tk.LEFT)
            add_to_cart_button = tk.Button(quantity_frame, text="담기", command=lambda c=category, idx=i: add_to_cart(c, idx), font=("Helvetica", 14))
            add_to_cart_button.pack(side=tk.LEFT)

def add_to_cart(category, index):
    global categorized_menu_data
    menu = categorized_menu_data[category][index]
    order_list_label.pack()
    if menu['quantity'] > 0:
        # 주문 내역에 추가
        order_text = order_list_label.cget("text")
        if f"- {menu['menu_name']}" in order_text:
            # 이미 주문 내역에 있는 메뉴인 경우, 기존 수량에 더함
            lines = order_text.split("\n")
            for i, line in enumerate(lines):
                if line.startswith(f"- {menu['menu_name']}"):
                    quantity = int(line.split(":")[1].split("개")[0].strip())
                    lines[i] = f"- {menu['menu_name']}: {quantity + menu['quantity']}개"
                    break
            order_text = "\n".join(lines)
        else:
            # 주문 내역에 새로운 메뉴 추가
            order_text += f"- {menu['menu_name']}: {menu['quantity']}개\n"
        order_list_label.config(text=order_text)
        menu_copy = menu.copy()
        categorized_menu_data[category][index]['quantity'] = 0  # 수량 초기화
        place_order_menu_data.append(menu_copy)
        favorite_order_menu_data.append(menu_copy)
        quantity_labels[category][index].config(text=f"수량: {categorized_menu_data[category][index]['quantity']}")

def place_order():
        global place_order_menu_data
        if not place_order_menu_data:
            return  # 주문할 메뉴 데이터가 없는 경우 처리

        order_text = "주문 내역:\n"
        for menu in place_order_menu_data:
            order_text += f"- {menu['menu_name']}: {menu['quantity']}개\n"
        order_label.config(text=order_text)

        # Send the order request to the server
        response = requests.post('http://localhost:5000/orders', json=place_order_menu_data)
        if response.status_code == 201:
            order_list_label.config(text="")
            order_label.pack()
            if is_not_login:
                place_order_menu_data.clear()
                order_label.pack()
                
            else:
                place_order_menu_data.clear()
                order_label.pack()
                bring_favorite()
                logout()
            
        else:
            print(f"주문을 처리하는 도중에 오류가 발생했습니다. 상태 코드: {response.status_code}")

def bring_favorite():
    global favorite_order_menu_data
    if not favorite_order_menu_data:
            return  # 주문할 메뉴 데이터가 없는 경우 처리
    else:
        for favorite_menu in favorite_order_menu_data:
            favorite_menu_name = favorite_menu['menu_name']
            response = requests.post('http://localhost:5000/favorite', json=favorite_menu_name)
        if response.status_code == 201:
            print(f"메뉴 정보 전송 완료 상태 코드: {response.status_code}")
        else:
            print(f"주문을 처리하는 도중에 오류가 발생했습니다. 상태 코드: {response.status_code}")

def get_favorite():
    global get_favorite_menu
    response = requests.get('http://localhost:5000/favorite')
    if response.status_code ==200:
        get_favorite_menu= response.json()
        get_favorite_label.config(text=user_name+"님에게 추천하는 메뉴는 "+get_favorite_menu +"입니다.")
        get_favorite_label.pack()


window = tk.Tk()
window.geometry("1000x600")
window.title("Cafe Kiosk")



menu_label = tk.Label(window, text="")
get_menu_button = tk.Button(window, text="시작하기", command=get_menu_data, font=("Helvetica", 100))
get_menu_button.pack(fill="both", expand=True, padx=10, pady=300)


order_label = tk.Label(window, text="", font=("Helvetica", 14))

order_button = tk.Button(window, text="주문하기", command=place_order, font=("Helvetica", 14))

order_list_label = tk.Label(window, text="담은내역\n", font=("Helvetica", 14), relief=tk.RAISED, width=40, height=10)

signup_frame = tk.Frame(window)
signup_frame.pack()

get_name_label = tk.Label(signup_frame, text="이름:", font=("Arial", 12))
get_name_entry = tk.Entry(signup_frame, font=("Arial", 12))

get_ID_label = tk.Label(signup_frame, text="아이디:", font=("Arial", 12))
get_ID_entry = tk.Entry(signup_frame, font=("Arial", 12))

get_PW_label = tk.Label(signup_frame, text="비밀번호:", font=("Arial", 12))
get_PW_entry = tk.Entry(signup_frame, font=("Arial", 12))

get_PW_confirm_label = tk.Label(signup_frame, text="비밀번호:", font=("Arial", 12))
get_PW_confirm_entry = tk.Entry(signup_frame, font=("Arial", 12))

signup_Start_button = tk.Button(text="회원가입하기", command=signupGUI, font=("Arial", 12))

signup_button = tk.Button(signup_frame, text="회원가입", command=signup, font=("Arial", 12))

login_frame = tk.Frame(window)
login_frame.pack()


# ID 입력 필드
ID_label = tk.Label(login_frame, text="ID:", font=("Arial", 12))
ID_entry = tk.Entry(login_frame, font=("Arial", 12))


# 비밀번호 입력 필드
password_label = tk.Label(login_frame, text="비밀번호:", font=("Arial", 12))
password_entry = tk.Entry(login_frame, show="*", font=("Arial", 12))


# 로그인 버튼 & 로그아웃 버튼
loginStart_button = tk.Button(text="로그인하기", command=loginGUI, font=("Arial", 12))
login_button = tk.Button(login_frame, text="로그인", command=login, font=("Arial", 12))

logout_frame=tk.Frame(window)
logout_frame.pack()

logout_button=tk.Button(logout_frame, text="로그아웃", command=logout, font=("Arial", 12))

result_label=tk.Label(logout_frame,text="",font=("Arial", 16))
result_label.pack()

get_favorite_label=tk.Label(logout_frame,text="",font=("Arial", 14))
get_favorite_label.pack()


window.mainloop()
