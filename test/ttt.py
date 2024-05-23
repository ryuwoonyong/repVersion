import os
import subprocess

# JAVA_HOME 경로 설정 (본인의 설치 경로로 변경)
#java_home_path = "C:\\Program Files\\Java\\jdk-<version>"  # Windows 예제
# java_home_path = "/Library/Java/JavaVirtualMachines/jdk-<version>/Contents/Home"  # macOS 예제
java_home_path = "/usr/lib/jvm/java-<version>"  # Linux 예제

# 환경 변수 설정
os.environ["JAVA_HOME"] = java_home_path
os.environ["PATH"] = java_home_path + "\\bin;" + os.environ["PATH"]  # Windows
# os.environ["PATH"] = java_home_path + "/bin:" + os.environ["PATH"]  # macOS/Linux

# Java 프로그램 실행
result = subprocess.run(["java", "-version"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)