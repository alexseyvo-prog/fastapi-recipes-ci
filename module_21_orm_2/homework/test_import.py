import requests

url = 'http://127.0.0.1:5000/api/students/import'

with open('students.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post(url, files=files)
    print(response.status_code)
    print(response.json())