# SSH 클라이언트 객체 생성
import paramiko, time, webbrowser
import tkinter as tk
import re
import os
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
            self.libCombo.addItem(str(ver))
    finally:
        # SSH 연결 종료
        ssh.close()
def jsComSet(self, hostname, port, username, password):
    try:
        sel_en_ver=[]
        ssh.connect(hostname, port, username, password)
        stdin, stdout, stderr = ssh.exec_command("ls -r /app/tomcat/files/js/")
        for line in stdout.readlines():
            sel_en_ver.append(line.replace("\n",""))
        for line in stderr.readlines():
            print(line.strip())
        sel_en_verint = [int (i) for i in sel_en_ver]
        sel_en_verint.sort(reverse=True)
        for ver in sel_en_verint:
            self.jsCombo.addItem(str(ver))
    finally:
        # SSH 연결 종료
        ssh.close()
def crfComSet(self, hostname, port, username, password):
    try:
        sel_en_ver=[]
        ssh.connect(hostname, port, username, password)
        stdin, stdout, stderr = ssh.exec_command("ls -r /app/tomcat/ClipReport5/WEB-INF/clipreport5/crf/")
        for line in stdout.readlines():
            sel_en_ver.append(line.replace("\n",""))
        for line in stderr.readlines():
            print(line.strip())
        for ver in sel_en_ver:
            self.crfCombo.addItem(str(ver))
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
    crfNm = self.crfCombo.currentText()
    jsVer = self.jsCombo.currentText()
    dataVal = self.dataVal.toPlainText()
    dataType = self.dataType.currentText()
    param="?crfNm="+crfNm+"&jsVer="+jsVer+"&dataVal="+dataVal+"&dataType="+dataType
    # 기본 웹 브라우저를 사용하여 URL 열기(임시)
    webbrowser.open('http://10.0.2.21:8080/ClipReport5/report_repv.jsp'+param)

    # 특정 웹 브라우저 (크롬) 사용하여 URL 열기
    #webbrowser.get('chrome').open('http://10.0.2.21/ClipReport5/report.jsp')

    # 특정 웹 브라우저 (엣지) 사용하여 URL 열기
    #webbrowser.get('edge').open('http://10.0.2.21/ClipReport5/report.jsp')

def get_file_path():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename()
    return file_path

def upload_file_to_server(hostname, port, username, password, local_file_path, remote_file_path, ver):
    # SSH 클라이언트 초기화
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # SSH 연결 시도
        ssh.connect(hostname, port=port, username=username, password=password)
        
        # SFTP 클라이언트 초기화
        sftp = ssh.open_sftp()

        if remote_file_path is None:
            temporary_directory = '/tmp/'  # 임시 디렉토리 경로
            remote_file_path = os.path.join(temporary_directory, os.path.basename(local_file_path))
        elif ver is not None:
            # remote_file_path에 ver 추가
            remote_file_path = remote_file_path + ver + "/ClipReport5.0." + ver + ".jar"
        else:
            raise ValueError("If 'remote_file_path' is provided, 'ver' must also be provided.")
        
        # 원격 디렉토리 경로 생성
        remote_dir = os.path.dirname(remote_file_path)
        
        # 원격 디렉토리가 존재하지 않으면 생성
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            make_remote_dir(sftp, remote_dir)
        
        # 파일 업로드
        sftp.put(local_file_path, remote_file_path)
        print(f"File {local_file_path} uploaded to {remote_file_path} on {hostname}")
        
        # SFTP 클라이언트 종료
        sftp.close()
    
    except paramiko.AuthenticationException:
        print("Authentication failed, please verify your credentials")
    except paramiko.SSHException as sshException:
        print(f"Could not establish SSH connection: {sshException}")
    except Exception as e:
        print(f"Exception in connecting to the server or uploading file: {e}")
    finally:
        # SSH 연결 종료
        ssh.close()
        print("SSH connection closed")

def make_remote_dir(sftp, remote_directory):
    """재귀적으로 디렉토리를 생성하는 함수"""
    dirs = remote_directory.split('/')
    path = ''
    for directory in dirs:
        if directory:
            path = f"{path}/{directory}"
            try:
                sftp.stat(path)
            except FileNotFoundError:
                sftp.mkdir(path)

def extract_last_four_to_seven_chars(file_path):
    # 파일명 추출
    file_name = os.path.basename(file_path)
    # 파일명에서 마지막 4~7자리 추출
    last_four_to_seven_chars = file_name[-7:-4]
    return last_four_to_seven_chars
