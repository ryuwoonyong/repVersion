import tkinter as tk
from tkinter import filedialog

def get_file_path():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename()
    return file_path

if __name__ == '__main__':
    file_path = get_file_path()
    if file_path:
        print(f"Selected file: {file_path}")
    else:
        print("No file selected")