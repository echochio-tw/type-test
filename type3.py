import tkinter as tk
import requests
import time

# 取得隨機句子
def get_random_sentence():
    url = "https://baconipsum.com/api/?type=all-meat&sentences=1&format=text"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text.strip().lower()
    return "error: 無法獲取測試文字"

# 開始測試
def start_test():
    global test_sentence, start_time, current_index, prev_key
    test_sentence = get_random_sentence()
    sentence_label.config(text=test_sentence)
    entry.config(state="normal")
    entry.delete(0, tk.END)
    start_time = time.time()
    current_index = 0
    prev_key = None  # 記錄上一個字母
    reset_keyboard_color()
    highlight_next_key()

# 計算 WPM
def end_test():
    global start_time
    end_time = time.time()
    words = len(test_sentence.split())
    time_taken = end_time - start_time
    wpm = (words / time_taken) * 60

    result_label.config(text=f"⏱ WPM: {round(wpm, 2)}")
    entry.config(state="disabled")
    reset_keyboard_color()  # 測試結束時重置鍵盤顏色
    finger_label.config(text="") # 清除手指提示

# 變色鍵盤顯示
def on_key_press(event):
    global current_index, prev_key
    key = event.char.lower()

    if current_index < len(test_sentence) and key == test_sentence[current_index]:
        entry.insert(tk.END, key)  # 只允許正確的鍵出現在輸入框

        # 如果按下的是橘色的鍵，變回白色
        if key in key_buttons and key_buttons[key].cget("bg") == "orange":
            key_buttons[key].config(bg="white")

        # 如果按下的是藍色的鍵，變回白色
        elif key in key_buttons and key_buttons[key].cget("bg") == "lightblue":
            key_buttons[key].config(bg="white")

        # 空白鍵變回白色
        elif key == " " and "space" in key_buttons and key_buttons["space"].cget("bg") == "lightblue":
            key_buttons["space"].config(bg="white")

        prev_key = key  # 更新前一個按鍵
        current_index += 1
        highlight_next_key()  # 更新下一個應輸入的字母變色

    return "break"  # 阻止 Tkinter 預設輸入

def highlight_next_key():
    """讓下一個應輸入的字母變藍色，如果與前一個相同則變橘色"""
    reset_keyboard_color()  # 清除所有顏色
    if current_index < len(test_sentence):
        next_key = test_sentence[current_index].lower()
        if next_key in key_buttons:
            if prev_key == next_key:  # 如果與前一個字母相同，變橘色
                key_buttons[next_key].config(bg="orange")
            else:  # 否則變藍色
                key_buttons[next_key].config(bg="lightblue")
            finger_label.config(text=finger_mapping.get(next_key, "")) # 更新手指提示
        elif next_key == " " and "space" in key_buttons:
            key_buttons["space"].config(bg="lightblue")
            finger_label.config(text=finger_mapping.get(" ", "")) # 更新手指提示

# 重置鍵盤顏色
def reset_keyboard_color():
    """清除所有按鍵顏色，恢復白色"""
    for btn in key_buttons.values():
        btn.config(bg="white")

# 創建 GUI 視窗
root = tk.Tk()
root.title("打字測試")
root.geometry("800x600") # 增加視窗高度

# 顯示測試句子
sentence_label = tk.Label(root, text="按 '開始' 來獲取測試文字", font=("Arial", 14), wraplength=700)
sentence_label.pack(pady=20)

# 輸入框
entry = tk.Entry(root, font=("Arial", 14), width=70)
entry.pack(pady=10)
entry.bind("<KeyPress>", on_key_press)

# 按鈕
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="開始", command=start_test, font=("Arial", 12))
start_btn.pack(side="left", padx=10)

submit_btn = tk.Button(btn_frame, text="提交", command=end_test, font=("Arial", 12))
submit_btn.pack(side="left", padx=10)

# 顯示結果
result_label = tk.Label(root, text="", font=("Arial", 14))
result_label.pack(pady=10)

# 鍵盤模擬
keyboard_frame = tk.Frame(root)
keyboard_frame.pack(pady=10)

# 調整鍵盤佈局，使其符合標準 QWERTY
keyboard_layout = [
    ("1234567890-=", 0),  # 數字鍵
    ("qwertyuiop[]", 18),  # 第一排
    ("asdfghjkl;'", 18),  # 第二排
    ("zxcvbnm,./", 18),  # 第三排，讓 Z 對齊 A/S
]

key_buttons = {}

for row_index, (row, indent) in enumerate(keyboard_layout):
    row_frame = tk.Frame(keyboard_frame)
    row_frame.pack()

    # 使用 Label 來增加縮進
    tk.Label(row_frame, text=" " * indent).pack(side="left")

    for key in row:
        btn = tk.Button(row_frame, text=key.upper(), font=("Arial", 12), width=4, height=2, bg="white")
        btn.pack(side="left", padx=2, pady=2)
        key_buttons[key] = btn

# 加入空白鍵，向右移到 C/V 的下方
space_frame = tk.Frame(keyboard_frame)
space_frame.pack()

# 設置縮進來對齊 C/V
tk.Label(space_frame, text=" " * 16).pack(side="left")  # 這裡增加縮進

space_btn = tk.Button(space_frame, text="Space", font=("Arial", 12), width=25, height=2, bg="white")
space_btn.pack()
key_buttons["space"] = space_btn

# 手指對應字典
finger_mapping = {
    "q": "左手小指", "a": "左手小指", "z": "左手小指",
    "w": "左手無名指", "s": "左手無名指", "x": "左手無名指",
    "e": "左手中指", "d": "左手中指", "c": "左手中指",
    "r": "左手食指內", "f": "左手食指內", "v": "左手食指內", "t": "左手食指外", "g": "左手食指外", "b": "左手食指外",
    "y": "右手食指外", "h": "右手食指外", "n": "右手食指外", "u": "右手食指內", "j": "右手食指內", "m": "右手食指內",
    "i": "右手中指", "k": "右手中指", ",": "右手中指",
    "o": "右手無名指", "l": "右手無名指", ".": "右手無名指",
    "p": "右手小指", ";": "右手小指", "/": "右手小指",
    " ": "拇指"
}

# 手指提示標籤
finger_label = tk.Label(root, text="", font=("Arial", 14))
finger_label.pack(pady=10)

# 初始化變數
test_sentence = ""
start_time = 0
current_index = 0
prev_key = None  # 記錄上一個字母

# 啟動視窗
root.mainloop()