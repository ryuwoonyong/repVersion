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

#경로설정
reportPath = "/app/tomcat/ClipReport5"
log_file_path="/app/tomcat/tomcat/logs/catalina.out"
verFilePath="/app/tomcat/files"


#하기 함수로 vm및 was 커넥션 체크
#AliveCheck.check_vm_connection(hostname, port, username, password)
#AliveCheck.check_tom_connection(URL)


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
        
        self.setWindowTitle("Report Version TEST")
        self.setFixedWidth(691)
        
        # VM 서버 확인
        
        # 톰캣 확인
        if(ServerCommon.AliveCheck.check_tom_connection("http://10.0.2.21:8080/ClipReport5/tomCheck.jsp")):
            self.tomOn()
        else:
            self.tomDown()
        
        # 리포트 버전 확인
        self.libVer.setText("현재 엔진 버전 -  5.0."+ReportCommon.versionCheck(hostname, port, username, password, reportPath))
        
        # lib 콤보박스 세팅
        ReportCommon.libComSet(self, hostname, port, username, password)
        
        # js 콤보박스 세팅
        ReportCommon.jsComSet(self, hostname, port, username, password)
        
        # crf 콤보박스 세팅
        ReportCommon.crfComSet(self, hostname, port, username, password)  
        
        # 톰캣 로그
        self.textEditLogger.setReadOnly(True)
        self.setup_log_reader(hostname, port, username, password, log_file_path)
        

        '''''''''''''''''UI 초기세팅'''''''''''''''''
        
        
        #jar 업로드 
        self.libSearch.clicked.connect(self.fileSearch)
        self.libUpload.clicked.connect(self.upload_file_to_server)
        
        # 톰캣 start
        self.server_start.clicked.connect(self.on_button_click)
        
        # 톰캣 shutdown
        self.server_shutdown.clicked.connect(self.on_button_click1)
        
        # 버전 변경
        self.verSet.clicked.connect(self.verComSet)
        
        # 뷰어 실행
        self.ViewRun.clicked.connect(self.view)

    #여기에 함수 설정 
    #여러개의 파일의 경로를 가져 오기 위한 파일 서치
    def fileSearch(self):
        result = ReportCommon.get_file_paths()
        for file_path in result:
            file_paths_str = "\n".join(result)  # 파일 경로들을 줄 바꿈 문자로 연결하여 하나의 문자열로 변환
            self.textEdit.setText(file_paths_str)

    def upload_file_to_server(self):
        local_file_paths = self.textEdit.toPlainText()
        local_file_paths_list = local_file_paths.split('\n')
        ver = ReportCommon.extract_number_before_jar(local_file_paths_list)
        remote_dir="/app/tomcat/files/lib/"
        print("ver====" + ver)
        remote_dir = remote_dir + str(ver) +"/"
        ReportCommon.upload_files_to_server(hostname, port, username, password, local_file_paths_list, remote_dir, ver)

    def on_button_click(self):
        ServerCommon.tomcatAct.tomcatAct(hostname, port, username, password,"start")
        self.log_reader_thread = ServerCommon.LogReaderThread()
        self.log_reader_thread.setup(hostname, port, username, password, log_file_path)
        self.log_reader_thread.tomStartup_signal.connect(self.tomOn)
        self.log_reader_thread.start()

    def on_button_click1(self):
        ServerCommon.tomcatAct.tomcatAct(hostname, port, username, password,"shutdown")
        self.log_reader_thread = ServerCommon.LogReaderThread()
        self.log_reader_thread.setup(hostname, port, username, password, log_file_path)
        self.log_reader_thread.tomShutdown_signal.connect(self.tomDown)
        self.log_reader_thread.start()
    
    def tomOn(self):
        self.server_start.setEnabled(False)
        self.server_shutdown.setEnabled(True)
        self.verSet.setEnabled(True)
        self.tomStat.setText('<p align="left"><span style=" font-size:12pt; color:black;">started </span><span style=" font-size:12pt; color:green;">●</span></p>')
    def tomDown(self):
        self.server_start.setEnabled(True)
        self.server_shutdown.setEnabled(False)
        self.verSet.setEnabled(False)
        self.tomStat.setText('<p align="left"><span style=" font-size:12pt; color:black;">stop </span><span style=" font-size:12pt; color:red;">●</span></p>')
    def tomIng(self, str):
        self.tomStat.setText('<p align="left"><span style=" font-size:12pt; color:black;">'+str+'</span></p>')
        
    def view(self):
        ReportCommon.reportView(self)
        
    def verComSet(self):
        if ReportCommon.versionCheck(hostname, port, username, password, reportPath) != self.libCombo.currentText():
            self.setEnabled(False)
            ReportCommon.versionChange(hostname, port, username, password, self.libCombo.currentText())
            self.log_reader_thread = ServerCommon.LogReaderThread()
            self.log_reader_thread.setup(hostname, port, username, password, log_file_path)
            self.log_reader_thread.success_signal.connect(self.enable_ui)
            self.log_reader_thread.start()
        else:
             QMessageBox.about(self,'현재버전과 같음')
        
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

