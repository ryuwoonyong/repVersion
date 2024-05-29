import paramiko
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from requests.exceptions import ConnectionError, HTTPError

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