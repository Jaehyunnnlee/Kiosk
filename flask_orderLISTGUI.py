import tkinter as tk
from tkinter import messagebox, Scrollbar
import requests

class OrderListGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("주문 목록")

        self.order_buttons = {}

        self.refresh_button = tk.Button(self, text="주문 내역 갱신", command=self.refresh_order_list)

        self.order_frame = tk.Frame(self)
        self.order_frame.pack(pady=10)

        self.scrollbar = Scrollbar(self.order_frame)

        self.order_list_text = tk.Text(self.order_frame, font=("Helvetica", 14))

        self.refresh_order_list()  # 주문 내역 초기화 및 표시

    def remove_order(self, order_num):
        try:
            post_order_num = order_num
            response = requests.delete('http://localhost:5000/orders', json=post_order_num)

            if response.status_code == 200:
                messagebox.showinfo("주문 삭제", "주문이 성공적으로 삭제되었습니다.")
            else:
                messagebox.showerror("주문 삭제 오류", f"주문 삭제 중 오류가 발생했습니다. 에러 코드: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("주문 삭제 오류", f"주문 삭제 중 오류가 발생했습니다. 에러 메시지: {str(e)}")

    def refresh_order_list(self):
        try:
            response = requests.get('http://localhost:5000/orders')
            if response.status_code == 200:
                orders = response.json()

                # 기존 버튼 삭제
                for button in self.order_buttons.values():
                    button.destroy()
                self.order_buttons.clear()

                # 주문번호별로 버튼 및 주문 목록 생성
                for order in orders:
                    order_num = order['order_num']
                    menu_name = order['menu_name']
                    quantity = order['quantity']

                    if order_num in self.order_buttons:
                        # 이미 버튼이 생성된 주문번호의 경우, 해당 버튼에 주문 목록 추가
                        button = self.order_buttons[order_num]
                        order_text = f"메뉴명: {menu_name}\n수량: {quantity}\n\n"
                        button["text"] += order_text
                    else:
                        # 새로운 주문번호인 경우, 버튼 생성 및 주문 목록 추가
                        button = tk.Button(self.order_frame, text=f"주문번호: {order_num}\n")
                        order_text = f"메뉴명: {menu_name}\n수량: {quantity}\n\n"
                        button["text"] += order_text
                        button["command"] = lambda num=order_num: self.remove_order(num)
                        button.pack(pady=5)
                        self.order_buttons[order_num] = button

                # 스크롤바 연결
                self.scrollbar.config(command=self.order_list_text.yview)
                self.order_list_text.config(yscrollcommand=self.scrollbar.set)

            else:
                messagebox.showerror("주문 내역 오류", f"주문 내역을 가져오는 중 오류가 발생했습니다. 에러 코드: {response.status_code}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("주문 내역 오류", f"주문 내역을 가져오는 중 오류가 발생했습니다. 에러 메시지: {str(e)}")

        # 5초마다 주문 내역을 자동으로 갱신
        self.after(1000, self.refresh_order_list)


if __name__ == "__main__":
    order_list_gui = OrderListGUI()
    order_list_gui.geometry("1000x600")
    order_list_gui.mainloop()
