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

def libComSet(self, hostname, port, username, password, new_ver=None):
    self.libCombo.clear()
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
    if new_ver:
        self.libCombo.setCurrentText(new_ver)

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

def get_file_paths():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames()
    return list(file_paths)

def upload_files_to_server(hostname, port, username, password, local_file_paths, remote_dir, ver=None):
    # SSH 클라이언트 초기화
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # SSH 연결 시도
        ssh.connect(hostname, port=port, username=username, password=password)
        
        # SFTP 클라이언트 초기화
        sftp = ssh.open_sftp()
        
        # 원격 디렉토리가 존재하지 않으면 생성
        try:
            sftp.stat(remote_dir)
        except FileNotFoundError:
            make_remote_dir(sftp, remote_dir)
        
        # 각 파일에 대해 업로드
        for local_file_path in local_file_paths:
            if remote_dir is None:
                temporary_directory = '/tmp/'  # 임시 디렉토리 경로
                remote_file_path = os.path.join(temporary_directory, os.path.basename(local_file_path))
            elif ver is not None:
                # remote_file_path에 ver 추가
                remote_file_path = os.path.join(remote_dir, os.path.basename(local_file_path))
            else:
                raise ValueError("If 'remote_dir' is provided, 'ver' must also be provided.")
            
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
    if remote_directory == '/':
        sftp.chdir('/')
        return
    if remote_directory == '':
        return
    try:
        sftp.chdir(remote_directory)  # Test if remote directory exists
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        make_remote_dir(sftp, dirname)  # Create parent directories
        sftp.mkdir(basename)  # Create remote directory
        sftp.chdir(basename)
        return True

def extract_number_before_jar(file_paths_str, self):
    uploadFileList=[]
    uploadFilePathList=[]
    version=""
    for file_path in file_paths_str:
        # 파일명만 추출
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)  # 파일 크기 (바이트 단위)
        if os.path.isfile(file_path) and file_path.endswith('.jar'):
            uploadFileList.append(filename)
            uploadFilePathList.append(file_path)
            if file_size <= 20 * 1024 * 1024:
                # 'ClipReport5.0.'가 파일명에 있는지 확인
                if 'ClipReport5.0.' in filename:
                    # '.'으로 분할하여 마지막에서 두 번째 요소 추출
                    parts = filename.split('.')
                    if len(parts) > 1:
                        version_number = parts[-2]
                        print(f"Found version number: {version_number} in {filename}")
                        version=str(version_number)
            else:
                print("용량이 너무큼")
                uploadFileList.append(filename + "- 용량제한 제외")
        else:
            uploadFileList.append(filename + "- jar 파일이 아님")
    message = "5.0."+version+" version\r\n"+',\r\n'.join(uploadFileList)
    return version, message, uploadFilePathList