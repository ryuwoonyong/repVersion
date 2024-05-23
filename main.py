import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import subprocess
import paramiko

root = tk.Tk()
root.title("리포트 버전 테스트")
root.geometry("800x400")

# 실행 파이선 파일
urlAlivepy = "./util/urlAlive.py"
vmAlivepy = "./util/vmAlive.py"  # 여기서 경로 수정
Startpy = "./util/start.py"
Shutdownpy = "./util/shutdown.py"

# 타이틀 라벨
labelTitle = ttk.Label(root, text="Report Version Test", font=("Helvetica", 25, "bold italic"))
labelTitle.pack(pady=20)

# 라벨들을 각각 pack과 grid로 배치
labelAliveCheckTitle = ttk.Label(root, text="SERVER CONDITION", width=20, anchor="center", font=("Helvetica", 12), foreground="black", background="lightgray", borderwidth=2, relief="solid", padding=(10, 5))
labelAliveCheckTitle.pack(side=tk.LEFT, padx=5, pady=20)

labelAliveCheck = ttk.Label(root, text="", width=20, anchor="center", font=("Helvetica", 12), foreground="black", background="lightgray", borderwidth=2, relief="solid", padding=(10, 5))
labelAliveCheck.pack(side=tk.LEFT, padx=5, pady=20)

def upLoadJs():
    try:
        # 'other_script.py'를 실행
        result = subprocess.run(["python", "./test/shape.py"], capture_output=True, text=True, check=True, encoding='utf-8')
        # 레이블의 텍스트를 실행 결과로 변경
        messagebox.showinfo("정보", "다른 스크립트가 성공적으로 실행되었습니다!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("오류", f"스크립트 실행 중 오류 발생: {e}")

def tomcatStart():
    result = subprocess.run(["python", Startpy], capture_output=True, text=True, encoding='utf-8')
    return result.stdout.strip()

def tomcatShutdown():
    result = subprocess.run(["python", Shutdownpy], capture_output=True, text=True, encoding='utf-8')
    return result.stdout.strip()

button = tk.Button(root, text="업로드", width=10, anchor="center", font=("Helvetica", 12), foreground="black", background="lightgray", borderwidth=2, relief="solid", command=upLoadJs)
button.pack(side=tk.LEFT, padx=5, pady=20)

button = tk.Button(root, text="WAS START", command=tomcatStart)
button.pack(pady=10)

button = tk.Button(root, text="WAS SHUTDOWN", command=tomcatShutdown)
button.pack(pady=10)

def run_script_and_get_result(script_path):
    result = subprocess.run(["python", script_path], capture_output=True, text=True, encoding='utf-8')
    return result.stdout.strip()

def wasAlive():
    # 다른 스크립트 실행 후 반환된 결과
    result = run_script_and_get_result(urlAlivepy)    
    # 라벨 업데이트
    labelAliveCheck.config(text=result)

def wmAlive():
    result = run_script_and_get_result(vmAlivepy)
    # 라벨 업데이트
    messagebox.showinfo("VM 상태", result + "\r\n서버 담당자에게 문의하세요 김진현")

# 서버 ALIVE 체크
wmAlive()
# WAS ALIVE 체크
wasAlive()

root.mainloop()