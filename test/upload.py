import paramiko
import os

# SFTP 서버 정보
hostname = '10.0.2.21'  # SFTP 서버 주소
port = 22  # SFTP 서버 포트 (기본값: 22)
username = 'tomcat'  # SFTP 서버 사용자 이름
password = 'tomcat'  # SFTP 서버 비밀번호

# 업로드할 파일 경로
local_file_path = 'D://ClipReport5/259/5.0.259/5.0.259/ClipReport5/WEB-INF/lib/ClipReport5.0.259.ja_'
remote_file_path = '/app/tomcat/files/ClipReport5.0.259.ja_'  # 원격 서버에 저장될 파일 경로

# SFTP 연결 설정
try:
    # Transport 객체 생성 및 연결
    transport = paramiko.Transport((hostname, port))
    transport.connect(username=username, password=password)

    # SFTP 클라이언트 생성
    sftp = paramiko.SFTPClient.from_transport(transport)

    # 파일 업로드
    sftp.put(local_file_path, remote_file_path)
    print(f"File '{local_file_path}' successfully uploaded to '{remote_file_path}'")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # SFTP 및 Transport 연결 종료
    sftp.close()
    transport.close()