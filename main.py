import os
import sys
import paramiko
import subprocess
import logging

from util import ReportCommon

from PyQt5.QtWidgets import *
from PyQt5 import uic

# SSH 연결 설정
hostname = "10.0.2.21"
port = 22
username = "tomcat"
password = "tomcat"
reportPath = "/app/tomcat/ClipReport5"

# 실행 파이선 파일
urlAlivepy = "./util/urlAlive.py"
vmAlivepy = "./util/vmAlive.py"  # 여기서 경로 수정
Startpy = "./util/start.py"
Shutdownpy = "./util/shutdown.py"
fileSelect ="./util/fileSelect.py"


def fileSearch(self):
    result = run_script_and_get_result(fileSelect)
    print(result)
    self.textEdit.setText(result)

def run_script_and_get_result(script_path):
    result = subprocess.run(["python", script_path], capture_output=True, text=True, encoding='utf-8')
    return result.stdout.strip()

def wasAlive():
    # 다른 스크립트 실행 후 반환된 결과
    result = run_script_and_get_result(urlAlivepy)    
    
def wmAlive():
    result = run_script_and_get_result(vmAlivepy)

def tomcatStart():
        result = subprocess.run(["python", Startpy], capture_output=True, text=True, encoding='utf-8')
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
        
        '''''''''''''''''UI 초기세팅'''''''''''''''''
        
        self.setWindowTitle("톰캣/리포트 확인")
        self.setFixedWidth(680)
        # 리포트 버전 확인
        self.label_4.setText("현재버전 - "+ReportCommon.versionCheck(hostname, port, username, password, reportPath))
        
        # 라이브러리 콤보박스 세팅
        ReportCommon.libComSet(self, hostname, port, username, password)
        
        # 서버 status
        
        # 톰캣 status
        
        # 톰캣 로그
        

        '''''''''''''''''UI 초기세팅'''''''''''''''''
        
        
        
        #self.pushButton.clicked.connect(self.search1)
        
        # 톰캣 start
        self.server_start.clicked.connect(self.on_button_click)
        
        # 톰캣 shutdown
        self.server_shutdown.clicked.connect(self.on_button_click1)
        
        # 버전 변경
        self.verSet.clicked.connect(self.verSet1)
        
        
        

    #여기에 함수 설정
    def on_button_click(self):
        tomcatStart()

    def on_button_click1(self):
        tomcatShutdown()

    def search1(self):
        fileSearch(self)
        
    def verSet1(self):
        print(self.comboBox.currentText())
        ReportCommon.versionChange(hostname, port, username, password, self.comboBox.currentText())

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = WindowClass( )
    myWindow.show( )
    app.exec_( )

