import paramiko
import requests
import xml.etree.ElementTree as ET
from PyQt5.QtCore import QThread, pyqtSignal
from requests.exceptions import ConnectionError, HTTPError
import os

class LogReaderThread(QThread):
    new_log_signal = pyqtSignal(str)
    success_signal = pyqtSignal()
    tomStartup_signal = pyqtSignal()
    tomShutdown_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True

    def setup(self, hostname, port, username, password, log_file_path):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.log_file_path = log_file_path

    def run(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.hostname, port=self.port, username=self.username, password=self.password)

        command = f'tail -f {self.log_file_path}'
        stdin, stdout, stderr = ssh.exec_command(command)

        while self.running:
            line = stdout.readline()
            if line:
                self.new_log_signal.emit(line.replace("\n",""))
                if 'org.apache.catalina.core.StandardContext.reload' in line:
                    self.success_signal.emit()
                if '[main] org.apache.catalina.startup.Catalina.start Server startup in' in line:
                    self.tomStartup_signal.emit()
                if '[main] org.apache.coyote.AbstractProtocol.destroy 프로토콜 핸들러 ["http-nio-8080"]을(를) 소멸시킵니다.' in line:
                    self.tomShutdown_signal.emit()
                

        ssh.close()

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

class tomcatAct:
    def tomcatAct(hostname, port, username, password, act):
    # SSH 클라이언트 초기화
        ssh = paramiko.SSHClient()
    # 호스트 키 자동 추가 정책 설정
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
        try:
            # SSH 연결 시도
            ssh.connect(hostname, port, username, password)
        
            # 원격 명령 실행 act 여부에 따라 start 또는 shutdown
            command =""
            if act == "start" :
                command = "export JRE_HOME=/usr/lib/java/openjdk-8u342-b07; /app/tomcat/tomcat/bin/startup.sh"
            if act == "shutdown" :
                command = "export JRE_HOME=/usr/lib/java/openjdk-8u342-b07; /app/tomcat/tomcat/bin/shutdown.sh"

            stdin, stdout, stderr = ssh.exec_command(command)
        
            # 명령의 출력 결과 읽기
            print("STDOUT:")
            for line in stdout.readlines():
                print(line.strip())
        
            print("STDERR:")
            for line in stderr.readlines():
                print(line.strip())
    
        except paramiko.AuthenticationException:
            print("Authentication failed, please verify your credentials")
        except paramiko.SSHException as sshException:
            print(f"Could not establish SSH connection: {sshException}")
        except Exception as e:
            print(f"Exception in connecting to the server: {e}")
        finally:
            # SSH 연결 종료
            ssh.close()
            print("SSH connection closed")

class AliveCheck:
    def check_vm_connection(hostname, port, username, password):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
        try:
            ssh.connect(hostname, port, username, password)
            ssh.close()
            return True
        except paramiko.AuthenticationException:
            print("Authentication failed, please verify your credentials")
            return False
        except paramiko.SSHException as sshException:
            print(f"Could not establish SSH connection: {sshException}")
            return False
        except Exception as e:
            print(f"Exception in connecting to the server: {e}")
            return False
        finally:
            # SSH 연결 종료
            ssh.close()
            print("SSH connection closed")
        
    def check_tom_connection (URL):
        try:
            response = requests.get(URL)
            response.raise_for_status()  # HTTPError가 발생하면 예외 처리
            return True
        except ConnectionError:
            #print(f"Failed to connect to {url}. Please check the server.")
            return False
        except HTTPError as http_err:
            #print(f"HTTP error occurred: {http_err}")
            return False
        except Exception as err:
            return False
        
def create_context(hostname, port, username, password, version):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # SSH 연결 시도
        ssh.connect(hostname, port, username, password)
        
        # 루트 요소 생성
        context = ET.Element('Context')
        context.set('path', '/ClipReport5_' + version)
        context.set('docBase', '/app/tomcat/ClipReport5_' + version)
        context.set('reloadable', 'true')

        # 트리 구조 생성
        tree = ET.ElementTree(context)

        # 저장할 경로 설정
        save_path = '/app/tomcat/tomcat/conf/Catalina/localhost'
        file_name = 'ClipReport5_' + version + '.xml'
        full_path = save_path + "/" + file_name

        # XML 파일을 로컬에 저장
        local_temp_file = f'/temp/{file_name}'
        with open(local_temp_file, 'wb') as file:
            file.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            tree.write(file, encoding='utf-8', xml_declaration=False)
        
        # 원격 서버에 디렉토리 생성 명령 실행
        ssh.exec_command(f'mkdir -p {save_path}')
        
        # SFTP 세션을 시작하고 파일을 원격 서버로 전송
        sftp = ssh.open_sftp()
        sftp.put(local_temp_file, full_path)
        sftp.close()
        
        # 로컬 임시 파일 삭제
        os.remove(local_temp_file)

        print(f"{full_path} 파일이 생성되었습니다.")

    except Exception as e:
        print(f"Exception in connecting to the server: {e}")
    finally:
        ssh.close()