import tkinter as tk
import requests
import time
import random
from bs4 import BeautifulSoup
from pypinyin import pinyin, Style

# 注音符號對應表 (標準 Google 注音排列)
phonetic_symbols = {
    "1": "ㄅ", "q": "ㄆ", "a": "ㄇ", "z": "ㄈ",
    "2": "ㄉ", "w": "ㄊ", "s": "ㄋ", "x": "ㄌ",
    "e": "ㄍ", "d": "ㄎ", "c": "ㄏ",
    "r": "ㄐ", "f": "ㄑ", "v": "ㄒ",
    "5": "ㄓ", "t": "ㄔ", "g": "ㄕ", "b": "ㄖ",
    "y": "ㄗ", "h": "ㄘ", "n": "ㄙ",
    "u": "ㄧ", "j": "ㄨ", "m": "ㄩ",
    "8": "ㄚ", "i": "ㄛ", "k": "ㄜ", ",": "ㄝ",
    "9": "ㄞ", "o": "ㄟ", "l": "ㄠ", ".": "ㄡ",
    "0": "ㄢ", "p": "ㄣ", ";": "ㄤ", "/": "ㄥ", "-": "ㄦ",
    "6": "ˊ", "3": "ˇ", "4": "ˋ", "7": "˙",
    " ": " "  # 空格對應到沒有聲調或作為輸入間隔
}

# 反向查找注音符號對應的按鍵
symbol_to_keys = {v: k for k, v in phonetic_symbols.items()}

# 取得隨機中文字
def get_random_char():
    try:
        urls = [
            "https://tw.news.yahoo.com/",
            "https://www.chinatimes.com/realtimenews/?chdtv",
            "https://www.ettoday.net/news/"
        ]
        random.shuffle(urls)  # 隨機選取網站
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                response.encoding = 'utf-8'
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()
                    chinese_chars = [char for char in text if '\u4e00' <= char <= '\u9fff']
                    if chinese_chars:
                        return random.choice(list(set(chinese_chars)))
            except requests.exceptions.RequestException:
                print(f"無法連接到 {url}")
                continue
        return "error: 無法獲取測試文字"
    except Exception as e:
        return f"error: 發生錯誤：{e}"

# 開始測試
def start_test():
    global test_char, target_keys, current_key_index
    test_char = get_random_char()
    if test_char.startswith("error"):
        sentence_label.config(text=test_char)
        entry.config(state="disabled")
        reset_keyboard_color()
        finger_label.config(text="")
        return

    sentence_label.config(text=test_char)
    entry.config(state="normal")
    entry.delete(0, tk.END)
    current_key_index = 0
    target_keys = []

    # 取得注音並轉換為按鍵序列
    try:
        zhuyin_list = pinyin(test_char, style=Style.BOPOMOFO)
        for p_list in zhuyin_list:
            for symbol in p_list:
                for char in symbol:
                    if char in symbol_to_keys:
                        target_keys.append(symbol_to_keys[char])
                    elif char == ' ':
                        target_keys.append('space')
    except Exception as e:
        sentence_label.config(text=f"Error getting pinyin: {e}")
        return

    highlight_next_key()

# 變色鍵盤顯示
def on_key_press(event):
    global current_key_index

    if not target_keys:
        return "break"

    key = event.char.lower()
    if current_key_index < len(target_keys):
        expected_key = target_keys[current_key_index]

        if key == expected_key:
            entry.insert(tk.END, key)
            current_key_index += 1
            if current_key_index < len(target_keys):
                highlight_next_key()
            else:
                # 輸入完成，延遲後重置
                root.after(5, start_test)
        elif key in key_buttons:
            # 輸入錯誤時閃爍紅色
            key_buttons[key].config(bg="red")
            root.after(200, lambda k=key: key_buttons[k].config(bg="white"))

    return "break"

def highlight_next_key():
    reset_keyboard_color()
    if current_key_index < len(target_keys):
        next_key = target_keys[current_key_index].lower()
        if next_key in key_buttons:
            key_buttons[next_key].config(bg="lightblue")
            finger_label.config(text=finger_mapping.get(next_key, ""))
        elif next_key == "space":
            key_buttons["space"].config(bg="lightblue")
            finger_label.config(text=finger_mapping.get(" ", ""))

# 重置鍵盤顏色（保留正確按鍵藍色，其他白色）
def reset_keyboard_color():
    # 先重置所有按鍵為白色
    for btn in key_buttons.values():
        btn.config(bg="white")
    # 將正確按鍵設為藍色
    for key in target_keys:
        if key in key_buttons:
            key_buttons[key].config(bg="white")
        elif key == "space":
            key_buttons["space"].config(bg="white")

# 創建 GUI 視窗
root = tk.Tk()
root.title("注音打字練習")
root.geometry("800x700")

# 顯示測試句子
sentence_label = tk.Label(root, text="按 '開始' 來獲取測試文字", font=("Arial", 24), wraplength=700)
sentence_label.pack(pady=20)

# 輸入框
entry = tk.Entry(root, font=("Arial", 24), width=10, state="disabled")
entry.pack(pady=10)
entry.bind("<KeyPress>", on_key_press)

# 按鈕
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="開始", command=start_test, font=("Arial", 16))
start_btn.pack(side="left", padx=10)

# 鍵盤模擬
keyboard_frame = tk.Frame(root)
keyboard_frame.pack(pady=10)

keyboard_layout = [
    ("1234567890-", 0),
    ("qwertyuiop[]", 28),
    ("asdfghjkl;'", 26),
    ("zxcvbnm,./", 26),
]

key_buttons = {}

for row_index, (row, indent) in enumerate(keyboard_layout):
    row_frame = tk.Frame(keyboard_frame)
    row_frame.pack()

    tk.Label(row_frame, text=" " * indent).pack(side="left")

    for key_char in row:
        btn = tk.Button(row_frame, text=phonetic_symbols.get(key_char, key_char.upper()), 
                        font=("Arial", 16), width=3, height=2, bg="white")
        btn.pack(side="left", padx=2, pady=2)
        key_buttons[key_char] = btn

# 空白鍵
space_frame = tk.Frame(keyboard_frame)
space_frame.pack()
tk.Label(space_frame, text=" " * 16).pack(side="left")
space_btn = tk.Button(space_frame, text="Space", font=("Arial", 16), width=15, height=2, bg="white")
space_btn.pack()
key_buttons["space"] = space_btn

# 手指對應提示
finger_mapping = {
    "q": "左手小指", "a": "左手小指", "z": "左手小指",
    "w": "左手無名指", "s": "左手無名指", "x": "左手無名指",
    "e": "左手中指", "d": "左手中指", "c": "左手中指",
    "r": "左手食指內", "f": "左手食指內", "v": "左手食指內", 
    "t": "左手食指外", "g": "左手食指外", "b": "左手食指外",
    "y": "右手食指外", "h": "右手食指外", "n": "右手食指外", 
    "u": "右手食指內", "j": "右手食指內", "m": "右手食指內",
    "i": "右手中指", "k": "右手中指", ",": "右手中指",
    "o": "右手無名指", "l": "右手無名指", ".": "右手無名指",
    "p": "右手小指", ";": "右手小指", "/": "右手小指",
    " ": "拇指",
    "1": "左手小指", "2": "左手無名指", "3": "左手中指", 
    "4": "左手食指", "5": "左手食指", "6": "右手食指", 
    "7": "右手食指", "8": "右手中指", "9": "右手無名指", 
    "0": "右手小指", "-": "右手小指",
    "[": "右手小指", "]": "右手小指", "'": "右手小指"
}

finger_label = tk.Label(root, text="", font=("Arial", 16))
finger_label.pack(pady=10)

# 全局變數
test_char = ""
target_keys = []
current_key_index = 0

root.mainloop()
