import os
import sys
import paramiko
import subprocess

from PyQt5.QtWidgets import *
from PyQt5 import uic
# 더 추가할 필요가 있다면 추가하시면 됩니다. 예: (from PyQt5.QtGui import QIcon)

rep_en_ver=""
rep_js_ver=""
sel_en_ver=[]

# 실행 파이선 파일
urlAlivepy = "./util/urlAlive.py"
vmAlivepy = "./util/vmAlive.py"  # 여기서 경로 수정
Startpy = "./util/start.py"
Shutdownpy = "./util/shutdown.py"

# SSH 클라이언트 객체 생성
ssh = paramiko.SSHClient()

# 자동으로 서버의 호스트 키를 추가
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# SSH 연결 설정
hostname = "10.0.2.21"
port = 22
username = "tomcat"
password = "tomcat"
try:
    ssh.connect(hostname, port, username, password)

    # 원격 명령 실행
    stdin, stdout, stderr = ssh.exec_command("/app/tomcat/files/libcp.sh 260")
    
    # 명령의 출력 결과 읽기
    print("STDOUT111:")
    for line in stdout.readlines():
        print(line.strip())

    print("STDERR111:")
    for line in stderr.readlines():
        print(line.strip())

    # 원격 명령 실행
    stdin, stdout, stderr = ssh.exec_command("cat /app/tomcat/files/lib_version.txt")
    
    # 명령의 출력 결과 읽기
    print("STDOUT222:")
    for line in stdout.readlines():
        print(line.strip())
        rep_en_ver+=line.strip()

    print("STDERR222:")
    for line in stderr.readlines():
        print(line.strip())
finally:
    # SSH 연결 종료
    ssh.close()

def tomcatStart():
    result = subprocess.run(["python", Startpy], capture_output=True, text=True, encoding='utf-8')
    #wasAlive()
    return result.stdout.strip()

def tomcatShutdown():
    result = subprocess.run(["python", Shutdownpy], capture_output=True, text=True, encoding='utf-8')
    #wasAlive()
    return result.stdout.strip()


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))    
    return os.path.join(base_path, relative_path)

form = resource_path('./templates/app.ui')
form_class = uic.loadUiType(form)[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super( ).__init__( )
        self.setupUi(self)
        self.setWindowTitle("톰캣/리포트 확인")
        self.label_4.setText("현재버전 - 5.0." + rep_en_ver)
        # 여기에 시그널, 설정 
        
        ssh.connect(hostname, port, username, password)
        # 원격 명령 실행
        stdin, stdout, stderr = ssh.exec_command("ls -r /app/tomcat/files/lib/")
        # 명령의 출력 결과 읽기
        for line in stdout.readlines():
            sel_en_ver.append(line.replace("\n",""))
        for line in stderr.readlines():
            print(line.strip())
        sel_en_verint = [int (i) for i in sel_en_ver]
        sel_en_verint.sort(reverse=True)
        for ver in sel_en_verint:
            self.comboBox.addItem(str(ver))

        self.server_start.clicked.connect(tomcatStart)
        
        #def on_button_click(self):
        # 버튼 클릭 시 실행될 코드
        
        #self.start
    #여기에 함수 설정


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = WindowClass( )
    myWindow.show( )
    app.exec_( )