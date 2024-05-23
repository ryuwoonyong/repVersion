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
    stdin, stdout, stderr = ssh.exec_command("ls -lart")
    

    # 명령의 출력 결과 읽기
    print("STDOUT:")
    for line in stdout.readlines():
        print(line.strip())

    print("STDERR:")
    for line in stderr.readlines():
        print(line.strip())

finally:
    # SSH 연결 종료
    ssh.close()