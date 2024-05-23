from flask import Flask, request, redirect, url_for, render_template
import paramiko
import os

app = Flask(__name__)

# SFTP 서버 정보
hostname = '10.0.2.21'  # SFTP 서버 주소
port = 22  # SFTP 서버 포트 (기본값: 22)
username = 'tomcat'  # SFTP 서버 사용자 이름
password = 'tomcat'  # SFTP 서버 비밀번호

# 업로드할 파일 경로
remote_path = '/app/tomcat/files'  # 원격 서버에 저장될 파일 경로


@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    local_file_path = os.path.join('uploads', file.filename)
    file.save(local_file_path)

    try:
        # SFTP 연결 설정
        transport = paramiko.Transport((hostname, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        
        remote_file_path = remote_path + file.filename
        sftp.put(local_file_path, remote_file_path)
        sftp.close()
        transport.close()
        
        return f"File '{file.filename}' successfully uploaded to '{remote_file_path}'"
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == '__main__':
    app.run(debug=True)