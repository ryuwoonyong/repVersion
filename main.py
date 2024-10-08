import os, sys, paramiko, subprocess, logging, time
from os import environ

from util import ReportCommon
from util import ServerCommon

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

# SSH 연결 설정
hostname = "10.0.2.24"
port = 22
username = "tomcat"
password = "tomcat"

#경로설정
reportPath = "/app/tomcat/ClipReport5"
log_file_path="/app/tomcat/tomcat/logs/catalina.out"
verFilePath="/app/tomcat/files"
remote_lib_dir="/app/tomcat/files/lib/"
remote_js_dir="/app/tomcat/files/web/js/"
remote_crf_dir="/app/tomcat/ClipReport5/WEB-INF/clipreport5/crf/"
engine_path = "/app/tomcat/files/mount/onedrive/General/제품릴리즈/(클립리포트)(클립이폼)5.0/서버엔진"
engine_sh_path="/app/tomcat/files/mount/getEng.sh"
conetext_path = "/app/tomcat/tomcat/conf/Catalina/localhost"

#하기 함수로 vm및 was 커넥션 체크
#AliveCheck.check_vm_connection(hostname, port, username, password)
#AliveCheck.check_tom_connection(URL)


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))    
    return os.path.join(base_path, relative_path)

form = resource_path('./templates/app.ui')
form_class = uic.loadUiType(form)[0]

# 높은 해상도에서도 안깨지게
def suppress_qt_warnings():
    environ["QT_DEVICE_PIXEL_RATIO"]="0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"]="1"
    environ["QT_SCREEN_SCALE_FACTORS"]="1"
    environ["QT_SCALE_FACTOR"]="1"

class compareDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        form = resource_path('./templates/multi.ui')
        uic.loadUi(form, self)
        
        '''''''''''''''''UI 초기세팅'''''''''''''''''

        # 다이얼로그 내 버튼 클릭
        self.addContextBtn.clicked.connect(self.addContextpath)

        '''''''''''''''''UI 초기세팅'''''''''''''''''

    # 여기에 함수 설정 
    
    def addContextpath(self):
        #QMessageBox.information(self, '대기', '대기')
        wait_msg_box = QMessageBox(self)
        wait_msg_box.setWindowTitle('대기')
        wait_msg_box.setText('대기대기대기')
        wait_msg_box.show()
        
        versionInfo = self.versionEdit.toPlainText()  
        remote_lib_list = ReportCommon.getRemoteDirectories(hostname, port, username, password, remote_lib_dir)
        
        # resultVersion 초기화
        resultVersion = []
        
        values = versionInfo.split(',')
        for value in values:
            version = value.strip()
            if version in remote_lib_list:
                try:
                    resultVersion.append(version)

                    # Context 추가 
                    ServerCommon.create_context(hostname, port, username, password, version)
                
                    # Directory 생성 
                    ReportCommon.exec_cmd(hostname, port, username, password, f"rsync -av --exclude 'js' --exclude 'WEB-INF/lib/*' {reportPath}/* {reportPath}_{version}")
                    ReportCommon.exec_cmd(hostname, port, username, password, f"cp {remote_lib_dir}/{version}/* {reportPath}_{version}/WEB-INF/lib")

                except Exception as e:
                    print(f'Error processing version {version}: {str(e)}') 
            else:
                print(f'Version {version} not found in remote library directory, skipping context creation.')
        
        # 완료 메시지 표시 후 다이얼로그 닫기
        wait_msg_box.close()
        QMessageBox.information(self, '작업 완료', '작업이 완료되었습니다.')
        self.accept()

        #view
        ReportCommon.compareView(','.join(resultVersion))
            
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super( ).__init__( )
        self.setupUi(self)
        
        '''''''''''''''''UI 초기세팅'''''''''''''''''
        #self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setWindowTitle("Report Version TEST")
        #self.setFixedWidth(680)
        
        # VM 서버 확인
        
        # 톰캣 확인
        if(ServerCommon.AliveCheck.check_tom_connection("http://"+hostname+":8080/ClipReport5/tomCheck.jsp")):
            self.tomOn()
        else:
            self.tomDown()
        
        # 리포트 버전 확인
        self.libVer.setText("엔진 버전 - 5.0."+ReportCommon.versionCheck(hostname, port, username, password, reportPath))
        #self.jsVer.setText("뷰어 버전 - 5.0."+self.jsCombo.currentText())
        
        # 리포트 버전 갱신
        ReportCommon.updateEngine(hostname, port, username, password, remote_lib_dir, engine_path, engine_sh_path)

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
        
        
        # jar 업로드 
        self.libSearch.clicked.connect(self.fileSearch_lib)
        self.libUpload.clicked.connect(self.upload_file_to_server_lib)
        
        # js 업로드
        self.jsSearch.clicked.connect(self.fileSearch_js)
        self.jsUpload.clicked.connect(self.upload_file_to_server_js)
        
        # crf 업로드
        self.crfSearch.clicked.connect(self.fileSearch_crf)
        self.crfUpload.clicked.connect(self.upload_file_to_server_crf)
        
        # 톰캣 start
        self.server_start.clicked.connect(self.on_button_click)
        
        # 톰캣 shutdown
        self.server_shutdown.clicked.connect(self.on_button_click1)
        
        # 버전 변경
        self.verSet.clicked.connect(self.verComSet)
        
        # 뷰어 실행
        self.ViewRun.clicked.connect(self.view)
        
        # PDF 다운로드
        self.PDFRun.clicked.connect(self.exportPDF)
        
        # 데이터타입
        self.dataType.currentTextChanged.connect(self.dataType_select)
        
        # 뷰어버전
        self.jsCombo.currentTextChanged.connect(self.viewerVerSet)
        
        # 로그 새창 보기
        self.log_btn.clicked.connect(self.logNewWin)

        # 버튼 클릭 시 다이얼로그 띄우기
        self.multi.clicked.connect(self.openCompareDialog) 
        self.multiViewRun.clicked.connect(self.openCompareView) 

    #여기에 함수 설정 
    
    # ui 로드된 후 이벤트
    def showEvent(self, event):
        super().showEvent(event)
        self.jsVer.setText("뷰어 버전 - 5.0."+self.jsCombo.currentText())
        
    #여러개의 파일의 경로를 가져 오기 위한 파일 서치
    def fileSearch_lib(self):
        result = ReportCommon.get_file_paths('jar')
        for file_path in result:
            file_paths_str = "\n".join(result)  # 파일 경로들을 줄 바꿈 문자로 연결하여 하나의 문자열로 변환
            self.libUploadPath.setText(file_paths_str)

    def upload_file_to_server_lib(self):
        if self.libUploadPath.toPlainText() != "":
            local_file_paths = self.libUploadPath.toPlainText()
            local_file_paths_list = local_file_paths.split('\n')
            if len(local_file_paths_list) > 1:
                #버전 추출 및 파일 체크
                ver, message, uploadFilePathList = ReportCommon.extract_number_before_jar(local_file_paths_list)
                QMessageBox.about(self,'QMessageBox',message)
                remote_dir = remote_lib_dir + ver +"/"
                QMessageBox.about(self,'QMessageBox',ReportCommon.upload_files_to_server(hostname, port, username, password, uploadFilePathList, remote_dir, ver))
                ReportCommon.libComSet(self, hostname, port, username, password, ver)
            else:
                QMessageBox.about(self,'QMessageBox','두개이상 선택')
        else:
            QMessageBox.about(self,'QMessageBox','찾기먼저')

    def fileSearch_js(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder:
            self.jsUploadPath.setText(f'{folder}')

    def upload_file_to_server_js(self):
        
        if self.jsUploadPath.toPlainText() != "":
            local_dir = self.jsUploadPath.toPlainText()
            ver, message, uploadFilePathList = ReportCommon.upload_File_Check_js(local_dir)
            #print(ReportCommon.upload_File_Check_js(local_dir))
            if len(uploadFilePathList) > 1:
                QMessageBox.about(self,'QMessageBox',message)
                remote_dir = remote_js_dir + ver + "/"
                QMessageBox.about(self,'QMessageBox',ReportCommon.upload_files_to_server(hostname, port, username, password, uploadFilePathList, remote_dir, ver))
                ReportCommon.jsComSet(self, hostname, port, username, password, ver)
        else:
            QMessageBox.about(self,'QMessageBox','찾기먼저')
    
    def fileSearch_crf(self):
        result = ReportCommon.get_file_paths('crf')
        for file_path in result:
            file_paths_str = "\n".join(result)  # 파일 경로들을 줄 바꿈 문자로 연결하여 하나의 문자열로 변환
            self.crfUploadPath.setText(file_paths_str)
    def upload_file_to_server_crf(self):
            
        if self.crfUploadPath.toPlainText() != "":
            local_file_paths = self.crfUploadPath.toPlainText()
            local_file_paths_list = local_file_paths.split('\n')
            message, uploadFilePathList = ReportCommon.upload_File_Check_crf(local_file_paths_list)
            if len(uploadFilePathList) > 0:
                QMessageBox.about(self,'QMessageBox',message)
                remote_dir = remote_crf_dir
                QMessageBox.about(self,'QMessageBox',ReportCommon.upload_files_to_server_crf(hostname, port, username, password, uploadFilePathList, remote_dir))
                ReportCommon.crfComSet(self, hostname, port, username, password, uploadFilePathList[0].split('/')[-1])
        else:
            QMessageBox.about(self,'QMessageBox','찾기먼저')       
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
    def exportPDF(self):
        ReportCommon.exportPDF(self)
        # QMessageBox.about(self,'QMessageBox','아 귀찮;;')       
    def verComSet(self):
        if ReportCommon.versionCheck(hostname, port, username, password, reportPath) != self.libCombo.currentText():
            self.setEnabled(False)
            ReportCommon.versionChange(hostname, port, username, password, self.libCombo.currentText())
            self.log_reader_thread = ServerCommon.LogReaderThread()
            self.log_reader_thread.setup(hostname, port, username, password, log_file_path)
            self.log_reader_thread.success_signal.connect(self.enable_ui)
            self.log_reader_thread.start()
        else:
            QMessageBox.about(self,'QMessageBox','현재버전과 같음')
    
    def dataType_select(self):
        if self.dataType.currentText() == 'CSV':
            QMessageBox.about(self,'QMessageBox','CSV아직안댐')
    def viewerVerSet(self):
        self.jsVer.setText("뷰어 버전 - 5.0."+self.jsCombo.currentText())
                   
    def enable_ui(self):
        self.setEnabled(True)
        self.libVer.setText("엔진 버전 - 5.0."+ReportCommon.versionCheck(hostname, port, username, password, reportPath))
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
    def logNewWin(self):
        QMessageBox.about(self,'QMessageBox','이것도 귀찮;')

    def openCompareDialog(self):
        self.compareDialog = compareDialog(self)
        self.compareDialog.exec_()

    def openCompareView(self):
        file_names = ReportCommon.getRemoteFiles(hostname, port, username, password, conetext_path)

        # 문자열 제거할 패턴들
        patterns_to_remove = ["ClipReport5", '_', ".xml"]
        # 파일 이름에서 패턴 제거
        cleaned_file_names = []
        for file_name in file_names:
            cleaned_name = file_name
            for pattern in patterns_to_remove:
                cleaned_name = cleaned_name.replace(pattern, '')
            cleaned_file_names.append(cleaned_name)

        ReportCommon.compareView(','.join(cleaned_file_names))
       

    
if __name__ == '__main__':
    suppress_qt_warnings()
    app = QApplication(sys.argv)
    myWindow = WindowClass( )
    myWindow.show( )
    app.exec_( )





# dialog 버튼 클릭 
#def add_button_click(self):
 #   QMessageBox.information(self, 'Info', 'Add button clicked!')
    
  #  # version 에 versionEdit Value 값 추가
   # version = self.versionEdit.text()
    
    # context Path 추가 
    #ServerCommon.create_context(hostname, port, username, password, version)

    # js, lib 업로드 
    #ReportCommon.upload_files(hostname, port, username, password, remote_lib_dir, remote_js_dir, version)