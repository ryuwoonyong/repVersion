# SSH 클라이언트 객체 생성
import paramiko, time, webbrowser, re, os
import tkinter as tk
import urllib.parse
# 쉘 실행
import subprocess
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

def jsComSet(self, hostname, port, username, password, new_ver=None):
    self.jsCombo.clear()
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
    if new_ver:
        self.jsCombo.setCurrentText(new_ver)
def crfComSet(self, hostname, port, username, password, new_ver=None):
    self.crfCombo.clear()
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
    if new_ver:
        print('>>>>>' + new_ver)
        self.crfCombo.setCurrentText(new_ver)

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
    
    encoded_dataVal=urllib.parse.quote(dataVal)
    param="?crfNm="+crfNm+"&jsVer="+jsVer+"&dataVal="+encoded_dataVal+"&dataType="+dataType
    # 기본 웹 브라우저를 사용하여 URL 열기(임시)
    webbrowser.open('http://10.0.2.24:8080/ClipReport5/report_repv.jsp'+param)

    # 특정 웹 브라우저 (크롬) 사용하여 URL 열기
    #webbrowser.get('chrome').open('http://10.0.2.178/ClipReport5/report.jsp')

    # 특정 웹 브라우저 (엣지) 사용하여 URL 열기
    #webbrowser.get('edge').open('http://10.0.2.178/ClipReport5/report.jsp')

def get_file_paths(type):
    if type == 'jar':
        title = "Open JAR files"
        file_extension_filter = [("JAR files", "*.jar")]
    elif type == 'crf':
        title = "Open report files"
        file_extension_filter = [("crf, crfe files", "*.crf *.crfe"), ("crf files", "*.crf"),("crfe files", "*.crfe")]
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    file_paths = filedialog.askopenfilenames(title=title, filetypes=file_extension_filter)
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
        sftp.stat(remote_dir)
        return "이미 존재함"
    except:
        # 원격 디렉토리가 존재하지 않으면 생성
        
        make_remote_dir(sftp, remote_dir)
        try:
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
            return "upload success !!"
        
        except paramiko.AuthenticationException:
            return "Authentication failed, please verify your credentials"
        except paramiko.SSHException as sshException:
            return f"Could not establish SSH connection: {sshException}"
        except Exception as e:
            return f"Exception in connecting to the server or uploading file: {e}"
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

def extract_number_before_jar(file_paths_str):
    uploadFileList=[]
    uploadFilePathList=[]
    version=""
    for file_path in file_paths_str:
        # 파일명만 추출
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)  # 파일 크기 (바이트 단위)
        if os.path.isfile(file_path) and file_path.endswith('.jar'):
            if file_size <= 20 * 1024 * 1024:
                uploadFileList.append(filename)
                uploadFilePathList.append(file_path)
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
                uploadFileList.append(filename + "<< 용량제한 제외")
        else:
            uploadFileList.append(filename + "<< jar 파일이 아님")
    message = "5.0."+version+" version\r\n"+'\r\n'.join(uploadFileList)
    return version, message, uploadFilePathList

def upload_File_Check_js(local_dir):
    uploadFileNameList=[]
    uploadFilePathList=[]
    version=""
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_file = os.path.join(root, file)
            filename = os.path.basename(local_file)
            # 파일 확장자가 .js인지 확인하고, 파일 크기가 20MB 이하인지 확인
            if local_file.endswith('.js'):
                file_size = os.path.getsize(local_file)  # 파일 크기 (바이트 단위)
                if file_size <= 20 * 1024 * 1024:  # 20MB 이하인지 확인
                    if filename != 'OOFDocument.js':
                        print('local_file >> ' + local_file)
                        uploadFileNameList.append(filename)
                        uploadFilePathList.append(local_file)
                        if filename == 'clipreport5.js':
                            # 읽어올 바이트 수 설정 (예: 1KB)
                            bytes_to_read = 1024
                            # 파일 내용 일부 읽기
                            with open(local_file, 'r', encoding='utf-8') as file:
                                js_content = file.read(bytes_to_read)
                            # 정규식 패턴 설정
                            pattern = r'var report_version="([\d.]+)";'
                            # 정규식 검색
                            match = re.search(pattern, js_content)
                            if match:
                                version = match.group(1).split('.')[2]
                                #print(f"report_version: {report_version}")  # Output: 5.0.263
                                #version = :
                            
    message=version+" version\r\n" + '\r\n'.join(uploadFileNameList)
    print(uploadFilePathList)
    return version, message, uploadFilePathList                  

def upload_File_Check_crf(file_paths_str):
    uploadFileList=[]
    uploadFilePathList=[]
    print('aaaaaaaaaaa')
    print(file_paths_str)
    print('aaaaaaaaaaa')
    for file_path in file_paths_str:
        # 파일명만 추출
        filename = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)  # 파일 크기 (바이트 단위)
        if os.path.isfile(file_path) and file_path.endswith('.crf'):
            if file_size <= 20 * 1024 * 1024:
                print('ffffffffffffffffffff')
                uploadFileList.append(filename)
                uploadFilePathList.append(file_path)
            else:
                print("용량이 너무큼")
                uploadFileList.append(filename + "<< 용량제한 제외")
        else:
            uploadFileList.append(filename + "<< crf 파일이 아님")
    message = '\r\n'.join(uploadFileList)
    return message, uploadFilePathList

def upload_files_to_server_crf(hostname, port, username, password, local_file_paths, remote_dir):

    # SSH 클라이언트 초기화
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port=port, username=username, password=password)
    sftp = ssh.open_sftp()
    print(local_file_paths)
    print('remote_dir>> ' + remote_dir)
    try:
        # 각 파일에 대해 업로드
        for local_file_path in local_file_paths:
            
            remote_file_path = os.path.join(remote_dir, os.path.basename(local_file_path))
            # 파일 업로드
            sftp.put(local_file_path, remote_file_path)
            print(f"File {local_file_path} uploaded to {remote_file_path} on {hostname}")
            
        # SFTP 클라이언트 종료
        sftp.close()
        return "upload success !!"
        
    except paramiko.AuthenticationException:
        return "Authentication failed, please verify your credentials"
    except paramiko.SSHException as sshException:
        return f"Could not establish SSH connection: {sshException}"
    except Exception as e:
        return f"Exception in connecting to the server or uploading file: {e}"
    finally:
        # SSH 연결 종료
        ssh.close()
        print("SSH connection closed")

def getRemoteDirectories(hostname, port, username, password, path):

    # SSH 클라이언트 초기화
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)
    sftp = ssh.open_sftp()

    resultArray = []

    # 디렉토리 목록 불러오기
    try:
        list = sftp.listdir(path)
        resultArray = [item for item in list]

    except FileNotFoundError:
        print(f"경로를 찾을 수 없습니다: {path}")
    except Exception as e:
        print(f"디렉토리 목록 불러오기 중 오류 발생: {str(e)}")

    # SSH 연결 종료
    sftp.close()
    ssh.close()

    return resultArray

def getRemoteFiles(hostname, port, username, password, path):
    fileArray = []

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)
    sftp = ssh.open_sftp()

    files = sftp.listdir(path)
    for file in files:
            fileArray.append(file)

    sftp.close()
    ssh.close()

    return fileArray

    
def updateEngine(hostname, port, username, password,lib_path, engine_path, engine_sh_path):
    eng_list = getRemoteDirectories(hostname, port, username, password, engine_path)
    lib_list = getRemoteDirectories(hostname, port, username, password, lib_path)
    
    # eng_list에서 각 항목의 "5.0." 글자 제거
    eng_list = [item[4:] for item in eng_list]

    # SSH 클라이언트 초기화
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)

    # 목록 비교하여 없는 lib/js 버전만 업로드 
    for item in eng_list:
        if item not in lib_list:
            stdin, stdout, stderr = ssh.exec_command(engine_sh_path+" "+item)
            stdout.readlines() 
            #print(f"업로드한 항목(*사용불가 무시): {item}")

    # SSH 연결 종료
    ssh.close()

def exportPDF(self):
    crfNm = self.crfCombo.currentText()
    jsVer = self.jsCombo.currentText()
    dataVal = self.dataVal.toPlainText()
    dataType = self.dataType.currentText()
    
    encoded_dataVal=urllib.parse.quote(dataVal)
    
    param="?crfNm="+crfNm+"&jsVer="+jsVer+"&dataVal="+encoded_dataVal+"&dataType="+dataType
    # 기본 웹 브라우저를 사용하여 URL 열기(임시)
    webbrowser.open('http://10.0.2.24:8080/ClipReport5/exportForPDF.jsp'+param)

    # 특정 웹 브라우저 (크롬) 사용하여 URL 열기
    #webbrowser.get('chrome').open('http://10.0.2.178/ClipReport5/report.jsp')

    # 특정 웹 브라우저 (엣지) 사용하여 URL 열기
    #webbrowser.get('edge').open('http://10.0.2.178/ClipReport5/report.jsp')

def compareView(version):
    param="?version="+version
    webbrowser.open('http://10.0.2.24:8080/ClipReport5/compare_repv.jsp'+param)

def upload_files(hostname, port, username, password, remote_lib_dir, remote_js_dir, version):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port, username, password)

    stdin, stdout, stderr = ssh.exec_command(f"cp -R {remote_lib_dir}{version}/* /app/tomcat/ClipReport5_{version}/WEB-INF/lib/")

    ssh.close()

def exec_cmd(hostname, port, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname, port, username, password)
        stdin, stdout, stderr = ssh.exec_command(command)

        # 명령어 실행 결과 출력
        print(stdout.read().decode())
        print(stderr.read().decode())
        
    except Exception as e:
        print(f"Exception in connecting to the server: {e}")
    finally:
        ssh.close()