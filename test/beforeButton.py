import tkinter as tk
from tkinter import messagebox
import subprocess

# 다른 파이썬 스크립트를 실행하는 함수
def run_other_script():
    try:
        # 'other_script.py'를 실행
        result = subprocess.run(["python", "other_script.py"], capture_output=True, text=True, check=True)
        # 레이블의 텍스트를 실행 결과로 변경
        label_result.config(text=result.stdout)
        messagebox.showinfo("정보", "다른 스크립트가 성공적으로 실행되었습니다!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("오류", "스크립트 실행 중 오류 발생: {e}")

# 기본 창 설정
root = tk.Tk()
root.title("Tkinter 예제")
root.geometry("300x200")

# 레이블 (고정된 텍스트)
label_static = tk.Label(root, text="This is a static label:", font=("Helvetica", 14))
label_static.pack(pady=5)

# 레이블 (동적으로 변경될 텍스트)
label_result = tk.Label(root, text="Hello, Tkinter!", font=("Helvetica", 16))
label_result.pack(pady=10)

# 버튼
button = tk.Button(root, text="다른 스크립트 실행", command=run_other_script)
button.pack(pady=10)

# 메인 루프 실행
root.mainloop()