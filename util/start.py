import paramiko

# SSH 클라이언트 객체 생성
ssh = paramiko.SSHClient()

# 자동으로 서버의 호스트 키를 추가
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# SSH 연결 설정
hostname = "10.0.2.21"
port = 22
username = "tomcat"
password = "tomcat"

try:
    ssh.connect(hostname, port, username, password)

    # 원격 명령 실행
    command = "export JRE_HOME=/usr/lib/java/openjdk-8u342-b07; /app/tomcat/tomcat/bin/startup.sh"
    stdin, stdout, stderr = ssh.exec_command(command)    
    #stdin, stdout, stderr = ssh.exec_command("ls -alrt")
    #stdin, stdout, stderr = ssh.exec_command("./startup.sh")
    
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