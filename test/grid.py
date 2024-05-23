import tkinter as tk
from tkinter import ttk

# Tkinter 창 생성
root = tk.Tk()
root.title("Horizontal Label Placement")

# 라벨 생성 및 그리드 배치
label1 = ttk.Label(root, text="Label 1")
label1.grid(row=0, column=0, padx=5)

label2 = ttk.Label(root, text="Label 2")
label2.grid(row=0, column=1, padx=5)

label3 = ttk.Label(root, text="Label 3")
label3.grid(row=0, column=2, padx=5)

# 메인 루프 실행
root.mainloop()