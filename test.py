import requests

password_to_check = "MyP@ssw0rd123"

response = requests.post('http://localhost:5000/api/check', 
    json={'password': password_to_check})

print(response.json())