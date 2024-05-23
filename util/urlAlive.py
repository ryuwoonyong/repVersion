import requests
from requests.exceptions import ConnectionError, HTTPError

url = 'http://10.0.2.21:8080/ClipReport5/report.jsp'

try:
    response = requests.get(url)
    response.raise_for_status()  # HTTPError가 발생하면 예외 처리
    print("Started")
except ConnectionError:
    #print(f"Failed to connect to {url}. Please check the server.")
    print(f"Connection Error")
except HTTPError as http_err:
    #print(f"HTTP error occurred: {http_err}")
    print(f"HTTP Error")
except Exception as err:
    print(f"An error occurred: {err}")