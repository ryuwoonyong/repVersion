import os, sys, paramiko, subprocess, logging, time

from util import ReportCommon
from util import ServerCommon

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

# SSH 연결 설정
hostname = "10.0.2.21"
port = 22
username = "tomcat"
password = "tomcat"
reportPath = "/app/tomcat/ClipReport5"
log_file_path="/app/tomcat/tomcat/logs/catalina.out"

# 실행 파이선 파일
urlAlivepy = "./util/urlAlive.py"
vmAlivepy = "./util/vmAlive.py"  # 여기서 경로 수정
fileSelect ="./util/fileSelect.py"


def run_script_and_get_result(script_path):
    result = subprocess.run(["python", script_path], capture_output=True, text=True, encoding='utf-8')
    return result.stdout.strip()

def wasAlive():
    # 다른 스크립트 실행 후 반환된 결과
    result = run_script_and_get_result(urlAlivepy)    
    
def wmAlive():
    result = run_script_and_get_result(vmAlivepy)

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
        self.libVer.setText("현재버전 - 5.0."+ReportCommon.versionCheck(hostname, port, username, password, reportPath))
        
        # 라이브러리 콤보박스 세팅
        ReportCommon.libComSet(self, hostname, port, username, password)

        
        # 서버 status
        
        # 톰캣 status
        #self.tomOn()
        #self.tomDown()
        #분기필요
        
        
        
        # 톰캣 로그
        self.textEditLogger.setReadOnly(True)
        self.setup_log_reader(hostname, port, username, password, log_file_path)
        

        '''''''''''''''''UI 초기세팅'''''''''''''''''
        
        
        #jar 업로드 
        self.pushButton_5.clicked.connect(self.fileSearch)
        
        # 톰캣 start
        self.server_start.clicked.connect(self.on_button_click)
        
        # 톰캣 shutdown
        self.server_shutdown.clicked.connect(self.on_button_click1)
        
        # 버전 변경
        self.verSet.clicked.connect(self.verSet1)
        
        # 뷰어 실행
        self.ViewRun.clicked.connect(self.view)
        
        
        

    #여기에 함수 설정
    def fileSearch(self):
        result = run_script_and_get_result(fileSelect)
        print(result)
        self.textEdit.setText(result)

    def on_button_click(self):
        self.tomIng('starting...')
        ServerCommon.tomcatAct.tomcatAct(hostname, port, username, password,"start")
        self.log_reader_thread = ServerCommon.LogReaderThread()
        self.log_reader_thread.setup(hostname, port, username, password, log_file_path)
        self.log_reader_thread.tomStartup_signal.connect(self.tomOn)
        self.log_reader_thread.start()

    def on_button_click1(self):
        self.tomIng('stopping...')
        ServerCommon.tomcatAct.tomcatAct(hostname, port, username, password,"shutdown")
        self.log_reader_thread = ServerCommon.LogReaderThread()
        self.log_reader_thread.setup(hostname, port, username, password, log_file_path)
        self.log_reader_thread.tomShutdown_signal.connect(self.tomDown)
        self.log_reader_thread.start()
    
    def tomOn(self):
        self.server_start.setEnabled(False)
        self.server_shutdown.setEnabled(True)
        self.tomStat.setText('<p align="left"><span style=" font-size:12pt; color:black;">started </span><span style=" font-size:12pt; color:green;">●</span></p>')
    def tomDown(self):
        self.server_start.setEnabled(True)
        self.server_shutdown.setEnabled(False)
        self.verSet.setEnabled(False)
        self.tomStat.setText('<p align="left"><span style=" font-size:12pt; color:black;">stop </span><span style=" font-size:12pt; color:red;">●</span></p>')
    def tomIng(self, str):
        self.tomStat.setText('<p align="left"><span style=" font-size:12pt; color:black;">'+str+'</span></p>')
        #pers = ['-', '\\', '|',  '/']
        #for z in range(20):
        #    for i in pers :
        #        print(i, end='\r', flush=True)
        #        time.sleep(0.2)
        #        self.tomStat.setText('<p align="left"><span style=" font-size:12pt; color:black;">'+i+'</span></p>')
        
    def view(self):
        ReportCommon.reportView(self)




    def search1(self):
        fileSearch(self)
        
    def verSet1(self):
        self.setEnabled(False)
        ReportCommon.versionChange(hostname, port, username, password, self.comboBox.currentText())
        self.log_reader_thread = ServerCommon.LogReaderThread()
        self.log_reader_thread.setup(hostname, port, username, password, log_file_path)
        self.log_reader_thread.success_signal.connect(self.enable_ui)
        self.log_reader_thread.start()        
        
    def enable_ui(self):
        self.setEnabled(True)
        self.libVer.setText("현재버전 - 5.0."+ReportCommon.versionCheck(hostname, port, username, password, reportPath))
        self.log_reader_thread.stop()
        
    def append_log(self, log_line):
        self.textEditLogger.append(log_line)
        
    def setup_log_reader(self, hostname, port, username, password, log_file_path):
        self.log_reader_thread = ServerCommon.LogReaderThread()
        self.log_reader_thread.setup(hostname, port, username, password, log_file_path)
        self.log_reader_thread.new_log_signal.connect(self.append_log)
        self.log_reader_thread.start()

    def stop_log_reader(self):
        if self.log_reader_thread:
            self.log_reader_thread.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myWindow = WindowClass( )
    myWindow.show( )
    app.exec_( )

