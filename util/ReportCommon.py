# SSH 클라이언트 객체 생성
import paramiko, time, webbrowser
import tkinter as tk
# 파일 다이얼로그
from tkinter import filedialog




ssh = paramiko.SSHClient()

# 자동으로 서버의 호스트 키를 추가
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())



def versionCheck(hostname, port, username, password, reportPath):
    try:
        rep_en_ver=""
        ssh.connect(hostname, port, username, password)

        # 원격 명령 실행
        stdin, stdout, stderr = ssh.exec_command("cat /app/tomcat/files/lib_version.txt")
        #print(">>>>>>   " + reportPath);
        #stdin, stdout, stderr = ssh.exec_command("unzip -p "+reportPath+"/WEB-INF/lib/ClipReport5.0-Common.jar Version.txt")
        
        # 명령의 출력 결과 읽기
        for line in stdout.readlines():
            rep_en_ver+=line.strip()
    
    finally:
        # SSH 연결 종료
        ssh.close()
    #return rep_en_ver.split("=")[1]
    return rep_en_ver

def libComSet(self, hostname, port, username, password):
    try:
        sel_en_ver=[]
        ssh.connect(hostname, port, username, password)
        stdin, stdout, stderr = ssh.exec_command("ls -r /app/tomcat/files/lib/")
        for line in stdout.readlines():
            sel_en_ver.append(line.replace("\n",""))
        for line in stderr.readlines():
            print(line.strip())
        sel_en_verint = [int (i) for i in sel_en_ver]
        sel_en_verint.sort(reverse=True)
        for ver in sel_en_verint:
            self.comboBox.addItem(str(ver))
    finally:
        # SSH 연결 종료
        ssh.close()

def versionChange(hostname, port, username, password, ver):
    try:
        rep_en_ver=""
        ssh.connect(hostname, port, username, password)

        # 원격 명령 실행
        stdin, stdout, stderr = ssh.exec_command("/app/tomcat/files/libcp.sh "+ver)
    
    finally:
        # SSH 연결 종료
        ssh.close()

def reportView(self):
    print("여기로와야지")
    self.tomStat.setText('되냐')
    # 기본 웹 브라우저를 사용하여 URL 열기(임시)
    webbrowser.open('http://10.0.2.21:8080/ClipReport5/report.jsp')

    # 특정 웹 브라우저 (크롬) 사용하여 URL 열기
    #webbrowser.get('chrome').open('http://10.0.2.21/ClipReport5/report.jsp')

    # 특정 웹 브라우저 (엣지) 사용하여 URL 열기
    #webbrowser.get('edge').open('http://10.0.2.21/ClipReport5/report.jsp')

def get_file_path():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename()
    return file_path