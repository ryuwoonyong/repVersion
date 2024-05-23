import tkinter as tk
from tkinter import ttk

# Tkinter 창 생성
root = tk.Tk()
root.title("Horizontal Label Placement")

# 라벨 생성
label1 = ttk.Label(root, text="Label 1")
label1.pack(side=tk.LEFT, padx=5)

label2 = ttk.Label(root, text="Label 2")
label2.pack(side=tk.LEFT, padx=5)

label3 = ttk.Label(root, text="Label 3")
label3.pack(side=tk.LEFT, padx=5)

# 메인 루프 실행
root.mainloop()