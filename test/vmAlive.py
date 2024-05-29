import paramiko

def check_vm_connection(hostname, port, username, password):
    """
    원격 서버에 SSH 연결이 가능한지 확인하는 함수
    """
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

# 테스트를 위한 예제 실행
if __name__ == "__main__":
    hostname = "10.0.2.21"
    port = 22
    username = "tomcat"
    password = "tomcat"
    
    if check_vm_connection(hostname, port, username, password):
        print("0")
    else:
        print("1")
    