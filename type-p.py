import tkinter as tk
from tkinter import ttk
import requests
import random
from bs4 import BeautifulSoup
from pypinyin import pinyin, Style

# 标准键盘布局（修正偏移方向）
keyboard_layout = [
    ("1234567890-", "center"),    # 数字行居中
    ("qwertyuiop", "center"),     # 第一行字母居中
    ("asdfghjkl", -15),           # 第二行字母（向右偏移15像素）
    ("zxcvbnm", 30),             # 第三行字母（向右偏移30像素）
]

# 手指对应提示（标准指法）
finger_mapping = {
    "q": "左手小指", "a": "左手小指", "z": "左手小指",
    "w": "左手无名指", "s": "左手无名指", "x": "左手无名指",
    "e": "左手中指", "d": "左手中指", "c": "左手中指",
    "r": "左手食指", "f": "左手食指", "v": "左手食指",
    "t": "左手食指", "g": "左手食指", "b": "左手食指",
    "y": "右手食指", "h": "右手食指", "n": "右手食指",
    "u": "右手食指", "j": "右手食指", "m": "右手食指",
    "i": "右手中指", "k": "右手中指",
    "o": "右手无名指", "l": "右手无名指",
    "p": "右手小指", ";": "右手小指",
    " ": "拇指"
}

# 获取随机简体中文字
def get_random_char():
    try:
        urls = [
            "http://news.sina.com.cn/",
            "https://www.163.com/",
            "https://news.qq.com/"
        ]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        
        random.shuffle(urls)
        for url in urls:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.encoding = 'utf-8'
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    text = soup.get_text()
                    chinese_chars = [char for char in text if '\u4e00' <= char <= '\u9fff']
                    if chinese_chars:
                        return random.choice(list(set(chinese_chars)))
            except Exception as e:
                print(f"连接失败 {url}: {str(e)}")
                continue
        return "error: 无法获取测试文字"
    except Exception as e:
        return f"error: 发生错误：{e}"

# 全局变量
test_char = ""
target_keys = []
current_key_index = 0

# 开始测试
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

    # 获取拼音并转换按键序列
    try:
        pinyin_list = pinyin(test_char, style=Style.NORMAL)
        py = pinyin_list[0][0]
        py = py.replace('ü', 'v')  # 处理ü转v
        target_keys = list(py)
    except Exception as e:
        sentence_label.config(text=f"获取拼音失败: {e}")
        return

    highlight_next_key()

# 按键处理
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
                root.after(500, start_test)
        elif key in key_buttons:
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
        elif next_key == " ":
            key_buttons[" "].config(bg="lightblue")
            finger_label.config(text=finger_mapping.get(" ", ""))

def reset_keyboard_color():
    for btn in key_buttons.values():
        btn.config(bg="white")

# 创建主窗口
root = tk.Tk()
root.title("拼音打字练习")
root.geometry("800x700")

# 汉字显示区域
sentence_label = tk.Label(root, text="按 '开始' 进行测试", 
                         font=("Microsoft YaHei", 24), wraplength=700)
sentence_label.pack(pady=20)

# 输入框
entry = tk.Entry(root, font=("Microsoft YaHei", 24), width=15, state="disabled")
entry.pack(pady=10)
entry.bind("<KeyPress>", on_key_press)

# 控制按钮
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="开始", command=start_test, 
                     font=("Microsoft YaHei", 16), width=10)
start_btn.pack(side="left", padx=10)

# 键盘布局
keyboard_frame = tk.Frame(root)
keyboard_frame.pack(pady=20)

key_buttons = {}
for row, offset in keyboard_layout:
    row_frame = tk.Frame(keyboard_frame)
    row_frame.pack()
    
    if isinstance(offset, int):
        # 对于需要偏移的行
        if offset < 0:  # 向右偏移
            # 先添加一个占位框架
            left_pad = tk.Frame(row_frame, width=abs(offset))
            left_pad.pack(side="left")
        
        for key_char in row:
            btn = tk.Button(row_frame, text=key_char.upper(), 
                          font=("Arial", 16), width=3, height=2, bg="white")
            btn.pack(side="left", padx=2, pady=2)
            key_buttons[key_char] = btn
        
        if offset > 0:  # 向左偏移
            right_pad = tk.Frame(row_frame, width=abs(offset))
            right_pad.pack(side="right")
    else:
        # 居中的行
        for key_char in row:
            btn = tk.Button(row_frame, text=key_char.upper(), 
                          font=("Arial", 16), width=3, height=2, bg="white")
            btn.pack(side="left", padx=2, pady=2)
            key_buttons[key_char] = btn

# 空格键（居中显示）
space_frame = tk.Frame(keyboard_frame)
space_frame.pack(pady=5)
space_btn = tk.Button(space_frame, text="空格", font=("Microsoft YaHei", 16), 
                     width=30, height=2, bg="white")
space_btn.pack()
key_buttons[" "] = space_btn

# 手指提示
finger_label = tk.Label(root, text="", font=("Microsoft YaHei", 16))
finger_label.pack(pady=10)

# 启动主循环
root.mainloop()