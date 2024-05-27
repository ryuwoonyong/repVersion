import paramiko
from PyQt5.QtCore import QThread, pyqtSignal

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